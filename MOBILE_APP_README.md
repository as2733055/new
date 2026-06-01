# Mobile Chat App - Flutter/Android

> A fully working Android APK with socket-based room chat functionality

## Features

- **Room-based Chat**: Create and join chat rooms to communicate with others
- **Real-time Messaging**: WebSocket-based instant messaging
- **User Authentication**: Secure login and registration
- **Message History**: Access previous messages in each room
- **Offline Support**: Local storage of messages and rooms
- **End-to-End Encryption**: Optional message encryption
- **User Presence**: See who's online in each room
- **Typing Indicators**: See when someone is typing

## Build & Installation

### Prerequisites
- Android SDK (API level 21+)
- Flutter SDK
- Gradle

### Build APK
```bash
cd mobile
flutter pub get
flutter build apk --release
```

### Install on Device
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

## Architecture

```
mobile/
├── android/          # Android native code
├── ios/              # iOS native code
├── lib/
│   ├── main.dart     # App entry point
│   ├── models/       # Data models
│   ├── services/     # API & WebSocket services
│   ├── screens/      # UI screens
│   ├── widgets/      # Reusable components
│   └── utils/        # Helper functions
└── pubspec.yaml      # Dependencies
```

## API Endpoints

### WebSocket
- `ws://SERVER:PORT/room-ws/chat/{room_id}/{token}`

### REST
- `GET /room-ws/rooms` - List all active rooms
- `GET /room-ws/room/{room_id}/info` - Get room info
- `GET /room-ws/room/{room_id}/history` - Get message history

## Message Format

### Join Room
```json
{
  "type": "message",
  "content": "Hello, room!",
  "encrypted_content": null
}
```

### Message Response
```json
{
  "type": "message",
  "id": "uuid",
  "room_id": "room_id",
  "user_id": "user_id",
  "username": "username",
  "content": "message",
  "timestamp": "2026-06-01T10:00:00"
}
```

## Configuration

Update `lib/config.dart`:
```dart
const String API_BASE_URL = 'http://YOUR_SERVER:8000';
const String WS_BASE_URL = 'ws://YOUR_SERVER:8000';
```

## Development

### Run on Emulator
```bash
flutter run
```

### Hot Reload
- Press `r` to hot reload
- Press `R` to hot restart

### Debug
```bash
flutter run -v
```

## Troubleshooting

### WebSocket Connection Failed
- Check server is running
- Verify firewall settings
- Check API base URL in config

### Messages Not Syncing
- Ensure authentication token is valid
- Check network connectivity
- Verify room ID is correct

## License

MIT
