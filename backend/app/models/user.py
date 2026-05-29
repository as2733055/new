"""User model for encrypted messaging system"""
from datetime import datetime
from typing import Optional


class User:
    """User model with encryption keys"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        public_key: str,
        private_key: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.public_key = public_key
        self.private_key = private_key
        self.created_at = created_at or datetime.utcnow()
        self.is_online = False
    
    def to_dict(self):
        """Convert user to dictionary (without private key)"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "public_key": self.public_key,
            "created_at": self.created_at.isoformat(),
            "is_online": self.is_online
        }
