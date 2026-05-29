# 🚨 Emergency Messaging System - QUICK START

**Status:** ✅ **FULLY WORKING** - Ready for emergency use

## 🎯 What This Does

This is a **fully encrypted messaging system** for when Signal is down or unavailable. People can:
- ✅ Register accounts
- ✅ Connect with friends
- ✅ Send encrypted messages (nobody can read them - not even the server)
- ✅ See online status in real-time
- ✅ Message history saved locally
- ✅ Works offline-first, syncs when connection restored

---

## ⚡ START IMMEDIATELY (60 seconds)

### Step 1: Start the System
```bash
cd /workspaces/new
docker-compose up -d
```

### Step 2: Open in Browser
```bash
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Step 3: Create Your First Account
1. Click "Register"
2. Create username & password
3. Done! Your encryption keys generated automatically

### Step 4: Connect with Friends
1. Have friends register too
2. Search for their username
3. Start messaging (all encrypted!)

---

## 📱 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Chat App** | http://localhost:3000 | Main messaging interface |
| **API** | http://localhost:8000 | Backend API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System status |

---

## 🔐 Security Features

✅ **End-to-End Encrypted**
- Only you and recipient can read messages
- Server stores encrypted blobs only

✅ **RSA-2048 + AES-256-GCM**
- Military-grade encryption
- Authenticated encryption prevents tampering

✅ **Zero-Knowledge Architecture**
- Server cannot read your messages
- Server cannot decrypt conversations

✅ **Secure Authentication**
- Password hashed with PBKDF2
- JWT tokens with expiration

---

## 🛑 Stop the System

```bash
docker-compose down
```

---

## 🔧 Troubleshooting

### System won't start?
```bash
# Check status
docker ps

# View logs
docker-compose logs

# Restart everything
docker-compose restart
```

### Port already in use?
```bash
# Change ports in docker-compose.yml
# Then restart
docker-compose down && docker-compose up -d
```

### Need to reset data?
```bash
# WARNING: This deletes all data
docker-compose down -v
docker-compose up -d
```

---

## 📊 System Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (React App)    │
└────────┬────────┘
         │ HTTPS/WSS
         ↓
┌─────────────────┐
│  Nginx Reverse  │
│     Proxy       │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌──────────┐
│FastAPI │  │PostgreSQL│
│Backend │  │Database  │
└────────┘  └──────────┘
```

---

## 🚀 For Emergency Use

### In Case of Signal Outage:
1. ✅ Start system: `docker-compose up -d`
2. ✅ Share URL with friends: `http://your-server:3000`
3. ✅ Everyone creates account
4. ✅ Search & connect
5. ✅ Message securely!

### Broadcasting Emergency Info:
```bash
# Backend is stateless and can run multiple instances
# Just start more containers on different ports
docker-compose -f docker-compose-2.yml up -d  # on port 8001, 3001
```

---

## 📖 More Information

- **README.md** - Project overview
- **QUICKSTART.md** - Detailed setup guide
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **MESSAGING_SYSTEM_README.md** - Complete technical docs

---

## 🆘 Emergency Contacts

If system fails:
1. Check logs: `docker-compose logs`
2. Restart: `docker-compose restart`
3. Reset: `docker-compose down -v && docker-compose up -d`

---

## ⚙️ System Requirements

✅ **Docker & Docker Compose** (v3.8+)
✅ **Ports 3000, 8000, 5432** (available)
✅ **RAM: 2GB minimum** (1GB per container)
✅ **Disk: 1GB** (for database)

---

## 💾 Backup Data

```bash
# Backup database
docker-compose exec db pg_dump -U messaging_user encrypted_messaging > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U messaging_user encrypted_messaging
```

---

**READY TO USE!** 🎉

Start messaging securely now!
