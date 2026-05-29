"""Conversation model for grouped messages"""
from datetime import datetime
from typing import List, Optional
import uuid


class Conversation:
    """Represents a conversation between users or in a group"""
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
        participants: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_group: bool = False
    ):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.name = name
        self.participants = participants or []
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.is_group = is_group
        self.messages = []
    
    def add_participant(self, user_id: str):
        """Add participant to conversation"""
        if user_id not in self.participants:
            self.participants.append(user_id)
    
    def remove_participant(self, user_id: str):
        """Remove participant from conversation"""
        if user_id in self.participants:
            self.participants.remove(user_id)
    
    def add_message(self, message):
        """Add message to conversation"""
        self.messages.append(message)
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "name": self.name,
            "participants": self.participants,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "is_group": self.is_group,
            "message_count": len(self.messages)
        }
