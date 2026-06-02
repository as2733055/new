# How to Use the Offline Chat System - Practical Guide

## 🎯 What Happens Automatically

Your chat app now works like this:

```
✅ User has internet  → Chat works normally (online mode)
✅ User loses internet → Messages save locally (offline mode)
✅ User regains internet → Messages send automatically (sync)
✅ No action needed from user - it's all automatic!
```

---

## 📱 User Experience

### Before (Without Offline)
```
No internet → Can't send messages ❌
Try again → Still can't send ❌
No way to know if message sent ❌
```

### After (With Offline)
```
No internet → "🟡 Offline mode" indicator shows
Send message → Message shows as "pending" (saved locally)
Get internet back → Message automatically sends
App shows "✅ Synced" when complete
```

---

## ⚙️ Implementation Steps

### Step 1: Backend Setup (10 minutes)

**1. Update `backend/app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ADD THESE IMPORTS
from app.utils.network_detector import HealthCheckEndpoint
from app.routes.offline_sync import router as offline_router

app = FastAPI()

# Your existing CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADD THESE LINES - for health check
health = HealthCheckEndpoint(app)
health.register_routes()

# ADD THESE LINES - for offline sync
app.include_router(offline_router)

# Your existing routes below...
@app.get("/api/rooms")
async def list_rooms():
    pass
```

**2. Update `backend/requirements.txt`:**

Add this line:
```
aiohttp>=3.8.0
```

**3. Test it works:**

```bash
cd backend
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload

# In another terminal, test:
curl http://localhost:8000/health
# Should return: {"status": "healthy", "timestamp": "...", "mode": "SERVER"}
```

---

### Step 2: Frontend Setup (15 minutes)

**1. In your main Chat component (e.g., `ChatWindow.js`):**

```javascript
import React, { useState, useEffect } from 'react';
import NetworkDetectionService from '../services/networkDetectionService';
import MessageSyncService from '../services/messageSyncService';

function ChatWindow({ userId, recipientId }) {
  // State
  const [messages, setMessages] = useState([]);
  const [isOffline, setIsOffline] = useState(false);
  const [syncProgress, setSyncProgress] = useState(null);
  
  // Services
  const [detector] = useState(new NetworkDetectionService());
  const [syncService] = useState(new MessageSyncService());

  // Initialize on component mount
  useEffect(() => {
    initializeOfflineMode();
  }, []);

  const initializeOfflineMode = async () => {
    // 1. Initialize storage
    await syncService.init();

    // 2. Listen for network mode changes
    detector.onModeChange(async (isOnline) => {
      setIsOffline(!isOnline);
      
      if (isOnline) {
        // Switched to ONLINE - sync pending messages
        console.log('Back online! Starting sync...');
        setSyncProgress({ message: 'Syncing offline messages...', percentage: 0 });

        // Track sync progress
        syncService.onSyncProgress((progress) => {
          setSyncProgress(progress);
        });

        // Start sync
        const result = await syncService.syncPendingMessages();
        console.log('Sync complete:', result);
        
        // Clear progress after 2 seconds
        setTimeout(() => setSyncProgress(null), 2000);
      }
    });

    // 3. Start monitoring
    detector.startMonitoring();
  };

  const handleSendMessage = async (content) => {
    if (isOffline) {
      // ========== OFFLINE MODE ==========
      // Save message locally
      const message = await syncService.sendOfflineMessage({
        sender_id: userId,
        recipient_id: recipientId,
        content: content
      });

      // Show in UI immediately
      setMessages([...messages, {
        id: message.id,
        sender_id: userId,
        content: content,
        timestamp: new Date().toISOString(),
        status: 'pending'  // ← Shows as pending
      }]);
      
      console.log('Message saved offline, will sync when online');
      
    } else {
      // ========== ONLINE MODE ==========
      // Send via API normally (your existing code)
      const response = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender_id: userId,
          recipient_id: recipientId,
          content: content
        })
      });
      
      const result = await response.json();
      setMessages([...messages, result]);
    }
  };

  const handleCleanup = () => {
    detector.stopMonitoring();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => handleCleanup();
  }, []);

  return (
    <div className="chat-window">
      {/* Status Indicator */}
      <div className={`status-bar ${isOffline ? 'offline' : 'online'}`}>
        <span className="indicator">
          {isOffline ? '🟡 Offline Mode' : '🟢 Online'}
        </span>
        {isOffline && (
          <span className="info">Messages will sync when online</span>
        )}
      </div>

      {/* Sync Progress */}
      {syncProgress && (
        <div className="sync-progress">
          <div className="message">{syncProgress.message}</div>
          <progress value={syncProgress.percentage} max="100"></progress>
          <div className="percentage">{syncProgress.percentage}%</div>
        </div>
      )}

      {/* Message List */}
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.status}`}>
            <div className="content">{msg.content}</div>
            <div className="status-badge">
              {msg.status === 'pending' && '⏳ Pending'}
              {msg.status === 'sent' && '✓ Sent'}
              {msg.status === 'synced' && '✅ Synced'}
            </div>
          </div>
        ))}
      </div>

      {/* Message Input */}
      <div className="input-area">
        <input
          type="text"
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSendMessage(e.target.value);
              e.target.value = '';
            }
          }}
        />
      </div>
    </div>
  );
}

