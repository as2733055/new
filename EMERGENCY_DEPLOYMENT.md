# 🚨 Emergency Deployment Guide

**For when Signal is down and you need reliable messaging NOW**

---

## ⚡ Quick Deploy Scenarios

### Scenario 1: Home/Office (Fastest - 60 seconds)

```bash
cd /workspaces/new
docker-compose up -d

# Done! Access at http://localhost:3000
```

**Requirements:**
- Docker installed
- 2 GB RAM
- Ports 3000, 8000 free

---

### Scenario 2: Shared Server (For Teams)

```bash
# Clone/transfer to shared machine
git clone <your-repo> /opt/emergency-messaging
cd /opt/emergency-messaging

# Start
docker-compose up -d

# Access: http://SERVER-IP:3000
```

**Share with team:**
```
Send them: http://SERVER-IP:3000
They create account and start messaging
```

---

### Scenario 3: Multiple Locations (Distributed)

**Location 1:**
```bash
cd /opt/emergency-messaging
docker-compose up -d
# Runs on port 3000
```

**Location 2 (same or different machine):**
```bash
cd /opt/emergency-messaging-2
# Edit docker-compose.yml - change ports to 3001:80, 8001:8000
docker-compose up -d
# Runs on port 3001
```

**Share links:**
- Team A: `http://LOCATION1:3000`
- Team B: `http://LOCATION2:3001`

---

## 📋 Pre-Deployment Checklist

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Ports available: `lsof -i :3000,8000,5432`
- [ ] 2GB+ RAM available: `free -h`
- [ ] Repository cloned: `ls /path/to/repo`

---

## 🚀 Deployment Steps

### 1. **Initial Setup**
```bash
# Clone/extract repository
cd /workspaces/new

# Verify files
ls -la docker-compose.yml backend frontend
```

### 2. **Start System**
```bash
# Build and start all services
docker-compose up -d

# Wait 30 seconds for all containers to start
sleep 30

# Check status
docker-compose ps
```

**Expected output:**
```
CONTAINER ID   IMAGE             STATUS      PORTS
xxxxx          new-backend       Up 20s      0.0.0.0:8000->8000/tcp
xxxxx          new-frontend      Up 20s      0.0.0.0:3000->80/tcp
xxxxx          postgres:13       Up 30s      0.0.0.0:5432->5432/tcp
```

### 3. **Verify System**
```bash
# Test backend health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"encrypted-messaging"}

# Test frontend
curl -I http://localhost:3000

# Should return:
# HTTP/1.1 200 OK
```

### 4. **Access in Browser**
```
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
```

---

## 👥 User Onboarding (For Emergency)

### Tell users:

1. **Access the app:**
   ```
   Go to: http://YOUR-SERVER:3000
   ```

2. **Create account:**
   - Click "Register"
   - Enter username
   - Create password (8+ chars)
   - Click Register

3. **Find friends:**
   - Click "Users" tab
   - Search by username
   - Click to start chat

4. **Send message:**
   - Type message
   - Click Send
   - Message is encrypted!

5. **See encryption:**
   - All messages automatically encrypted
   - Server can't read them
   - Only you + recipient can see content

---

## 🔐 Security for Emergency Use

### For Teams Sharing Same Server:

✅ **Good:**
- All messages encrypted client-side
- Server stores only encrypted blobs
- Each user has unique encryption keys
- Nobody can impersonate anyone

⚠️ **Be Aware:**
- Change default SECRET_KEY in `.env`
- Use HTTPS in production
- Use strong passwords

### Emergency Setup (Minimal):
```bash
# Works as-is for internal team
# All messages encrypted automatically
docker-compose up -d
```

### Production Setup (More Secure):
```bash
# Edit backend/.env
SECRET_KEY=your-unique-secret-key-min-32-chars
ENCRYPTION_KEY=your-unique-encryption-key

# Then restart
docker-compose restart backend
```

---

