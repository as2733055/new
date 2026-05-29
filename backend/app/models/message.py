"""Message model for encrypted messaging"""
from datetime import datetime
from typing import Optional
import uuid


class Message:
    """Encrypted message model"""
    
    def __init__(
        self,
        sender_id: str,
        recipient_id: str,
        encrypted_content: str,  # JSON string containing {encrypted_message, encrypted_key, iv}
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_read: bool = False
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.encrypted_content = encrypted_content
        self.conversation_id = conversation_id
        self.created_at = created_at or datetime.utcnow()
        self.is_read = is_read
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "encrypted_content": self.encrypted_content,
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read
        }
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
