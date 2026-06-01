# Quick Reference - Mobile Chat System

## 🚀 Quick Start (5 minutes)

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Mobile (in another terminal)
cd mobile
flutter pub get
flutter run

# 3. Done! App will connect and you can start chatting
```

## 📱 Mobile App - Key Features

### Screens

| Screen | Features | Navigation |
|--------|----------|-----------|
| **Login** | Login/Register, Email validation | → Rooms |
| **Rooms** | List rooms, Create room, Join room, Logout | ↔ Chat |
| **Chat** | Send/receive messages, Typing indicator, User presence | ← Rooms |

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/users/login` | POST | User login |
| `/users/register` | POST | User registration |
| `/room-ws/chat/{roomId}/{token}` | WebSocket | Real-time chat |
| `/room-ws/rooms` | GET | List rooms |
| `/room-ws/room/{roomId}/info` | GET | Room info |

## 🔧 Configuration

### Server Connection (mobile/lib/config.dart)

```dart
// Emulator
const String API_BASE_URL = 'http://10.0.2.2:8000';
const String WS_BASE_URL = 'ws://10.0.2.2:8000';

// Physical Device
const String API_BASE_URL = 'http://192.168.1.100:8000';
const String WS_BASE_URL = 'ws://192.168.1.100:8000';
```

## 📦 Build Commands

```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# Install
adb install build/app/outputs/flutter-apk/app-release.apk

# Run on device
flutter run -d <device_id>

# Emulator
flutter run
```

## 🐛 Troubleshooting

### WebSocket Connection Failed
- Check server is running: `curl http://localhost:8000/health`
- Update config.dart with correct IP
- For emulator use `10.0.2.2` not `localhost`

### App Won't Build
```bash
flutter clean
flutter pub get
flutter build apk --release
```

### Connection to Server
```bash
# Test from device
adb shell ping 10.0.2.2

# Or check local IP
hostname -I
```

## 📊 Message Format

### Send Message
```json
{
  "type": "message",
  "content": "Hello!",
  "encrypted_content": null
}
```

### Receive Message
```json
{
  "type": "message",
  "id": "uuid",
  "room_id": "room_id",
  "user_id": "user_id",
  "username": "John",
  "content": "Hello!",
  "timestamp": "2026-06-01T10:00:00"
}
```

### Events
```json
{
  "type": "user_joined",
  "username": "John",
  "users_count": 5
}

{
  "type": "user_typing",
  "username": "John"
}
```

## 🔐 Security

- JWT token-based authentication
- Secure WebSocket connection
- Message encryption support (optional)
- Session timeout: 30 minutes default

## 📱 Supported Devices

- **Android**: 5.1+ (API 21+)
- **iOS**: 11.0+ (Flutter auto-builds for supported versions)

## 🎨 UI Framework

- **Flutter**: Modern, responsive UI
- **Material Design 3**: Latest material design
- **Custom Theme**: Easy customization

## 📚 File Structure

```
mobile/
├── lib/
│   ├── main.dart                 # App entry
│   ├── config.dart               # Configuration
│   ├── models/
│   │   └── models.dart           # Data models
│   ├── services/
│   │   ├── api_service.dart      # REST API
│   │   ├── websocket_service.dart # WebSocket
│   │   └── storage_service.dart  # Local storage
│   └── screens/
│       ├── login_screen.dart     # Login/Register
│       ├── room_list_screen.dart # Room list
│       └── chat_screen.dart      # Chat
├── pubspec.yaml                  # Dependencies
└── android/                       # Android config
```

## 🔄 Workflow

1. **User starts app** → Login screen
2. **Authenticates** → Gets JWT token
3. **Views rooms** → Joins selected room
4. **WebSocket connects** → Real-time messaging
5. **Send/receive messages** → Updates UI instantly

## 💾 Local Storage

- Auth token
- User ID & username
- Rooms list
- Message history (per room)
- Last accessed room

Cleared on logout.

## ⚙️ Advanced Configuration

### Message History Limit
Edit `config.dart`:
```dart
const int MESSAGE_HISTORY_LIMIT = 50;
```

### Heartbeat Interval
```dart
const int HEARTBEAT_INTERVAL = 30; // seconds
```

### Connection Timeout
```dart
const int SOCKET_TIMEOUT = 30; // seconds
```

## 📞 API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Connection refused" | Backend not running |
| "Invalid token" | Re-login required |
| "Room not found" | Room was deleted |
| "Message not sending" | Check connection status |
| "App crashes on startup" | Clear app data |

## 📝 Testing Checklist

- [ ] Login/Register works
- [ ] Token persists after restart
- [ ] Can list rooms
- [ ] Can join room
- [ ] Messages send in real-time
- [ ] Typing indicators show
- [ ] User presence updates
- [ ] Logout clears all data
- [ ] Offline handling works
- [ ] No crashes during normal use

## 🔗 Related Documentation

- [Mobile App README](./MOBILE_APP_README.md)
- [APK Build Guide](./APK_BUILD_GUIDE.md)
- [Complete Setup](./COMPLETE_SETUP.md)
- [API Documentation](./backend/app/main.py)

## 👨‍💻 Development

### Hot Reload
Press `r` in terminal while running

### Hot Restart
Press `R` in terminal

### Debug Info
Run with `-v` flag:
```bash
flutter run -v
```

### Check Errors
```bash
flutter doctor
flutter analyze
flutter test
```

## 🎯 Performance

- Lazy load messages
- Efficient re-renders with Provider
- WebSocket heartbeat (30s)
- Message caching
- Connection pooling

## 📦 Dependencies

- `web_socket_channel`: WebSocket communication
- `http`: REST API calls
- `provider`: State management
- `shared_preferences`: Local storage
- `google_fonts`: Typography
- `intl`: Date/time formatting

## 🔄 State Management

Using **Provider** for:
- Authentication state
- Room list
- Messages
- Connection status
- User presence

## 🌐 Network

- WebSocket: Auto-reconnect on disconnect
- HTTP: Timeout after 30 seconds
- Heartbeat: Every 30 seconds
- Message history: On room join

## 💡 Pro Tips

1. Use physical device for better testing
2. Check logs with: `flutter run -v`
3. Test offline scenarios
4. Monitor network with: Android Studio > Profiler
5. Use release mode for performance testing

---

**Version**: 1.0.0 | **Last Updated**: June 2026
