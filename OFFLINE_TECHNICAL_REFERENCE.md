# Offline Chat - Technical Reference

## Architecture Diagrams

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Chat Application                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │        Network Detection Layer               │      │
│  │  ✓ Monitor connectivity (10s intervals)     │      │
│  │  ✓ Detect server availability               │      │
│  │  ✓ Switch ONLINE ↔ OFFLINE modes            │      │
│  │  ✓ Trigger mode change callbacks            │      │
│  └──────────────────────────────────────────────┘      │
│                        ↓                                │
│  ┌──────────────────────────────────────────────┐      │
│  │        Offline Storage Layer                 │      │
│  │  ✓ Store messages (IndexedDB/Hive)          │      │
│  │  ✓ Track peer devices                       │      │
│  │  ✓ Manage sync queue                        │      │
│  │  ✓ Provide conversation history             │      │
│  └──────────────────────────────────────────────┘      │
│                        ↓                                │
│  ┌──────────────────────────────────────────────┐      │
│  │        Message Sync Layer                    │      │
│  │  ✓ Queue messages when offline              │      │
│  │  ✓ Sync when online (auto)                  │      │
│  │  ✓ Track sync progress                      │      │
│  │  ✓ Retry failed messages                    │      │
│  │  ✓ Handle conflicts                         │      │
│  └──────────────────────────────────────────────┘      │
│                        ↓                                │
│  ┌──────────────────────────────────────────────┐      │
│  │        API & WebSocket Layer                 │      │
│  │  ✓ Send to server when online               │      │
│  │  ✓ Receive real-time updates                │      │
│  │  ✓ User presence tracking                   │      │
│  └──────────────────────────────────────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌────────┐         ┌──────────────┐      ┌─────────┐
    │ Server │         │  Local WiFi  │      │Database │
    │ (online)        │ (offline P2P) │      │(server) │
    └────────┘         └──────────────┘      └─────────┘
```

### Message Flow - Online Mode

```
┌─────────┐                                    ┌────────┐
│ Sender  │                                    │Receiver│
└────┬────┘                                    └───┬────┘
     │                                             │
     │ 1. Send Message                            │
     │─────────────────→ NetworkDetector          │
     │                        │                   │
     │                        ├─ Check Server     │
     │                        ├─ Check Internet   │
     │                        └─ isOnline = true  │
     │                                             │
     │ 2. Send via API                            │
     │─────────────────→ REST API                 │
     │                        │                   │
     │                        └─→ WebSocket ─────→ Receiver
     │                            Broadcast
     │
     ├─────────────── Message Status: SENT ───→ UI
     │
     ├─ 3. Receive ACK
     │                        ← Server Response
     │
     └─────────────── Message Status: DELIVERED ─→ UI
```

### Message Flow - Offline Mode

```
┌─────────┐                                    ┌────────┐
│ Sender  │                                    │Receiver│
└────┬────┘                                    └───┬────┘
     │                                             │
     │ 1. Send Message                            │
     │─────────────────→ NetworkDetector          │
     │                        │                   │
     │                        ├─ Check Server     │
     │                        ├─ Check Internet   │
     │                        └─ isOnline = false │
     │                                             │
     │ 2. Save Locally                            │
     │─────────────────→ OfflineStorage           │
     │                        │                   │
     │                        ├─ Save to DB       │
     │                        ├─ Add to Queue     │
     │                        └─ Notify UI        │
     │                                             │
     ├─────────────── Message Status: PENDING ──→ UI
     │
     ├─ [Offline - Waiting for connection]
     │
     ├─ 3. Connection Restored                    │
     │─────────────────→ NetworkDetector          │
     │                        │                   │
     │                        └─ onModeChange()   │
     │                                             │
     │ 4. Sync Messages                           │
     │─────────────────→ MessageSyncService       │
     │                        │                   │
     │                        └─→ /api/offline/messages/sync
     │                                 │
     │ 5. Upload & Receive              │
     │                        ← Server Response
     │                                             │
     └─────────────── Message Status: SYNCED ──→ UI
