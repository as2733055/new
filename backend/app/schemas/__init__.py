"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRegisterResponse(BaseModel):
    """User registration response"""
    user_id: str
    username: str
    email: str
    public_key: str
    created_at: datetime


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """User login response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    username: str
    email: str
    public_key: str
    is_online: bool
    created_at: datetime


class UserListResponse(BaseModel):
    """List of users"""
    users: List[UserProfileResponse]


class SendMessageRequest(BaseModel):
    """Send encrypted message request"""
    recipient_id: str
    encrypted_content: str  # JSON string with {encrypted_message, encrypted_key, iv}
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Encrypted message response"""
    message_id: str
    sender_id: str
    recipient_id: str
    encrypted_content: str
    conversation_id: Optional[str]
    created_at: datetime
    is_read: bool


class ConversationCreateRequest(BaseModel):
    """Create conversation request"""
    name: Optional[str] = None
    participant_ids: List[str]
    is_group: bool = False


class ConversationResponse(BaseModel):
    """Conversation response"""
    conversation_id: str
    name: Optional[str]
    participants: List[str]
    created_by: str
    created_at: datetime
    is_group: bool
    message_count: int


class ConversationDetailResponse(BaseModel):
    """Conversation with messages"""
    conversation_id: str
    name: Optional[str]
    participants: List[str]
    is_group: bool
    messages: List[MessageResponse]


class MarkMessageReadRequest(BaseModel):
    """Mark message as read"""
    message_id: str
