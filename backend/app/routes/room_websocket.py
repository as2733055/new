"""Room WebSocket handling with socket.io-like functionality"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
import json
import uuid
import jwt
from typing import Dict, List, Set, Optional
from datetime import datetime
from pydantic import BaseModel
from ..routes.users import SECRET_KEY, ALGORITHM
import asyncio

router = APIRouter(prefix="/room-ws", tags=["room-websocket"])

# Pydantic models
class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max_members: int = 100

class RoomResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str
    user_count: int = 0
    max_members: int = 100

# Room storage (persistent)
rooms_storage: Dict[str, dict] = {}

# Room connection manager
class RoomConnectionManager:
    def __init__(self):
        # Structure: {room_id: {user_id: {websocket, username, joined_at}}}
        self.active_rooms: Dict[str, Dict[str, dict]] = {}
        self.user_rooms: Dict[str, List[str]] = {}  # user_id -> list of room_ids
        self.room_messages: Dict[str, List[dict]] = {}  # room_id -> list of messages
    
    async def join_room(self, room_id: str, user_id: str, username: str, websocket: WebSocket):
        """User joins a room"""
        await websocket.accept()
        
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = {}
            self.room_messages[room_id] = []
        
        self.active_rooms[room_id][user_id] = {
            "websocket": websocket,
            "username": username,
            "joined_at": datetime.utcnow().isoformat(),
            "user_id": user_id
        }
        
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = []
        if room_id not in self.user_rooms[user_id]:
            self.user_rooms[user_id].append(room_id)
        
        # Notify others
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "users_count": len(self.active_rooms[room_id]),
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    async def leave_room(self, room_id: str, user_id: str):
        """User leaves a room"""
        if room_id in self.active_rooms and user_id in self.active_rooms[room_id]:
            username = self.active_rooms[room_id][user_id]["username"]
            del self.active_rooms[room_id][user_id]
            
            # Notify others
            await self.broadcast_to_room(room_id, {
                "type": "user_left",
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "users_count": len(self.active_rooms[room_id]),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Clean up empty rooms
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        
        if user_id in self.user_rooms and room_id in self.user_rooms[user_id]:
            self.user_rooms[user_id].remove(room_id)
    
    async def send_message(self, room_id: str, user_id: str, username: str, message: str, encrypted_content: str = None):
        """Send message to room"""
        msg_obj = {
            "type": "message",
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "content": message,
            "encrypted_content": encrypted_content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if room_id in self.room_messages:
            self.room_messages[room_id].append(msg_obj)
            # Keep last 100 messages per room
            if len(self.room_messages[room_id]) > 100:
                self.room_messages[room_id] = self.room_messages[room_id][-100:]
        
        await self.broadcast_to_room(room_id, msg_obj)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in room"""
        if room_id not in self.active_rooms:
            return
        
        disconnected = []
        for user_id, user_data in self.active_rooms[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await user_data["websocket"].send_json(message)
            except Exception as e:
                print(f"Error broadcasting to user {user_id}: {e}")
                disconnected.append(user_id)
        
        # Remove disconnected users
        for user_id in disconnected:
            await self.leave_room(room_id, user_id)
    
    def get_room_info(self, room_id: str) -> dict:
        """Get room information"""
        if room_id not in self.active_rooms:
            return None
        
        users = [
            {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "joined_at": user_data["joined_at"]
            }
            for user_data in self.active_rooms[room_id].values()
        ]
        
        return {
            "room_id": room_id,
            "users_count": len(users),
            "users": users,
            "messages": len(self.room_messages.get(room_id, []))
        }
    
    def get_room_history(self, room_id: str, limit: int = 50) -> List[dict]:
        """Get message history for room"""
        if room_id not in self.room_messages:
            return []
        return self.room_messages[room_id][-limit:]
    
    def get_all_rooms(self) -> List[dict]:
        """Get all active rooms"""
        rooms_list = []
        
        # Add rooms from storage
        for room_id, room_data in rooms_storage.items():
            user_count = len(self.active_rooms.get(room_id, {}))
            rooms_list.append({
                "room_id": room_id,
                "id": room_id,
                "name": room_data.get("name", "Unnamed Room"),
                "description": room_data.get("description"),
                "created_at": room_data.get("created_at"),
                "users_count": user_count,
                "user_count": user_count,
                "max_members": room_data.get("max_members", 100)
            })
        
        # Add active rooms not in storage
        for room_id, users in self.active_rooms.items():
            if room_id not in rooms_storage:
                rooms_list.append({
                    "room_id": room_id,
                    "id": room_id,
                    "name": f"Room {room_id[:8]}",
                    "description": "Temporary room",
                    "created_at": datetime.utcnow().isoformat(),
                    "users_count": len(users),
                    "user_count": len(users),
                    "max_members": 100
                })
        
        return rooms_list


manager = RoomConnectionManager()


def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.InvalidTokenError:
        return None


@router.websocket("/chat/{room_id}/{token}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str, token: str):
    """WebSocket endpoint for room-based real-time messaging"""
    # Verify token
    user_id = verify_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    # Get username from token or use default
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username", f"User_{user_id[:8]}")
    except:
        username = f"User_{user_id[:8]}"
    
    # Join room
    await manager.join_room(room_id, user_id, username, websocket)
    
    # Send room history to new user
    history = manager.get_room_history(room_id)
    if history:
        await websocket.send_json({
            "type": "message_history",
            "room_id": room_id,
            "messages": history
        })
    
    # Send room info
    room_info = manager.get_room_info(room_id)
    if room_info:
        await websocket.send_json({
            "type": "room_info",
            "data": room_info
        })
    
    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            if msg_data.get("type") == "message":
                await manager.send_message(
                    room_id,
                    user_id,
                    username,
                    msg_data.get("content", ""),
                    msg_data.get("encrypted_content")
                )
            
            elif msg_data.get("type") == "typing":
                await manager.broadcast_to_room(room_id, {
                    "type": "user_typing",
                    "room_id": room_id,
                    "user_id": user_id,
                    "username": username
                }, exclude_user=user_id)
            
            elif msg_data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        await manager.leave_room(room_id, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.leave_room(room_id, user_id)


# REST endpoints for room management
@router.get("/rooms")
async def get_all_rooms():
    """Get all active rooms"""
    return {
        "rooms": manager.get_all_rooms()
    }


@router.get("/room/{room_id}/info")
async def get_room_info(room_id: str):
    """Get room information"""
    info = manager.get_room_info(room_id)
    if not info:
        return JSONResponse(status_code=404, content={"error": "Room not found"})
    return info


@router.get("/room/{room_id}/history")
async def get_room_history(room_id: str, limit: int = Query(50, le=100)):
    """Get message history for room"""
    history = manager.get_room_history(room_id, limit)
    return {
        "room_id": room_id,
        "messages": history,
        "count": len(history)
    }


# Room management endpoints
@router.post("/rooms", response_model=RoomResponse)
async def create_room(room: RoomCreate):
    """Create a new room"""
    room_id = str(uuid.uuid4())[:12]
    
    room_data = {
        "id": room_id,
        "name": room.name,
        "description": room.description,
        "created_at": datetime.utcnow().isoformat(),
        "max_members": room.max_members,
    }
    
    rooms_storage[room_id] = room_data
    
    return RoomResponse(
        id=room_id,
        name=room.name,
        description=room.description,
        created_at=room_data["created_at"],
        max_members=room.max_members
    )


@router.get("/rooms/list")
async def list_rooms():
    """List all rooms"""
    return {
        "rooms": manager.get_all_rooms()
    }


@router.get("/rooms/all")
async def list_all_rooms():
    """List all available rooms"""
    rooms = manager.get_all_rooms()
    return {
        "success": True,
        "data": {
            "rooms": rooms,
            "total": len(rooms)
        }
    }


@router.get("/room/{room_id}")
async def get_room(room_id: str):
    """Get room details"""
    if room_id not in rooms_storage:
        # Check if it's an active room
        if room_id in manager.active_rooms:
            return {
                "id": room_id,
                "name": f"Room {room_id[:8]}",
                "description": "Active room",
                "created_at": datetime.utcnow().isoformat(),
                "users_count": len(manager.active_rooms[room_id]),
                "max_members": 100
            }
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_data = rooms_storage[room_id]
    user_count = len(manager.active_rooms.get(room_id, {}))
    
    return {
        "id": room_id,
        "name": room_data["name"],
        "description": room_data.get("description"),
        "created_at": room_data["created_at"],
        "users_count": user_count,
        "max_members": room_data.get("max_members", 100),
        "users": [
            {
                "user_id": u["user_id"],
                "username": u["username"],
                "joined_at": u["joined_at"]
            }
            for u in manager.active_rooms.get(room_id, {}).values()
        ]
    }


@router.delete("/room/{room_id}")
async def delete_room(room_id: str):
    """Delete a room"""
    if room_id not in rooms_storage:
        raise HTTPException(status_code=404, detail="Room not found")
    
    del rooms_storage[room_id]
    
    return {
        "success": True,
        "message": f"Room {room_id} deleted"
    }
