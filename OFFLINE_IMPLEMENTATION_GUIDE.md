# Offline Chat Implementation Guide

## Quick Overview

This guide shows how to integrate offline/disaster-resilient features into your existing chat app across all platforms: Backend (FastAPI), Frontend (React), and Mobile (Flutter).

---

## Phase 1: Backend Integration (FastAPI)

### Step 1.1: Add Health Check Endpoint

Update your `backend/app/main.py`:

```python
from fastapi import FastAPI
from app.utils.network_detector import HealthCheckEndpoint
from app.routes.offline_sync import router as offline_router

app = FastAPI()

# Add health check routes
health = HealthCheckEndpoint(app)
health.register_routes()

# Add offline sync routes
app.include_router(offline_router)

# Your existing routes...
```

### Step 1.2: Add Database Migration

Run migrations to add the new tables (OfflineMessage, PeerDevice, SyncQueue):

```bash
cd backend
alembic upgrade head
```

Or manually create tables using the schema in `app/models/offline_sync.py`.

### Step 1.3: Update Requirements

Add to `backend/requirements.txt`:

```
aiohttp>=3.8.0
```

### Step 1.4: Test Backend Health Check

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "timestamp": "...", "mode": "SERVER"}
```

---

## Phase 2: Frontend Integration (React)

### Step 2.1: Create Network Status Component

Create `frontend/src/components/NetworkStatus.js`:

```javascript
import React, { useState, useEffect } from 'react';
import NetworkDetectionService from '../services/networkDetectionService';

function NetworkStatus() {
  const [status, setStatus] = useState({ mode: 'ONLINE' });
  
  useEffect(() => {
    const detector = new NetworkDetectionService();
    
    detector.onStatusChange((newStatus) => {
      setStatus(newStatus);
    });
    
    detector.startMonitoring();
    
    return () => detector.stopMonitoring();
  }, []);
  
  const isOnline = status.mode === 'ONLINE';
  
  return (
    <div className={`network-status ${isOnline ? 'online' : 'offline'}`}>
      <span>{isOnline ? '🟢' : '🟡'} {status.mode}</span>
    </div>
  );
}

export default NetworkStatus;
```

Add to your main App.js:

```javascript
import NetworkStatus from './components/NetworkStatus';

function App() {
  return (
    <div className="app">
      <NetworkStatus />
      {/* Rest of your app */}
    </div>
  );
}
```

### Step 2.2: Add Message Sync to Chat Component

Update your chat component:

```javascript
import MessageSyncService from '../services/messageSyncService';
import NetworkDetectionService from '../services/networkDetectionService';

function ChatWindow({ userId, recipientId }) {
  const [syncService] = useState(new MessageSyncService());
  const [detector] = useState(new NetworkDetectionService());
  const [isOffline, setIsOffline] = useState(false);
  const [syncProgress, setSyncProgress] = useState(null);
  
  useEffect(() => {
    syncService.init();
    
    // Listen for mode changes
    detector.onModeChange(async (isOnline) => {
      setIsOffline(!isOnline);
      
      if (isOnline) {
        // Switched to online - start syncing
        setSyncProgress({ message: 'Syncing offline messages...', percentage: 0 });
        syncService.onSyncProgress(setSyncProgress);
        
        const result = await syncService.syncPendingMessages();
        console.log('Sync result:', result);
      }
    });
    
    detector.startMonitoring();
    
    return () => {
      detector.stopMonitoring();
    };
  }, []);
  
  const handleSendMessage = async (content) => {
    if (isOffline) {
      // Save to offline queue
      await syncService.sendOfflineMessage({
        sender_id: userId,
        recipient_id: recipientId,
        content: content
      });
      
      // Show message in UI immediately
      addMessageToUI({
        sender_id: userId,
        content: content,
        status: 'pending'
      });
    } else {
      // Send via API normally
      // Your existing send logic
    }
  };
  
  return (
    <div className="chat-window">
      {syncProgress && (
        <div className="sync-progress">
          <div>{syncProgress.message} ({syncProgress.percentage}%)</div>
          <progress value={syncProgress.percentage} max="100" />
        </div>
      )}
      
      {/* Your existing chat UI */}
    </div>
  );
}
```

### Step 2.3: Add Storage Initialize to App.js

```javascript
import OfflineStorageService from './services/offlineStorageService';