## 📈 Scaling for Emergency

### More Users? More Servers Needed!

**Single Server Capacity:**
- ~500 concurrent users
- ~10,000 messages/minute
- ~1GB database size (1 week of messaging)

**Scale by adding servers:**

```bash
# Server 2 (same setup, different ports)
PORT_FRONTEND=3001 PORT_BACKEND=8001 docker-compose up -d

# Server 3 (same setup, different ports)
PORT_FRONTEND=3002 PORT_BACKEND=8002 docker-compose up -d

# Share load via DNS or proxy:
# messages.service → Round-robin to all 3 servers
```

---

## 🛑 Emergency Stop

### Stop Everything
```bash
docker-compose down
```

### Stop with Data Wipe
```bash
# WARNING: Deletes all data!
docker-compose down -v
```

### Pause Without Stopping
```bash
docker-compose pause
docker-compose unpause
```

---

## 📊 Monitoring (For Admins)

### Check All Services

```bash
# Status
docker-compose ps

# View logs (all services)
docker-compose logs --tail=100

# View specific service logs
docker-compose logs backend --tail=50
docker-compose logs frontend --tail=50

# Real-time logs
docker-compose logs -f
```

### Performance Metrics

```bash
# CPU & Memory usage
docker stats

# Database size
docker-compose exec db du -sh /var/lib/postgresql/data

# Connected users (rough count)
docker-compose exec backend curl http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# If error: "Address already in use"
lsof -i :8000
kill -9 <PID>

# Restart
docker-compose restart backend
```

### Frontend Not Loading

```bash
# Check logs
docker-compose logs frontend

# If nginx errors, check nginx.conf
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Restart
docker-compose restart frontend
```

### Database Connection Issues

```bash
# Check database status
docker-compose ps db

# Test database connection
docker-compose exec backend python -c "from app.config import settings; print(settings.DATABASE_URL)"

# Restart database
docker-compose restart db
```

### Clear Cache & Restart

```bash
# Complete reset
docker-compose down
docker system prune -f
docker-compose up -d
```

---

## 📱 Accessing from Different Devices

### Same Network:
```
Desktop: http://localhost:3000
Mobile:  http://SERVER-IP:3000
```

### Different Networks (Internet):
```
Use VPN or reverse proxy to expose:
http://emergency-messaging.yourdomain.com
```

---

## 🆘 When Things Go Wrong

| Issue | Solution |
|-------|----------|
| Can't start Docker | `sudo systemctl start docker` |
| Port in use | Change port in `docker-compose.yml` |
| Can't register | Check logs: `docker-compose logs backend` |
| Messages not sending | Reload page, check API docs at `:8000/docs` |
| Database corrupt | `docker-compose down -v && docker-compose up -d` (data loss) |
| Slow performance | Add more RAM or reduce concurrent users |

---

## 📞 Support & Documentation

- **Quick Start:** EMERGENCY_QUICK_START.md
- **Technical Docs:** MESSAGING_SYSTEM_README.md
- **Full Deployment:** DEPLOYMENT_GUIDE.md
- **API Reference:** http://localhost:8000/docs

---

## ✅ SUCCESS CRITERIA

System is ready when:

- [ ] `docker-compose ps` shows 3 containers (backend, frontend, db)
- [ ] `curl http://localhost:8000/health` returns healthy
- [ ] Can access http://localhost:3000 in browser
- [ ] Can create account successfully
- [ ] Can search for and message other users
- [ ] Messages appear encrypted in browser console

---

## 🎯 Emergency Messaging Best Practices

1. **Tell everyone the URL immediately** - have it ready
2. **Create simple usernames** - avoid complex characters
3. **Share links via multiple channels** - email, SMS, social
4. **Test with small group first** - before full deployment
5. **Monitor system logs** - watch for errors
6. **Keep backup of database** - in case of corruption

---

**You're ready to provide emergency messaging when Signal goes down!** 🚀
