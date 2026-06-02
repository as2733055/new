"""Main FastAPI application for encrypted messaging system"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime
from .routes import users, messages, websocket, room_websocket
from .config import settings

# Create FastAPI app
app = FastAPI(
    title="Encrypted Messaging System",
    description="Secure messaging application with end-to-end encryption",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(websocket.router)
app.include_router(room_websocket.router)

# Try to include offline sync routes (will fail gracefully if models don't exist)
try:
    from .routes import offline_sync
    app.include_router(offline_sync.router)
except (ImportError, Exception) as e:
    print(f"Warning: Could not load offline sync routes: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Encrypted Messaging System API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - used for network detection"""
    return {
        "status": "healthy",
        "service": "encrypted-messaging",
        "mode": "SERVER",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "status": "operational",
        "service": "encrypted-messaging",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "messaging": True,
            "rooms": True,
            "websocket": True,
            "offline_sync": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
