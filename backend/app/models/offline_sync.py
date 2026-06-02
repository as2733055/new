"""
Offline Message Queue and Sync System
Handles message persistence and sync between offline and online modes
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
from typing import List, Optional

Base = declarative_base()

class OfflineMessage(Base):
    """
    Message sent while offline or by offline user
    Stored locally until sync is possible
    """
    __tablename__ = "offline_messages"
    
    id = Column(String, primary_key=True)
    sender_id = Column(String, nullable=False)
    recipient_id = Column(String, nullable=False)
    room_id = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Sync tracking
    status = Column(String, default="pending")  # pending, sent, delivered, synced, failed
    sync_attempts = Column(Integer, default=0)
    last_sync_attempt = Column(DateTime, nullable=True)
    
    # Metadata
    is_offline = Column(Boolean, default=True)  # True if sent in offline mode
    encryption_key = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "room_id": self.room_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "is_offline": self.is_offline,
        }


class PeerDevice(Base):
    """
    Known peer devices for local network communication
    """
    __tablename__ = "peer_devices"
    
    device_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    
    # Network info
    ip_address = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    connection_type = Column(String)  # direct, relay, bluetooth
    
    # Status
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    discovery_timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "device_id": self.device_id,
            "username": self.username,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "port": self.port,
            "connection_type": self.connection_type,
            "is_online": self.is_online,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class SyncQueue(Base):
    """
    Queue of items waiting to be synced to server
    Tracks sync state and retry attempts
    """
    __tablename__ = "sync_queue"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, nullable=False)
    item_type = Column(String)  # message, room, user_profile
    
    # Content to sync
    payload = Column(JSON, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, syncing, synced, failed
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=5)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_retry = Column(DateTime, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "item_type": self.item_type,
            "status": self.status,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
        }


class OfflineMessageService:
    """
    Service for managing offline messages and sync queue
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def save_offline_message(self, 
                                   message_id: str,
                                   sender_id: str,
                                   recipient_id: str,
                                   content: str,
                                   room_id: Optional[str] = None) -> OfflineMessage:
        """Save a message to offline queue"""
        
        message = OfflineMessage(
            id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            room_id=room_id,
            content=content,
            status="pending",
            is_offline=True
        )
        
        self.db.add(message)
        await self.db.commit()
        return message
    
    async def get_pending_messages(self, limit: int = 100) -> List[OfflineMessage]:
        """Get messages waiting to be synced"""
        from sqlalchemy import select
        
        stmt = select(OfflineMessage).where(
            OfflineMessage.status == "pending"
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def mark_synced(self, message_id: str):
        """Mark message as successfully synced"""
        from sqlalchemy import update
        
        stmt = update(OfflineMessage).where(
            OfflineMessage.id == message_id
        ).values(status="synced", last_sync_attempt=datetime.utcnow())
        
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def add_to_sync_queue(self, 
                                message_id: str,
                                item_type: str,
                                payload: dict) -> SyncQueue:
        """Add item to sync queue"""
        from uuid import uuid4
        
        sync_item = SyncQueue(
            id=str(uuid4()),
            message_id=message_id,
            item_type=item_type,
            payload=payload,
            status="pending"
        )
        
        self.db.add(sync_item)
        await self.db.commit()
        return sync_item
    
    async def get_sync_queue(self, limit: int = 50) -> List[SyncQueue]:
        """Get items waiting to sync"""
        from sqlalchemy import select
        
        stmt = select(SyncQueue).where(
            SyncQueue.status.in_(["pending", "failed"])
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()


class MessageSyncService:
    """
    Handles synchronization of offline messages when coming back online
    """
    
    def __init__(self, db_session, http_client):
        self.db = db_session
        self.http = http_client
    
    async def sync_pending_messages(self, server_url: str) -> dict:
        """
        Sync all pending offline messages to server
        Returns sync report
        """
        from app.utils.network_detector import NetworkDetector
        
        detector = NetworkDetector(server_url)
        if not await detector._check_server():
            return {
                "status": "failed",
                "reason": "server_unavailable",
                "messages_synced": 0
            }
        
        service = OfflineMessageService(self.db)
        pending = await service.get_pending_messages()
        
        synced = 0
        failed = 0
        
        for message in pending:
            try:
                await self._sync_message(message, server_url)
                await service.mark_synced(message.id)
                synced += 1
            except Exception as e:
                print(f"Sync failed for message {message.id}: {e}")
                failed += 1
        
        return {
            "status": "completed",
            "messages_synced": synced,
            "messages_failed": failed,
            "total": len(pending)
        }
    
    async def _sync_message(self, message: OfflineMessage, server_url: str):
        """Sync single message to server"""
        import aiohttp
        
        payload = message.to_dict()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{server_url}/api/messages/sync",
                json=payload
            ) as resp:
                if resp.status not in [200, 201]:
                    raise Exception(f"Sync failed: {resp.status}")
                
                return await resp.json()


# Migration script to add tables:
"""
To add these tables to your database, run:

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'offline_messages',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('sender_id', sa.String, nullable=False),
        sa.Column('recipient_id', sa.String, nullable=False),
        sa.Column('room_id', sa.String, nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('status', sa.String, default='pending'),
        sa.Column('sync_attempts', sa.Integer, default=0),
        sa.Column('last_sync_attempt', sa.DateTime, nullable=True),
        sa.Column('is_offline', sa.Boolean, default=True),
        sa.Column('encryption_key', sa.String, nullable=True),
        sa.Column('device_id', sa.String, nullable=True),
    )
    
    op.create_table(
        'peer_devices',
        sa.Column('device_id', sa.String, primary_key=True),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('user_id', sa.String, nullable=False),
        sa.Column('ip_address', sa.String, nullable=True),
        sa.Column('port', sa.Integer, nullable=True),
        sa.Column('connection_type', sa.String),
        sa.Column('is_online', sa.Boolean, default=False),
        sa.Column('last_seen', sa.DateTime, server_default=sa.func.now()),
        sa.Column('discovery_timestamp', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'sync_queue',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('message_id', sa.String, nullable=False),
        sa.Column('item_type', sa.String),
        sa.Column('payload', sa.JSON, nullable=False),
        sa.Column('status', sa.String, default='pending'),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('max_retries', sa.Integer, default=5),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('last_retry', sa.DateTime, nullable=True),
        sa.Column('synced_at', sa.DateTime, nullable=True),
    )
"""
