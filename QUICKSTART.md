# Quick Start Guide

Get the encrypted messaging system up and running in 5 minutes!

## 🚀 Quick Setup (5 minutes)

### Option 1: Using Docker (Easiest)

```bash
# Clone the repository
git clone <repository-url>
cd new

# Start everything with Docker
docker-compose up -d

# Open in browser
open http://localhost
```

**Done!** The application is running at `http://localhost`

### Option 2: Manual Setup (15 minutes)

#### Terminal 1: Start Backend

```bash
cd new/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install and run
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend is running at `http://localhost:8000`

#### Terminal 2: Start Frontend

```bash
cd new/frontend

# Install and run
npm install
npm start
```

Frontend opens at `http://localhost:3000`

## 📝 First Steps

### 1. Create Account

1. Click **"Create one"** on login page
2. Enter:
   - **Username**: anything (3+ characters)
   - **Email**: your@email.com
   - **Password**: at least 8 characters
3. Click **"Create Account"**

### 2. Create Second Account (for testing)

1. Open new private/incognito window
2. Go to `http://localhost:3000`
3. Register with different email
4. You now have two accounts for testing

### 3. Send First Message

**Account 1:**
1. Login with first account
2. Click **"Users"** tab
3. Search for the other username
4. Click on user to start conversation
5. Type a message and press **Enter** or click **Send**

**Account 2:**
1. Login with second account
2. Click **"Conversations"** tab
3. Click the conversation to open chat
4. See the decrypted message from Account 1
5. Reply with your own message

## 🔐 How It Works

```
Account 1 Types Message
        ↓
Client encrypts with Account 2's public key
        ↓
Encrypted message sent to server
        ↓
Server stores encrypted data (can't read it!)
        ↓
Account 2 receives encrypted message
        ↓
Client decrypts with Account 2's private key
        ↓
Plaintext only visible on Account 2's device
```

## 📱 Features to Try

### Conversations
- **Create direct messages** with any user
- **See online status** with green dot
- **View message history** in conversations
- **Search users** by name or email

### Real-time Features
- **Typing indicator** when someone types
- **Online/offline status** updates instantly
- **Message delivery** notification

### Security
- Every message is **encrypted end-to-end**
- Server **cannot read** your messages
- Only recipient can **decrypt** messages
- **Military-grade** RSA-2048 + AES-256 encryption

## 🛠️ API Testing (Optional)

Test API endpoints with curl:

```bash
# Get all users
curl http://localhost:8000/users/list

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Send message (using token from login)
curl -X POST http://localhost:8000/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": "user_id",
    "encrypted_content": "{...encrypted data...}"
  }'
```

## 📂 Project Files

```
new/
├── backend/              # Python FastAPI server
│   ├── app/
│   │   ├── main.py      # Server entry point
│   │   ├── routes/      # API endpoints
│   │   └── utils/       # Encryption
│   └── requirements.txt
├── frontend/            # React web app
│   ├── src/
│   │   ├── App.js
│   │   ├── components/  # UI components
│   │   └── services/    # API & encryption
│   └── package.json
├── README.md           # Main documentation
├── MESSAGING_SYSTEM_README.md  # Detailed guide
└── DEPLOYMENT_GUIDE.md # Production guide
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Can't Connect to Backend
1. Check backend is running: `curl http://localhost:8000`
2. Check frontend .env has correct API URL
3. Check CORS is enabled in backend config

### Messages Not Showing
1. Check browser console for errors (F12)
2. Check backend server logs
3. Try refreshing page
4. Clear browser cache

### WebSocket Connection Failed
1. Ensure backend is running
2. Check WS URL in frontend .env
3. Check firewall isn't blocking WebSocket

## 🔑 Security Notes

⚠️ **For Development Only:**
- Private keys stored in browser localStorage
- In-memory database (data lost on restart)
- Single server setup

✅ **For Production:**
- Use HTTPS/TLS only
- Store keys securely
- Use PostgreSQL database
- Setup proper authentication
- Enable rate limiting
- See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 📚 Learn More

- **Full Documentation**: [MESSAGING_SYSTEM_README.md](./MESSAGING_SYSTEM_README.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **API Reference**: Check backend README
- **Security Details**: See documentation

## ✨ What's Included

✅ End-to-end encryption (RSA-2048 + AES-256)
✅ Real-time messaging (WebSocket)
✅ User authentication (JWT tokens)
✅ User discovery (search & browse)
✅ Conversation history
✅ Online status tracking
✅ Typing indicators
✅ Production deployment scripts
✅ Docker support
✅ Security best practices

## 🤔 Common Questions

**Q: Where are my messages stored?**
A: Encrypted on the server. Only you and recipient can decrypt.

**Q: Can the server see my messages?**
A: No! Messages are encrypted before reaching the server.

**Q: Is this like Signal?**
A: Yes! It's an alternative when Signal is unavailable.

**Q: Can I use on mobile?**
A: Yes! Responsive web app works on all devices.

**Q: How do I backup my account?**
A: Export your private key from browser developer tools.

**Q: Is my private key secure?**
A: In development mode: No (localStorage). In production: Yes (with proper implementation).

## 🎉 Ready to Chat!

You now have a fully functional encrypted messaging system running locally!

### Next Steps:
1. Invite friends with different accounts
2. Test various conversations
3. Try group chats
4. Check out [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production setup

---

**Questions or issues?** Check the full documentation or troubleshooting guide!

Happy secure messaging! 🔒
