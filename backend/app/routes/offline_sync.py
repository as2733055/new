"""
Backend API routes for offline message sync
Handles synchronization of messages from offline mode to server
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
from uuid import uuid4
import json

router = APIRouter(prefix="/api/offline", tags=["offline"])

# Dependency: get database session (adjust based on your setup)
async def get_db():
    # This should return your database session
    # Adjust based on your actual database setup
    pass


@router.get("/status")
async def offline_status():
    """
    Get current offline synchronization status
    Shows pending messages and sync queue
    """
    return {
        "status": "ok",
        "mode": "SERVER",
        "timestamp": datetime.utcnow().isoformat(),
        "pending_messages": 0,
        "sync_queue_size": 0
    }


@router.post("/messages/sync")
async def sync_offline_messages(payload: Dict, db = Depends(get_db)):
    """
    Receive batch of offline messages from client
    Messages were sent while client was offline
    
    Payload format:
    {
        "messages": [
            {
                "id": "msg-123",
                "sender_id": "user-1",
                "recipient_id": "user-2",
                "room_id": "room-1",
                "content": "Hello",
                "timestamp": "2026-06-02T10:00:00"
            }
        ],
        "device_id": "device-123",
        "client_mode": "offline"
    }
    """
    
    from app.models.offline_sync import OfflineMessageService
    from app.models.message import Message
    
    messages = payload.get("messages", [])
    device_id = payload.get("device_id")
    
    synced = []
    failed = []
    
    service = OfflineMessageService(db)
    
    for msg in messages:
        try:
            # Create server message from offline message
            message = Message(
                id=msg.get("id", str(uuid4())),
                sender_id=msg["sender_id"],
                recipient_id=msg.get("recipient_id"),
                room_id=msg.get("room_id"),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                is_from_offline=True  # Mark as from offline sync
            )
            
            db.add(message)
            synced.append(msg["id"])
            
        except Exception as e:
            failed.append({
                "message_id": msg.get("id"),
                "error": str(e)
            })
    
    await db.commit()
    
    return {
        "status": "synced",
        "synced_count": len(synced),
        "failed_count": len(failed),
        "synced_messages": synced,
        "failed_messages": failed,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/messages/pending")
async def get_pending_messages(user_id: str, db = Depends(get_db)):
    """
    Get messages that were pending delivery to this user
    (Sent while user was offline)
    
    Returns all messages the user should receive
    """
    
    from sqlalchemy import select
    from app.models.message import Message
    
    stmt = select(Message).where(
        (Message.recipient_id == user_id) |
        (Message.room_id.in_(
            select(distinct=True).where(Message.room_id.isnot(None))
        ))
    ).order_by(Message.timestamp.desc()).limit(100)
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    return {
        "pending_messages": [msg.to_dict() for msg in messages],
        "total": len(messages)
    }


@router.post("/conflict-resolution")
async def resolve_conflicts(payload: Dict, db = Depends(get_db)):
    """
    Handle message conflicts when same message received from multiple sources
    Uses last-write-wins strategy
    
    Payload:
    {
        "device_conflicts": [
            {
                "message_id": "msg-123",
                "from_device": "device-1",
                "from_device_timestamp": "2026-06-02T10:00:00",
                "server_timestamp": "2026-06-02T10:00:05"
            }
        ]
    }
    """
    
    conflicts = payload.get("device_conflicts", [])
    resolved = []
    
    for conflict in conflicts:
        msg_id = conflict["message_id"]
        device_ts = datetime.fromisoformat(conflict["from_device_timestamp"])
        server_ts = datetime.fromisoformat(conflict["server_timestamp"])
        
        # Last-write-wins: newer timestamp wins
        if server_ts > device_ts:
            resolution = "server_version_kept"
        else:
            resolution = "device_version_kept"
        
        resolved.append({
            "message_id": msg_id,
            "resolution": resolution,
            "server_timestamp": server_ts.isoformat(),
            "device_timestamp": device_ts.isoformat()
        })
    
    return {
        "status": "resolved",
        "conflicts_resolved": len(resolved),
        "resolutions": resolved
    }


@router.post("/sync-complete")
async def mark_sync_complete(payload: Dict, db = Depends(get_db)):
    """
    Client confirms sync is complete
    Use to trigger any post-sync actions
    
    Payload:
    {
        "device_id": "device-123",
        "messages_synced": 50,
        "status": "complete"
    }
    """
    
    device_id = payload.get("device_id")
    messages_synced = payload.get("messages_synced", 0)
    
    # Log sync completion
    print(f"Device {device_id} synced {messages_synced} messages")
    
    # Broadcast notification to other devices about the sync
    # This could trigger a websocket notification
    
    return {
        "status": "acknowledged",
        "device_id": device_id,
        "messages_synced": messages_synced,
        "next_sync_interval": 300  # 5 minutes
    }


@router.get("/stats")
async def get_offline_stats(db = Depends(get_db)):
    """
    Get statistics about offline messaging
    """
    
    from sqlalchemy import select, func
    from app.models.offline_sync import OfflineMessage, SyncQueue
    
    # Count pending messages
    pending_stmt = select(func.count(OfflineMessage.id)).where(
        OfflineMessage.status == "pending"
    )
    pending_count = await db.scalar(pending_stmt)
    
    # Count synced messages
    synced_stmt = select(func.count(OfflineMessage.id)).where(
        OfflineMessage.status == "synced"
    )
    synced_count = await db.scalar(synced_stmt)
    
    # Count failed messages
    failed_stmt = select(func.count(OfflineMessage.id)).where(
        OfflineMessage.status == "failed"
    )
    failed_count = await db.scalar(failed_stmt)
    
    # Count sync queue items
    queue_stmt = select(func.count(SyncQueue.id)).where(
        SyncQueue.status.in_(["pending", "failed"])
    )
    queue_size = await db.scalar(queue_stmt)
    
    return {
        "statistics": {
            "pending_messages": pending_count or 0,
            "synced_messages": synced_count or 0,
            "failed_messages": failed_count or 0,
            "sync_queue_size": queue_size or 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


# To register these routes in main.py:
"""
from app.routes.offline_sync import router as offline_router

app.include_router(offline_router)
"""