useEffect(() => {
  const storage = new OfflineStorageService();
  storage.init(); // Initialize IndexedDB
}, []);
```

### Step 2.4: Update CSS for Network Status

Add to `frontend/src/App.css`:

```css
.network-status {
  padding: 8px 16px;
  position: fixed;
  top: 0;
  right: 0;
  font-size: 14px;
  font-weight: bold;
  border-radius: 0 0 0 8px;
  z-index: 1000;
}

.network-status.online {
  background: #90EE90;
  color: #000;
}

.network-status.offline {
  background: #FFD700;
  color: #000;
}

.sync-progress {
  background: #F0F0F0;
  padding: 12px;
  margin: 8px 0;
  border-radius: 4px;
  text-align: center;
}

.sync-progress progress {
  width: 100%;
  height: 20px;
  margin-top: 8px;
}
```

---

## Phase 3: Mobile Integration (Flutter)

### Step 3.1: Update pubspec.yaml

Add dependencies to `mobile/pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^0.13.5
  connectivity_plus: ^3.0.0
  hive: ^2.2.0
  hive_flutter: ^1.1.0

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

### Step 3.2: Create Network Detection Widget

Create a provider in your main.dart:

```dart
import 'package:provider/provider.dart';
import 'services/network_detection_service.dart';

class NetworkStatus extends ChangeNotifier {
  late NetworkDetectionService _detector;
  bool isOnline = true;
  
  NetworkStatus() {
    _detector = NetworkDetectionService();
    _detector.onModeChange((online) {
      isOnline = online;
      notifyListeners();
    });
    _detector.startMonitoring();
  }
  
  String get modeString => _detector.getModeString();
  String get indicator => _detector.getConnectionIndicator();
  
  void dispose() {
    _detector.stopMonitoring();
    super.dispose();
  }
}

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => NetworkStatus()),
      ],
      child: const MyApp(),
    ),
  );
}
```

### Step 3.3: Add Network Status UI

Create `mobile/lib/widgets/network_status_bar.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../main.dart'; // For NetworkStatus

class NetworkStatusBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<NetworkStatus>(
      builder: (context, status, _) {
        return Container(
          padding: EdgeInsets.all(8),
          color: status.isOnline ? Colors.green : Colors.amber,
          child: Row(
            children: [
              Text(
                status.indicator,
                style: TextStyle(fontSize: 18),
              ),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  status.modeString,
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
```

Use in your app:

```dart
@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: Text('Chat'),
    ),
    body: Column(
      children: [
        NetworkStatusBar(),
        Expanded(child: ChatScreen()),
      ],
    ),
  );
}
```

### Step 3.4: Integrate Message Sync

In your chat screen:

```dart
import 'services/message_sync_service.dart';
import 'package:provider/provider.dart';

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  late MessageSyncService _syncService;
  late NetworkStatus _networkStatus;
  
  @override
  void initState() {
    super.initState();
    _syncService = MessageSyncService();
    _syncService.init();
    
    // Listen for sync progress
    _syncService.onSyncProgress((progress) {
      print('${progress.message} (${progress.percentage}%)');
      // Update UI
    });
  }
  
  Future<void> sendMessage(String content) async {
    final isOnline = context.read<NetworkStatus>().isOnline;
    
    if (!isOnline) {
      // Send offline
      await _syncService.sendOfflineMessage(
        senderId: userId,
        recipientId: recipientId,
        content: content,
      );
      
      // Show in UI with "pending" status
      addMessageToUI(
        content,
        status: 'pending',
      );
    } else {
      // Send online - use your existing API call
    }
  }
  
  @override
  void dispose() {
    _syncService.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Consumer<NetworkStatus>(
      builder: (context, status, _) {
        if (!status.isOnline) {
          // Show offline indicator
          return Column(
            children: [
              Container(
                padding: EdgeInsets.all(8),
                color: Colors.amber,
                child: Text('Messages will sync when online'),
              ),
              Expanded(child: ChatList()),
            ],
          );
        }
        
        return ChatList();
      },
    );
  }
}
```