```

### Reconnect Flow

```
CONNECTION LOST                RECONNECTING                ONLINE
     │                               │                      │
     │ isOnline = false              │                      │
     ├─ Mode: OFFLINE               │                      │
     ├─ Storage: Active             │                      │
     ├─ API: Disabled               │                      │
     │                               │                      │
     │              Check Server────→│←─ Server Responds   │
     │                               │                     │
     │                        ┌──────┴─────┐                │
     │                        │            │                │
     │                    Online?        Offline?           │
     │                        │            │                │
     │                        ↓            ↓                │
     │                    RECONNECT   TRY AGAIN            │
     │                        │            │                │
     │◄────────────────────────┘            │                │
     │                                      │                │
     │ isOnline = true                      │                │
     ├─ Get Pending Messages                │                │
     ├─ POST to /api/offline/messages/sync  │                │
     ├─ Wait for Response                   │                │
     ├─ Mark as Synced                      │                │
     ├─ Download Missing Messages           │                │
     └─ Resume Normal Operation             │                │
                                            │                │
                                      [RETRY LOOP]           │
```

---

## Code Integration Examples

### Backend - Register Health Check

```python
# backend/app/main.py

from fastapi import FastAPI
from app.utils.network_detector import HealthCheckEndpoint
from app.routes.offline_sync import router as offline_router

app = FastAPI()

# Register health check routes
health = HealthCheckEndpoint(app)
health.register_routes()

# Register offline sync routes
app.include_router(offline_router)

# Your existing routes
@app.post("/api/messages")
async def send_message(message: MessageSchema):
    # Your existing code
    pass
```

### Frontend - Network Detection & Sync

```javascript
// src/components/ChatWindow.js

import React, { useState, useEffect } from 'react';
import NetworkDetectionService from '../services/networkDetectionService';
import MessageSyncService from '../services/messageSyncService';

function ChatWindow({ userId, recipientId }) {
  const [isOffline, setIsOffline] = useState(false);
  const [syncProgress, setSyncProgress] = useState(null);
  
  const detector = new NetworkDetectionService();
  const syncService = new MessageSyncService();
  
  useEffect(() => {
    syncService.init();
    
    // Listen for connection changes
    detector.onModeChange(async (isOnline) => {
      setIsOffline(!isOnline);
      
      if (isOnline) {
        // Switched to online - sync messages
        setSyncProgress({ message: 'Syncing...', percentage: 0 });
        
        syncService.onSyncProgress((progress) => {
          setSyncProgress(progress);
        });
        
        const result = await syncService.syncPendingMessages();
        console.log('Sync complete:', result);
      }
    });
    
    detector.startMonitoring();
    
    return () => detector.stopMonitoring();
  }, []);
  
  const sendMessage = async (content) => {
    if (isOffline) {
      // Save offline
      await syncService.sendOfflineMessage({
        sender_id: userId,
        recipient_id: recipientId,
        content: content
      });
    } else {
      // Send normally
      // Your existing API call
    }
  };
  
  return (
    <div className="chat-window">
      <div className={`status ${isOffline ? 'offline' : 'online'}`}>
        {isOffline ? '🟡 Offline' : '🟢 Online'}
      </div>
      
      {syncProgress && (
        <div className="sync-progress">
          {syncProgress.message} ({syncProgress.percentage}%)
        </div>
      )}
      
      {/* Message list */}
      {/* Message input */}
    </div>
  );
}

export default ChatWindow;
```

### Mobile - Network Provider

```dart
// lib/main.dart

import 'package:provider/provider.dart';
import 'services/network_detection_service.dart';
import 'services/message_sync_service.dart';

class NetworkStatusProvider extends ChangeNotifier {
  late NetworkDetectionService _detector;
  bool isOnline = true;
  late MessageSyncService _syncService;
  
