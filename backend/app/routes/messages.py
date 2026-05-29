"""API routes for messaging"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import json
from datetime import datetime
from ..models import Message, Conversation
from ..schemas import (
    SendMessageRequest,
    MessageResponse,
    ConversationCreateRequest,
    ConversationResponse,
    ConversationDetailResponse,
    MarkMessageReadRequest
)
from ..utils.encryption import MessageEncryption
from .dependencies import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

# In-memory storage (replace with database)
messages_db = {}
conversations_db = {}
user_messages = {}  # user_id -> list of message_ids


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send an encrypted message to a recipient"""
    try:
        message = Message(
            sender_id=current_user["user_id"],
            recipient_id=request.recipient_id,
            encrypted_content=request.encrypted_content,
            conversation_id=request.conversation_id
        )
        
        messages_db[message.message_id] = message
        
        # Track messages for users
        if current_user["user_id"] not in user_messages:
            user_messages[current_user["user_id"]] = []
        user_messages[current_user["user_id"]].append(message.message_id)
        
        if request.recipient_id not in user_messages:
            user_messages[request.recipient_id] = []
        user_messages[request.recipient_id].append(message.message_id)
        
        return MessageResponse(**message.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/inbox", response_model=List[MessageResponse])
async def get_inbox(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Get encrypted messages for current user"""
    user_id = current_user["user_id"]
    
    # Get all messages where user is recipient
    user_inbox = [
        m for m in messages_db.values()
        if m.recipient_id == user_id
    ]
    
    # Sort by created_at descending
    user_inbox.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    paginated = user_inbox[skip : skip + limit]
    
    return [MessageResponse(**m.to_dict()) for m in paginated]


@router.get("/sent", response_model=List[MessageResponse])
async def get_sent_messages(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Get sent messages from current user"""
    user_id = current_user["user_id"]
    
    # Get all messages where user is sender
    user_sent = [
        m for m in messages_db.values()
        if m.sender_id == user_id
    ]
    
    # Sort by created_at descending
    user_sent.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    paginated = user_sent[skip : skip + limit]
    
    return [MessageResponse(**m.to_dict()) for m in paginated]


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific encrypted message"""
    if message_id not in messages_db:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = messages_db[message_id]
    
    # Check if user is sender or recipient
    if message.sender_id != current_user["user_id"] and message.recipient_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return MessageResponse(**message.to_dict())


@router.post("/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a message as read"""
    if message_id not in messages_db:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = messages_db[message_id]
    
    # Check if user is recipient
    if message.recipient_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only recipient can mark as read")
    
    message.mark_as_read()
    return MessageResponse(**message.to_dict())


@router.post("/conversation/create", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    conversation = Conversation(
        name=request.name,
        participants=request.participant_ids,
        created_by=current_user["user_id"],
        is_group=request.is_group
    )
    
    # Ensure creator is in participants
    if current_user["user_id"] not in conversation.participants:
        conversation.add_participant(current_user["user_id"])
    
    conversations_db[conversation.conversation_id] = conversation
    
    return ConversationResponse(**conversation.to_dict())


@router.get("/conversation/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation with all messages"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations_db[conversation_id]
    
    # Check if user is participant
    if current_user["user_id"] not in conversation.participants:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Get messages in conversation
    conv_messages = [
        m for m in messages_db.values()
        if m.conversation_id == conversation_id
    ]
    
    conv_messages.sort(key=lambda x: x.created_at)
    
    return ConversationDetailResponse(
        conversation_id=conversation.conversation_id,
        name=conversation.name,
        participants=conversation.participants,
        is_group=conversation.is_group,
        messages=[MessageResponse(**m.to_dict()) for m in conv_messages]
    )


@router.get("/conversation", response_model=List[ConversationResponse])
async def get_user_conversations(
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for current user"""
    user_id = current_user["user_id"]
    
    user_conversations = [
        c for c in conversations_db.values()
        if user_id in c.participants
    ]
    
    user_conversations.sort(key=lambda x: x.created_at, reverse=True)
    
    return [ConversationResponse(**c.to_dict()) for c in user_conversations]
