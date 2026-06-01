"""User authentication and management routes"""
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from ..models import User
from ..schemas import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfileResponse,
    UserListResponse
)
from ..utils.encryption import EncryptionManager

router = APIRouter(prefix="/users", tags=["users"])

# Security - use argon2 instead of bcrypt to avoid issues
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory storage (replace with database)
users_db = {}
user_credentials = {}  # user_id -> {password_hash, email}


def hash_password(password: str) -> str:
    """Hash a password"""
    # Truncate to 72 bytes for bcrypt compatibility
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserRegisterResponse)
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    # Check if user exists
    if any(u.email == request.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if any(u.username == request.username for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Generate encryption keys
    private_key, public_key = EncryptionManager.generate_key_pair()
    
    # Create user
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        username=request.username,
        email=request.email,
        public_key=public_key,
        private_key=private_key
    )
    
    users_db[user_id] = user
    user_credentials[user_id] = {
        "email": request.email,
        "password_hash": hash_password(request.password)
    }
    
    return UserRegisterResponse(**user.to_dict())


@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest):
    """Login user and get access token"""
    # Find user by email
    user = None
    user_id = None
    for uid, u in users_db.items():
        if u.email == request.email:
            user = u
            user_id = uid
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    creds = user_credentials.get(user_id)
    if not creds or not verify_password(request.password, creds["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=access_token_expires
    )
    
    return UserLoginResponse(
        access_token=access_token,
        user=user.to_dict()
    )


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get user profile (public)"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    return UserProfileResponse(**user.to_dict())


@router.get("/list", response_model=UserListResponse)
async def list_users(skip: int = 0, limit: int = 50):
    """List all users (for discovery)"""
    users = list(users_db.values())
    users.sort(key=lambda x: x.created_at)
    
    paginated = users[skip : skip + limit]
    return UserListResponse(
        users=[UserProfileResponse(**u.to_dict()) for u in paginated]
    )


@router.get("/search", response_model=UserListResponse)
async def search_users(query: str):
    """Search users by username or email"""
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Search query too short")
    
    query_lower = query.lower()
    matching_users = [
        u for u in users_db.values()
        if query_lower in u.username.lower() or query_lower in u.email.lower()
    ]
    
    return UserListResponse(
        users=[UserProfileResponse(**u.to_dict()) for u in matching_users[:20]]
    )