  NetworkStatusProvider() {
    _detector = NetworkDetectionService();
    _syncService = MessageSyncService();
    
    _detector.onModeChange((online) {
      isOnline = online;
      
      if (online) {
        // Sync pending messages
        _syncService.syncPendingMessages().then((result) {
          print('Sync result: $result');
        });
      }
      
      notifyListeners();
    });
    
    _detector.startMonitoring();
  }
  
  String get modeIndicator => _detector.getConnectionIndicator();
  String get modeString => _detector.getModeString();
  
  @override
  void dispose() {
    _detector.stopMonitoring();
    super.dispose();
  }
}

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => NetworkStatusProvider()),
      ],
      child: MyApp(),
    ),
  );
}
```

---

## API Endpoints Reference

### Health Check
```
GET /health
Response: 
{
  "status": "healthy",
  "timestamp": "2026-06-02T10:00:00",
  "mode": "SERVER"
}
```

### Sync Messages
```
POST /api/offline/messages/sync
Request:
{
  "messages": [
    {
      "id": "msg_123",
      "sender_id": "user_1",
      "recipient_id": "user_2",
      "content": "Hello",
      "timestamp": "2026-06-02T10:00:00"
    }
  ],
  "device_id": "device_123"
}

Response:
{
  "status": "synced",
  "synced_count": 1,
  "failed_count": 0,
  "synced_messages": ["msg_123"]
}
```

### Get Pending
```
GET /api/offline/messages/pending?user_id=user_2
Response:
{
  "pending_messages": [
    {
      "id": "msg_456",
      "sender_id": "user_1",
      "content": "Hi there",
      "timestamp": "2026-06-02T10:05:00"
    }
  ],
  "total": 1
}
```

### Get Stats
```
GET /api/offline/stats
Response:
{
  "statistics": {
    "pending_messages": 5,
    "synced_messages": 150,
    "failed_messages": 0,
    "sync_queue_size": 3
  }
}
```

---

## State Management

### Network States

```
CHECKING
   ↓
┌─────────────┐
│   ONLINE    │ ← Server reachable
└─────────────┘
   ↓ ↑
CHECKING
   ↓
┌─────────────┐
│  OFFLINE    │ ← No server/Internet
└─────────────┘
```

### Message States

```
┌─────────┐
│CREATED  │ ← User typed message
└────┬────┘
     ↓
┌─────────┐
│PENDING  │ ← Queued in storage (offline)
└────┬────┘
     ↓ (connection restored)
┌─────────┐
│SYNCING  │ ← Uploading to server
└────┬────┘
     ↓ (upload successful)
┌─────────┐
│SYNCED   │ ← Confirmed on server
└────┬────┘
     ↓ (recipient received)