export default ChatWindow;
```

**2. Add CSS styling:**

```css
/* src/App.css */

.status-bar {
  padding: 12px;
  font-weight: bold;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-bar.online {
  background: #D4EDDA;
  color: #155724;
  border: 1px solid #C3E6CB;
}

.status-bar.offline {
  background: #FFF3CD;
  color: #856404;
  border: 1px solid #FFEAA7;
}

.indicator {
  font-size: 18px;
  margin-right: 10px;
}

.sync-progress {
  background: #F8F9FA;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  text-align: center;
}

.sync-progress .message {
  font-size: 14px;
  margin-bottom: 8px;
  color: #495057;
}

.sync-progress progress {
  width: 100%;
  height: 20px;
  border-radius: 4px;
}

.sync-progress .percentage {
  font-size: 12px;
  margin-top: 4px;
  color: #6C757D;
}

.message {
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  background: #F1F3F5;
}

.message.pending {
  opacity: 0.7;
  border-left: 4px solid #FFB81C;
}

.status-badge {
  font-size: 12px;
  color: #6C757D;
  margin-top: 4px;
}
```

**3. Initialize in App.js:**

```javascript
import React, { useEffect } from 'react';
import OfflineStorageService from './services/offlineStorageService';
import ChatWindow from './components/ChatWindow';

function App() {
  useEffect(() => {
    // Initialize offline storage when app starts
    const storage = new OfflineStorageService();
    storage.init();
  }, []);

  return (
    <div className="app">
      <ChatWindow userId="user-1" recipientId="user-2" />
    </div>
  );
}

export default App;
```

---

### Step 3: Mobile Setup (Flutter) - 10 minutes

**1. Update `mobile/pubspec.yaml`:**

Add these dependencies:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^0.13.5
  connectivity_plus: ^3.0.0
  hive: ^2.2.0
  hive_flutter: ^1.1.0
  provider: ^6.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  hive_generator: ^2.0.0
  build_runner: ^2.3.0
```

Run:
```bash
cd mobile
flutter pub get
flutter pub run build_runner build
```

**2. Update `mobile/lib/main.dart`:**

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/network_detection_service.dart';
import 'services/message_sync_service.dart';
import 'screens/chat_screen.dart';

// Network status provider
class NetworkStatusProvider extends ChangeNotifier {
  late NetworkDetectionService _detector;
  late MessageSyncService _syncService;
  bool isOnline = true;
  String syncMessage = '';
  int syncPercentage = 0;
  
  NetworkStatusProvider() {
    _detector = NetworkDetectionService();
    _syncService = MessageSyncService();
    
    // Listen for mode changes
    _detector.onModeChange((online) {
      isOnline = online;
      
      if (online) {
        // Start sync
        _startSync();
      }
      
      notifyListeners();
    });
    
    // Listen for sync progress
    _syncService.onSyncProgress((progress) {
      syncMessage = progress.message;
      syncPercentage = progress.percentage;
      notifyListeners();
    });
    
    _detector.startMonitoring();
  }
  
  Future<void> _startSync() async {
    final result = await _syncService.syncPendingMessages();
    print('Sync result: $result');
  }
  
  String get modeIndicator => _detector.getConnectionIndicator();
  String get modeString => _detector.getModeString();
  
  @override
  void dispose() {
    _detector.stopMonitoring();
    _syncService.dispose();
    super.dispose();
  }
}

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => NetworkStatusProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Offline Chat',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const ChatScreen(),
    );
  }
}
```

**3. Update `mobile/lib/screens/chat_screen.dart`:**

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/message_sync_service.dart';
import '../main.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  late MessageSyncService _syncService;
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];

  @override
  void initState() {
    super.initState();
    _syncService = MessageSyncService();
    _syncService.init();
  }

  Future<void> _sendMessage(String content, bool isOffline) async {
    if (content.isEmpty) return;

    if (isOffline) {
      // Send offline
      final message = await _syncService.sendOfflineMessage(
        senderId: 'user-1',
        recipientId: 'user-2',
        content: content,
      );

      setState(() {
        _messages.add(ChatMessage(
          id: message.id,
          content: content,
          status: 'pending',
          timestamp: DateTime.now(),
        ));
      });
    } else {
      // Send online (your existing API call)
      // Example:
      setState(() {
        _messages.add(ChatMessage(
          id: 'msg-${DateTime.now().millisecondsSinceEpoch}',
          content: content,
          status: 'sent',
          timestamp: DateTime.now(),
        ));
      });
    }

    _messageController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat'),
        elevation: 0,
      ),
      body: Consumer<NetworkStatusProvider>(
        builder: (context, networkStatus, _) {
          return Column(
            children: [
              // Status bar
              Container(
                padding: const EdgeInsets.all(12),
                color: networkStatus.isOnline ? Colors.green : Colors.amber,
                child: Row(
                  children: [
                    Text(
                      networkStatus.modeIndicator,
                      style: const TextStyle(fontSize: 20),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        networkStatus.modeString,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Sync progress
              if (networkStatus.syncMessage.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(12),
                  color: Colors.grey[200],
                  child: Column(
                    children: [
                      Text(networkStatus.syncMessage),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: networkStatus.syncPercentage / 100,
                      ),
                    ],
                  ),
                ),

              // Messages
              Expanded(
                child: ListView.builder(
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    return ChatBubble(
                      message: msg,
                    );
                  },
                ),
              ),

              // Message input
              Container(
                padding: const EdgeInsets.all(12),
                border: Border(
                  top: BorderSide(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _messageController,
                        decoration: InputDecoration(
                          hintText: 'Type a message...',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    FloatingActionButton(
                      mini: true,
                      onPressed: () {
                        _sendMessage(
                          _messageController.text,
                          !networkStatus.isOnline,
                        );
                      },
                      child: const Icon(Icons.send),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _syncService.dispose();
    _messageController.dispose();
    super.dispose();
  }
}

class ChatMessage {
  final String id;
  final String content;
  final String status;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.content,
    required this.status,
    required this.timestamp,
  });
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({
    Key? key,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final statusIcon = message.status == 'pending'
        ? '⏳'
        : message.status == 'sent'
            ? '✓'
            : '✅';

    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.all(8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.blue[100],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(message.content),
            const SizedBox(height: 4),
            Text(
              '$statusIcon ${message.status}',
              style: const TextStyle(fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🧪 Test It Now (3 minutes)

### Test 1: Frontend Offline

```bash
# 1. Open http://localhost:3000 in browser
# 2. Press F12 (Developer Tools)
# 3. Go to "Network" tab
# 4. Click dropdown that says "No throttling"
# 5. Select "Offline"
# 6. Type a message
# 7. ✅ Message shows as "pending"
# 8. Change back to "No throttling"
# 9. ✅ Message automatically syncs
```

### Test 2: Mobile Offline

```bash
# 1. Run app on device/emulator
# 2. Turn off WiFi and mobile data
# 3. Send a message
# 4. ✅ Shows as "⏳ pending"
# 5. Turn WiFi back on
# 6. ✅ Message syncs automatically
```

### Test 3: Server Down

```bash
# 1. Stop backend server
docker-compose down

