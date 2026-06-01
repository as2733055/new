# Complete System Setup & Running Guide

> Full guide to run the backend server, frontend, and mobile app

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client Applications                 │
├─────────────────┬──────────────────┬────────────────────┤
│  Web Frontend   │   Mobile App     │   Web Client       │
│  (React)        │   (Flutter APK)  │   (Browser)        │
└────────┬────────┴────────┬─────────┴────────────┬───────┘
         │                 │                      │
         └─────────────────┼──────────────────────┘
                           │
                  WebSocket & REST API
                           │
┌──────────────────────────▼─────────────────────────────┐
│                      Backend Server                    │
│                   (FastAPI + WebSocket)                │
├──────────────────────────────────────────────────────┤
│  • User Management (Auth)                            │
│  • Room Management                                   │
│  • WebSocket Room Communication                      │
│  • Message History & Storage                         │
└──────────────────────────────────────────────────────┘
         │
         ▼
   Database (SQLite/PostgreSQL)
```

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- Flutter 3.0+
- 4GB RAM minimum
- 2GB disk space

### Ports Required
- Backend: 8000 (FastAPI)
- Frontend: 3000 (React) - optional
- WebSocket: 8000 (same as backend)

## Backend Setup & Running

### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Backend

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./chat.db

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://10.0.2.2:8000"]

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 3. Initialize Database

```bash
cd backend/app

# Run migrations or create tables
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

cd ../..
```

### 4. Run Backend Server

```bash
cd backend

# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs
```

## Frontend Setup & Running

### 1. Install Node Dependencies

```bash
cd frontend

npm install
```

### 2. Configure Frontend

Create `.env` file in `frontend/`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### 3. Run Frontend

```bash
# Development mode
npm start

# Production build
npm run build
npm run serve
```

**Expected Output:**
```
Compiled successfully!

Local:            http://localhost:3000
```

## Mobile App Setup & Running

### 1. Install Flutter Dependencies

```bash
cd mobile

flutter pub get
```

### 2. Configure Mobile App

Edit `lib/config.dart`:

```dart
// For Android Emulator (localhost translation)
const String API_BASE_URL = 'http://10.0.2.2:8000';
const String WS_BASE_URL = 'ws://10.0.2.2:8000';

// For Physical Device (use your PC IP)
// const String API_BASE_URL = 'http://192.168.x.x:8000';
// const String WS_BASE_URL = 'ws://192.168.x.x:8000';
```

### 3. Run on Emulator

```bash
# Start Android emulator
emulator -avd <your_emulator_name>

# Run app
flutter run

# Or specific device
flutter run -d <device_id>
```

### 4. Build APK

```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# Install on device
adb install build/app/outputs/flutter-apk/app-release.apk
```

## Docker Setup (Optional)

### 1. Build Docker Images

```bash
# Backend
docker build -t mobile-chat-backend ./backend

# Frontend
docker build -t mobile-chat-frontend ./frontend
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Quick Start - All at Once

### Using Terminal Multiplexing (tmux)

```bash
# Create new session
tmux new-session -d -s chat

# Backend window
tmux send-keys -t chat "cd backend && source venv/bin/activate && uvicorn app.main:app --reload" Enter

# Frontend window
tmux new-window -t chat
tmux send-keys -t chat:1 "cd frontend && npm start" Enter

# Access tmux
tmux attach -t chat
```

### Using Multiple Terminal Tabs

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend (optional):**
```bash
cd frontend
npm start
```

**Terminal 3 - Mobile Development:**
```bash
cd mobile
flutter run
```

## Testing the System

### 1. User Registration & Login

```bash
# Register
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Get Token

From login response, copy the `access_token`.

### 3. Test WebSocket

```bash
# Install wscat: npm install -g wscat

wscat -c ws://localhost:8000/room-ws/chat/test-room/<token>

# Send message (type in wscat terminal):
{"type":"message","content":"Hello from wscat"}

# Expected response:
{"type":"message","id":"uuid","room_id":"test-room","user_id":"...","username":"testuser","content":"Hello from wscat","timestamp":"..."}
```

### 4. Test from Web

1. Open http://localhost:3000 in browser
2. Register/Login
3. Create a room
4. Send messages
5. Messages should appear in real-time

### 5. Test from Mobile

1. Run Flutter app on emulator
2. Register/Login with same credentials
3. Join a room
4. Send/receive messages
5. Test with multiple devices/instances

## Accessing the System

| Component | URL | Purpose |
|-----------|-----|---------|
| Backend API | http://localhost:8000 | REST endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:3000 | Web app |
| WebSocket | ws://localhost:8000 | Real-time chat |
| Admin | http://localhost:8000/admin | (if configured) |

## Database Management

### SQLite (Default)

```bash
# Connect to database
sqlite3 chat.db

# List tables
.tables

# View rooms
SELECT * FROM rooms;

# View messages
SELECT * FROM room_messages;

# Clear all data (careful!)
DELETE FROM rooms;
DELETE FROM room_messages;
DELETE FROM users;
```

### PostgreSQL (Production)

```bash
# Connect
psql -U postgres -d mobile_chat

# Same SQL commands as above
```

## Troubleshooting

### Backend Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Try different port
uvicorn app.main:app --reload --port 8001
```

### Mobile App Can't Connect

1. Check server is running: `curl http://localhost:8000/health`
2. Verify IP in config.dart
3. Check firewall: `sudo ufw allow 8000`
4. Test from device: `adb shell ping 10.0.2.2`

### WebSocket Connection Issues

```bash
# Test WebSocket
wscat -c ws://localhost:8000/room-ws/chat/test-room/<token>

# Check server logs for errors
# Look at backend terminal output
```

### Frontend Won't Connect to Backend

1. Verify .env file exists
2. Check API_URL in .env
3. Clear browser cache
4. Check CORS settings in backend

## Performance Tips

### Backend

- Use production ASGI server: Gunicorn + Uvicorn
- Enable caching
- Use connection pooling for database
- Monitor with: `htop`, `top`

### Frontend

- Enable service workers for offline support
- Minify CSS/JS: `npm run build`
- Use CDN for assets
- Monitor with: DevTools > Performance

### Mobile

- Enable release mode: `flutter run --release`
- Profile app: `flutter run --profile`
- Check memory: Android Studio > Profiler

## Security Best Practices

Before Production:

- [ ] Change JWT_SECRET_KEY in .env
- [ ] Enable HTTPS/WSS
- [ ] Configure CORS properly
- [ ] Set DEBUG=false in backend
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Enable database backups
- [ ] Set up monitoring/logging

## Next Steps

1. [Deploy to Production](./DEPLOYMENT_GUIDE.md)
2. [Build APK for Distribution](./APK_BUILD_GUIDE.md)
3. [Configure Database](./ENVIRONMENT_SETUP.md)
4. [User Guide](./USER_GUIDE.md)

## Support & Troubleshooting

- Check `.vscode` folder for workspace settings
- Review logs in each component's output
- Check network connectivity
- Verify all prerequisites are installed