┌─────────┐
│DELIVERED│ ← Successfully delivered
└─────────┘
```

---

## Database Schema

### OfflineMessages Table
```sql
CREATE TABLE offline_messages (
  id VARCHAR PRIMARY KEY,
  sender_id VARCHAR NOT NULL,
  recipient_id VARCHAR NOT NULL,
  room_id VARCHAR,
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR DEFAULT 'pending', -- pending, sent, synced
  is_offline BOOLEAN DEFAULT TRUE,
  sync_attempts INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PeerDevices Table
```sql
CREATE TABLE peer_devices (
  device_id VARCHAR PRIMARY KEY,
  username VARCHAR NOT NULL,
  user_id VARCHAR NOT NULL,
  ip_address VARCHAR,
  port INT,
  connection_type VARCHAR, -- direct, relay, bluetooth
  is_online BOOLEAN DEFAULT FALSE,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  discovery_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### SyncQueue Table
```sql
CREATE TABLE sync_queue (
  id VARCHAR PRIMARY KEY,
  message_id VARCHAR NOT NULL,
  item_type VARCHAR, -- message, room, user_profile
  payload JSON NOT NULL,
  status VARCHAR DEFAULT 'pending', -- pending, syncing, synced
  retry_count INT DEFAULT 0,
  max_retries INT DEFAULT 5,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_retry DATETIME,
  synced_at DATETIME
);
```

---

## Configuration Options

### Network Detection
```javascript
// Frontend
const detector = new NetworkDetectionService(
  'http://localhost:8000',  // Server URL
  10000                      // Check interval (ms)
);
```

```dart
// Mobile
final detector = NetworkDetectionService(
  serverUrl: 'http://localhost:8000',
  checkIntervalSeconds: 10,
);
```

### Storage Cleanup
```javascript
// Auto-cleanup old messages (not implemented yet)
// Suggested: Delete messages older than 30 days
// Adjust retention policy based on device storage

const RETENTION_DAYS = 30;
const MAX_MESSAGES = 10000;
```

---

## Performance Considerations

### Network Detection Overhead
- Check interval: 10 seconds (adjustable)
- Each check: ~1KB HTTP request
- Overhead: ~100KB/day

### Storage Overhead
- Per message: ~1-2KB
- 1000 messages: ~1-2MB
- IndexedDB limit: 50-100MB per domain

### Sync Overhead
- Batch size: 100 messages
- Sync request: ~50-100KB
- Frequency: Only on reconnect

---

## Security Checklist

- [ ] Enable HTTPS for sync endpoints
- [ ] Validate user authentication before sync
- [ ] Encrypt messages in transit (HTTPS)
- [ ] Optional: Encrypt stored messages
- [ ] Implement rate limiting on sync endpoints
- [ ] Log all sync activities
- [ ] Validate message signatures
- [ ] Clean up old offline messages

---

## Monitoring & Logging

### Key Metrics to Track
- Network detection accuracy
- Sync success rate
- Average sync time
- Messages in offline queue
- Storage usage
- Device count (local network)

### Suggested Logs
```
[NetworkDetection] Mode changed: OFFLINE
[MessageSync] Starting sync with 15 pending messages
[MessageSync] Synced 15 messages in 2.3 seconds
[OfflineStorage] Storage size: 1.2MB (145 messages)
```

---

## Troubleshooting Decision Tree

```
Problem: Messages not saving offline
├─ Check: Is IndexedDB/Hive initialized?
├─ Check: Is OfflineStorageService.init() called?
└─ Solution: Await init() before sending

Problem: Sync not starting
├─ Check: Is NetworkDetectionService running?
├─ Check: Is mode change callback registered?
├─ Check: Is server reachable after reconnect?
└─ Solution: Call detector.startMonitoring()

Problem: Messages stuck in queue
├─ Check: Server health endpoint responding?
├─ Check: Network connectivity stable?
├─ Check: Sync retry count exceeded?
└─ Solution: Check server logs, restart sync

Problem: Sync endpoint returning errors
├─ Check: Is POST body correctly formatted?
├─ Check: Is user authenticated?
├─ Check: Is database writable?
└─ Solution: Verify backend setup
```

---

## Version Compatibility

| Component | Min Version | Recommended | Notes |
|-----------|-------------|-------------|-------|
| FastAPI | 0.68+ | 0.95+ | async/await support required |
| React | 16.8+ | 18.0+ | Hooks support required |
| Flutter | 2.5+ | 3.0+ | Null safety required |
| Node.js | 14+ | 18+ | For build tools |
| Python | 3.7+ | 3.10+ | Async features |

---

## Support Resources

- 📖 `OFFLINE_ARCHITECTURE.md` - Design details
- 📖 `OFFLINE_IMPLEMENTATION_GUIDE.md` - Step-by-step integration
- 📖 `OFFLINE_QUICK_START.md` - Quick setup
- 🐛 Check browser console (Frontend)
- 🐛 Check `flutter logs` (Mobile)
- 🐛 Check server logs (Backend)

**Complete reference for offline chat implementation!** 🚀
