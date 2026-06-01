"""Room model for group chat functionality"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Room(Base):
    """Chat room model"""
    __tablename__ = "rooms"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    max_members = Column(Integer, default=100)
    member_count = Column(Integer, default=0)


class RoomMember(Base):
    """Room membership model"""
    __tablename__ = "room_members"
    
    id = Column(String, primary_key=True, index=True)
    room_id = Column(String, index=True)
    user_id = Column(String, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)


class RoomMessage(Base):
    """Room message model"""
    __tablename__ = "room_messages"
    
    id = Column(String, primary_key=True, index=True)
    room_id = Column(String, index=True)
    user_id = Column(String, index=True)
    username = Column(String)
    content = Column(String)
    encrypted_content = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    is_encrypted = Column(Boolean, default=False)
