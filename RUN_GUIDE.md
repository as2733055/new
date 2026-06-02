# 🚀 Run Chat App in One Command

## Quick Start

### **Everything on One Command:**

```bash
# From the project root directory
python run.py
```

That's it! This will:
- ✅ Start Backend on http://localhost:8000
- ✅ Start Frontend on http://localhost:3000
- ✅ Check all dependencies
- ✅ Install missing packages automatically
- ✅ Show status and access URLs

---

## Usage Options

```bash
# Start everything (default)
python run.py

# Start only backend
python run.py --backend

# Start only frontend
python run.py --frontend

# Show help
python run.py --help
```

---

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | 🌐 Chat App Web UI |
| **Backend** | http://localhost:8000 | 🔌 API & WebSocket |
| **Health** | http://localhost:8000/health | ✓ Server Status |
| **API Status** | http://localhost:8000/api/status | 📊 Detailed Status |

---

## What Happens

```
python run.py
    ↓
✓ Checks Python packages (installs if missing)
    ↓
✓ Checks Node packages (installs if missing)
    ↓
✓ Starts Backend (FastAPI + Uvicorn)
    ↓
✓ Waits for backend to be ready
    ↓
✓ Starts Frontend (React Dev Server)
    ↓
✓ Waits for frontend to be ready
    ↓
✅ READY! Open http://localhost:3000
    ↓
Press Ctrl+C to stop everything
```

---

## Testing

Once running, test in a new terminal:

```bash
# Test backend health
curl http://localhost:8000/health

# Test API status
curl http://localhost:8000/api/status

# Test offline sync endpoint
curl -X POST http://localhost:8000/api/offline/messages/sync \
  -H "Content-Type: application/json" \
  -d '{"messages":[],"device_id":"test"}'
```

---

## Troubleshooting

### Port Already In Use

```bash
# If port 8000 is taken:
# Kill it (on Linux/Mac)
kill -9 $(lsof -t -i :8000)

# Then run again
python run.py
```

### Permission Denied on Mac/Linux

```bash
# Make script executable
chmod +x run.py

# Then run
python run.py
```

### Node Modules Issues

```bash
# The script auto-installs, but if it fails:
cd frontend
npm cache clean --force
rm -rf node_modules
npm install
cd ..
python run.py
```

### Backend Not Starting

```bash
# Check if Python packages are installed
pip install fastapi uvicorn

# Then try again
python run.py --backend
```

---

## Stop Services

**Press Ctrl+C** (or Cmd+C on Mac) in the terminal to gracefully stop all services.

---

## Manual Run (Alternative)

If you prefer manual control:

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm start
```

---

## Features Included

✅ Backend: FastAPI, WebSocket, Rooms, Encryption  
✅ Frontend: React, Real-time chat, Offline support  
✅ Network Detection: Auto online/offline switching  
✅ Message Sync: Automatic syncing when back online  
✅ Health Checks: Server monitoring  
✅ CORS: Cross-origin support  

---

## Environment Variables

If you need custom ports:

```bash
# For backend port (default 8000)
# Modify in run.py or use:
# python run.py --backend-port 9000

# For frontend port (default 3000)
# Set in run.py or:
export PORT=3001 && python run.py --frontend
```

---

## Next Steps

1. ✅ Run `python run.py`
2. 📖 Open browser to http://localhost:3000
3. 🧪 Test offline features (F12 → Network → Offline)
4. 🚀 Deploy to production (see deployment guides)

---

**Happy chatting!** 🎉
