"""Route dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from ..config import settings

security = HTTPBearer()

# Use settings for SECRET_KEY
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


async def get_current_user(credentials = Depends(security)) -> dict:
    """Extract and validate JWT token from request"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": user_id}