---

## Phase 4: Testing

### Test 1: Offline Message Sending

**Frontend:**
1. Open developer console (F12)
2. Go to Network tab
3. Set throttle to "Offline"
4. Try sending a message
5. Message should be saved locally
6. Restore network
7. Messages should sync

**Mobile:**
1. Disconnect WiFi and mobile data
2. Send message
3. Message shows "pending"
4. Reconnect network
5. Message syncs automatically

### Test 2: Network Detection

```bash
# Backend - Check health endpoint
curl http://localhost:8000/health

# Should see immediate response
# Stop backend server
curl http://localhost:8000/health  # Should timeout
# Watch frontend switch to OFFLINE mode
```

### Test 3: Sync Completion

1. Go offline
2. Send 3-5 messages
3. Check IndexedDB (Frontend) or Hive (Mobile)
4. Come online
5. Watch sync progress
6. Check server database for synced messages

---

## Testing Scenarios

### Scenario 1: Complete Internet Loss
```
Device: WiFi off, mobile data off
Expected:
- App switches to OFFLINE mode
- Messages saved locally
- UI shows yellow indicator
```

### Scenario 2: Server Down (No Internet)
```
Device: WiFi connected but server not running
Expected:
- Connection check fails
- App switches to OFFLINE mode
- Messages still sync locally
```

### Scenario 3: Intermittent Connectivity
```
Device: WiFi on/off repeatedly
Expected:
- App switches between ONLINE/OFFLINE
- Messages queued during offline periods
- Sync triggered when online
```

### Scenario 4: Disaster Scenario
```
Device: Internet completely unavailable
Expected:
- Multiple devices on same WiFi
- Can all send messages to each other
- Messages stored locally
- When internet returns, all sync
```

---

## Monitoring & Debugging

### Backend Logs
```bash
# Watch sync attempts
docker logs new-backend-1 -f | grep sync

# Check pending messages
curl http://localhost:8000/api/offline/stats
```

### Frontend Console
```javascript
// Check network status
NetworkDetectionService.getStatus()

// Check IndexedDB contents
await storage.getStats()
await storage.getPendingMessages()
```

### Mobile Logs
```bash
flutter logs | grep "MessageSync\|NetworkDetection"
```

---

## Troubleshooting

### Problem: Messages not saving offline
**Solution**: Check IndexedDB is initialized
```javascript
const storage = new OfflineStorageService();
await storage.init();
const stats = await storage.getStats();
console.log(stats);
```

### Problem: Sync not starting on reconnect
**Solution**: Check network detection is running
```javascript
detector.onModeChange((isOnline) => {
  console.log('Mode changed to:', isOnline ? 'ONLINE' : 'OFFLINE');
});
```

### Problem: Server not receiving synced messages
**Solution**: Verify offline sync endpoint
```bash
curl -X POST http://localhost:8000/api/offline/messages/sync \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"id":"1","sender_id":"user1","content":"test"}],
    "device_id": "device123"
  }'
```

---

## Next: Local Network P2P (Phase 2)

Once offline mode is working, you can add:

1. **mDNS Discovery**: Devices find each other on local network
2. **Direct P2P Connections**: Messages between devices without server
3. **Message Relay**: Devices forward messages to extend range
4. **Mesh Network**: Create local mesh for disaster scenarios

See `OFFLINE_ARCHITECTURE.md` for detailed mesh networking implementation.

---

## Summary

✅ **Backend**: Health checks + offline sync endpoints  
✅ **Frontend**: Network detection + IndexedDB storage + auto-sync  
✅ **Mobile**: Network detection + Hive storage + auto-sync  
✅ **Transparency**: Users don't need to do anything special  
✅ **Disaster Ready**: Works without internet  

Your app is now **offline-first and disaster-resilient**!
