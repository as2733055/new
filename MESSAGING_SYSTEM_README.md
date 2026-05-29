# Encrypted Messaging System

A secure, end-to-end encrypted messaging application built with FastAPI and React. Provides a private communication channel when other services (like Signal) are unavailable.

## 🔒 Security Features

- **End-to-End Encryption**: RSA-2048 for key exchange, AES-256 for message encryption
- **Hybrid Encryption**: Combines asymmetric and symmetric encryption for optimal security and performance
- **No Plaintext Storage**: All messages are encrypted before being sent to the server
- **Unique Key Generation**: Each user gets a unique RSA key pair at registration
- **WebSocket Support**: Real-time messaging with secure WebSocket connections
- **JWT Authentication**: Token-based authentication for API security

## 📋 Architecture

### Backend (FastAPI)
- **Encryption**: RSA-2048 + AES-256-GCM hybrid encryption
- **Real-time Messaging**: WebSocket support for instant message delivery
- **User Management**: Registration, login, user discovery
- **Message Storage**: Encrypted message storage and retrieval
- **Conversation Management**: Support for direct and group conversations

### Frontend (React)
- **User Authentication**: Login and registration UI
- **Chat Interface**: Real-time chat with multiple conversations
- **User Discovery**: Search and browse online users
- **Message Encryption/Decryption**: Client-side encryption handling
- **WebSocket Integration**: Real-time typing indicators and message delivery

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies**:
```bash
cd frontend
npm install
```

2. **Create .env file**:
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

3. **Start the development server**:
```bash
npm start
```

The application will open at `http://localhost:3000`

## 📚 API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /users/login` - Login user
- `GET /users/profile/{user_id}` - Get user profile
- `GET /users/list` - List all users
- `GET /users/search` - Search users

### Messaging
- `POST /messages/send` - Send encrypted message
- `GET /messages/inbox` - Get received messages
- `GET /messages/sent` - Get sent messages
- `GET /messages/{message_id}` - Get specific message
- `POST /messages/{message_id}/read` - Mark message as read

### Conversations
- `POST /messages/conversation/create` - Create new conversation
- `GET /messages/conversation/{conversation_id}` - Get conversation with messages
- `GET /messages/conversation` - Get all user conversations

### WebSocket
- `WS /ws/chat/{token}` - Real-time messaging WebSocket

## 🔐 Encryption Details

### Key Generation
1. User registers with username, email, and password
2. Server generates unique RSA-2048 key pair
3. Public key stored in database, private key given to user
4. User stores private key securely in browser (localStorage - for demo only)

### Message Encryption Flow
1. User types message
2. Frontend generates random AES-256 key and IV
3. Message encrypted with AES-256-GCM
4. AES key encrypted with recipient's RSA-2048 public key
5. Both encrypted message and encrypted key sent to server
6. Server stores encrypted data without seeing plaintext
7. Recipient decrypts using their private key

### Message Decryption Flow
1. Recipient receives encrypted message
2. Frontend decrypts AES key using recipient's RSA private key
3. Frontend decrypts message using AES key
4. Message displayed in plaintext only on recipient's device

## 🗺️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── models/              # Data models
│   │   │   ├── user.py
│   │   │   ├── message.py
│   │   │   └── conversation.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   └── __init__.py
│   │   ├── routes/              # API routes
│   │   │   ├── users.py         # User authentication & management
│   │   │   ├── messages.py      # Message API
│   │   │   ├── websocket.py     # WebSocket handling
│   │   │   └── dependencies.py  # Route dependencies
│   │   └── utils/
│   │       ├── auth.py
│   │       └── encryption.py    # Encryption utilities
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.js               # Main app component
    │   ├── App.css
    │   ├── components/          # React components
    │   │   ├── LoginComponent.js
    │   │   ├── RegisterComponent.js
    │   │   ├── ChatInterface.js
    │   │   ├── ChatWindow.js
    │   │   ├── UserList.js
    │   │   ├── ConversationList.js
    │   │   ├── MessageList.js
    │   │   ├── MessageInput.js
    │   │   └── *.css            # Component styles
    │   └── services/            # API and utility services
    │       ├── apiService.js    # HTTP API client
    │       ├── webSocketService.js  # WebSocket client
    │       └── encryptionService.js # Client-side encryption
    └── package.json
```

## 💡 Usage Guide

### 1. Registration
- Click "Create one" on login page
- Enter username (3+ chars), email, and password (8+ chars)
- Account created with unique encryption keys

### 2. Login
- Enter email and password
- Receive JWT token for authentication
- Private key stored in browser

### 3. Finding Users
- Click "Users" tab in sidebar
- Search for username or email
- Click user to start conversation

### 4. Sending Messages
- Select conversation or user
- Type message in input box
- Press Enter or click Send
- Message encrypted client-side before sending

### 5. Receiving Messages
- Incoming messages appear in chat window
- Auto-decrypted with your private key
- Online status shown in real-time

## 🔧 Configuration

### Backend Configuration (`backend/app/config.py`)

```python
# Database
DATABASE_URL: str = "sqlite:///./messages.db"

# Security
SECRET_KEY: str = "your-secret-key-change-in-production"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# CORS
CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

# Encryption
ENCRYPTION_KEY: str = "default-key-32-bytes-long-123456"
```

### Frontend Configuration

Create `.env` file in frontend directory:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 📝 Security Considerations

### Current Implementation (Development)
- Private keys stored in browser localStorage (NOT recommended for production)
- In-memory database (data lost on server restart)
- Single-server deployment

### Production Recommendations
1. **Private Key Storage**:
   - Use browser's IndexedDB with encryption
   - Consider key derivation from password
   - Implement key export/import functionality

2. **Backend Database**:
   - Replace in-memory storage with PostgreSQL/MySQL
   - Add database encryption at rest
   - Implement regular backups

3. **Transport Security**:
   - Use HTTPS/TLS for all connections
   - Use WSS (secure WebSocket) for real-time messaging

4. **Authentication**:
   - Implement 2FA/MFA
   - Add rate limiting
   - Implement account lockout after failed attempts

5. **Compliance**:
   - Add audit logging
   - Implement data retention policies
   - Follow GDPR/privacy regulations

6. **Code Security**:
   - Regular security audits
   - Dependency vulnerability scanning
   - Implement Content Security Policy (CSP)

## 🧪 Testing

### Manual Testing
1. Register two user accounts
2. Login with first account
3. Search for and select second user
4. Send encrypted message
5. Verify message appears on recipient's side
6. Logout and login with second account
7. Verify message is still encrypted

### API Testing
```bash
# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# List users
curl http://localhost:8000/users/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📦 Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `cryptography` - Encryption library
- `pydantic` - Data validation
- `pyjwt` - JWT token handling
- `passlib` - Password hashing
- `websockets` - WebSocket support

### Frontend
- `react` - UI library
- `crypto-js` - Cryptography utilities

## 🐛 Troubleshooting

### WebSocket Connection Failed
- Check backend is running
- Verify WS_URL in environment
- Check browser console for errors

### Messages Not Decrypting
- Verify private key is stored correctly
- Check encryption/decryption logic
- Check browser console for errors

### CORS Errors
- Verify CORS origins in backend config
- Check Origin header in requests
- Restart backend after config changes

## 📄 License

MIT License - Feel free to use for personal or commercial projects

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Check browser/server console logs

## ⚠️ Disclaimer

This is a demonstration application. For production use:
- Conduct security audit
- Implement proper key management
- Use database for persistence
- Implement proper authentication/authorization
- Follow security best practices

---

**Built with security and privacy in mind** 🔒