# 2. Try sending messages in frontend/mobile
# 3. ✅ Messages save locally
# 4. Restart server
docker-compose up

# 5. ✅ Messages sync automatically
```

---

## 📊 What You Can Monitor

### In Browser Console (Frontend)

```javascript
// Check network status
detector.getStatus()
// Returns: {isOnline: true/false, mode: "ONLINE"/"OFFLINE_LOCAL"}

// Check pending messages
await syncService.storage.getPendingMessages()
// Returns: [{id, content, status, ...}]

// Check storage stats
await syncService.storage.getStats()
// Returns: {messages: 5, syncQueue: 2, totalItems: 7}
```

### In Flutter Logs

```bash
flutter logs | grep "NetworkDetection\|MessageSync"

# You'll see:
# [NetworkDetection] Mode changed: OFFLINE
# [MessageSync] Offline message saved: msg_123
# [MessageSync] Starting sync with 5 pending messages
# [MessageSync] Synced 5 messages in 2.3 seconds
```

### In Backend Logs

```bash
docker logs new-backend-1 -f | grep sync

# You'll see:
# POST /api/offline/messages/sync - Status: 200
# Synced 5 messages for device_123
```

---

## 🎯 Common Use Cases

### Case 1: User Traveling on Plane
```
1. Sends messages while WiFi off
2. ⏳ Shows as "pending"
3. Lands and turns on WiFi
4. ✅ All messages send automatically
5. ✅ Receives messages from others
```

### Case 2: Internet Outage
```
1. Internet goes down in city
2. Users can still message each other
3. Messages save locally
4. Internet comes back after 2 hours
5. ✅ All messages sync automatically
```

### Case 3: Disaster/Emergency
```
1. Major server failure/internet loss
2. All devices on same WiFi can message
3. Messages stored locally on each device
4. When connection restored, sync happens
5. ✅ No messages lost
```

---

## ⚡ Performance Tips

### To reduce network checks:
```javascript
// Frontend - check every 30 seconds instead of 10
const detector = new NetworkDetectionService('http://localhost:8000', 30000);
```

### To reduce storage:
```javascript
// Implement message cleanup (older than 30 days)
// Not included yet, but can be added
```

### To optimize sync:
```python
# Backend - increase batch size if you have many messages
# Currently syncs 100 messages per request
# Can be adjusted based on network conditions
```

---

## 🐛 Troubleshooting

### "Messages not saving offline"
```javascript
// Check in browser console:
const storage = new OfflineStorageService();
await storage.init();  // Make sure it initializes
```

### "Sync not starting when I reconnect"
```javascript
// Check network detection is running:
detector.startMonitoring();  // Must be called
detector.onModeChange(callback);  // Must have listener
```

### "Server not receiving synced messages"
```bash
# Check backend health:
curl http://localhost:8000/health
# Should return 200 status

# Check sync endpoint:
curl -X POST http://localhost:8000/api/offline/messages/sync
```

---

## ✅ You're Ready!

That's it! Your app now:
- 🟢 Works online with WebSocket
- 🟡 Works offline with local storage
- ↔️ Auto-syncs when reconnecting
- 📱 Works on Web and Mobile
- 🚨 Ready for disasters

**Start with Step 1 (Backend) → Step 2 (Frontend) → Step 3 (Mobile)**

Questions? Check the detailed guides:
- `OFFLINE_QUICK_START.md` - Quick reference
- `OFFLINE_IMPLEMENTATION_GUIDE.md` - More details
- `OFFLINE_TECHNICAL_REFERENCE.md` - Code examples
