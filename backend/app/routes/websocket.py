"""WebSocket handling for real-time messaging"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
import asyncio
from typing import Dict, List, Set
import jwt
from ..routes.users import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/ws", tags=["websocket"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_status: Dict[str, bool] = {}  # user_id -> is_online
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Connect a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.user_status[user_id] = True
    
    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Disconnect a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.user_status[user_id] = False
    
    async def send_personal_message(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message: {e}")
    
    async def broadcast_to_users(self, user_ids: List[str], message: dict):
        """Broadcast message to multiple users"""
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)
    
    async def broadcast_all(self, message: dict):
        """Broadcast to all connected users"""
        for user_id in self.active_connections:
            await self.send_personal_message(user_id, message)
    
    def get_online_users(self) -> List[str]:
        """Get list of online users"""
        return list(self.active_connections.keys())


manager = ConnectionManager()


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


@router.websocket("/chat/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time messaging"""
    # Verify token
    user_id = verify_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                # Forward encrypted message to recipient
                recipient_id = data.get("recipient_id")
                encrypted_content = data.get("encrypted_content")
                
                await manager.send_personal_message(
                    recipient_id,
                    {
                        "type": "message",
                        "sender_id": user_id,
                        "encrypted_content": encrypted_content,
                        "timestamp": data.get("timestamp")
                    }
                )
            
            elif message_type == "typing":
                # Notify recipient that user is typing
                recipient_id = data.get("recipient_id")
                await manager.send_personal_message(
                    recipient_id,
                    {
                        "type": "typing",
                        "sender_id": user_id
                    }
                )
            
            elif message_type == "status":
                # Broadcast online status
                await manager.broadcast_all({
                    "type": "user_status",
                    "user_id": user_id,
                    "status": "online"
                })
            
            elif message_type == "online_users":
                # Send list of online users
                online_users = manager.get_online_users()
                await websocket.send_json({
                    "type": "online_users",
                    "users": online_users
                })
    
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
        # Broadcast user offline status
        await manager.broadcast_all({
            "type": "user_status",
            "user_id": user_id,
            "status": "offline"
        })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(user_id, websocket)
