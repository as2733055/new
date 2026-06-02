# Offline & Disaster-Resilient Chat Architecture

## Overview
This chatting app works like WhatsApp but can function **completely offline** during internet outages or disasters. It creates a **mesh network** where devices connect to each other directly without needing a central server.

## How It Works

### Two Operating Modes

#### 1. **Online Mode (Server Available)**
- Connects to central backend server
- Real-time messaging via WebSocket
- Full feature set

#### 2. **Offline/Disaster Mode (No Internet)**
- **Local Network Discovery**: Devices find each other on WiFi or Bluetooth
- **Direct P2P Connection**: Devices communicate directly without server
- **Message Relay**: Each device can relay messages from other devices
- **Mesh Network**: Forms a network where messages hop through devices to reach recipients
- **Automatic Sync**: When connection returns, all messages sync to server

---

## Architecture Components

### 1. **Network Detection Layer**
```
Device → Check Internet Connection
       → If YES: Use Server
       → If NO: Activate Local Discovery
```

**Implementation**: Monitor network changes, switch modes automatically

### 2. **Local Discovery**
**Technologies**:
- **mDNS (Multicast DNS)**: Devices broadcast their presence on local network
- **UDP Broadcasting**: Quick device discovery
- **Bluetooth**: Fallback for close-range communication

**Process**:
1. Device broadcasts presence with ID and username
2. Other devices detect the broadcast
3. Devices create peer list
4. P2P connections established

### 3. **Peer-to-Peer Messaging**
**Architecture**:
```
Device A → Device B (direct connection)
Device A → Device B → Device C (relay connection)
Device A → Device B → Device C → Device D (multi-hop)
```

**Protocol**:
- **Direct Message**: A→B (if in range)
- **Relay Message**: A→B→C (B forwards to C)
- **Broadcast**: All devices on network get message
- **Async Delivery**: Messages queued and delivered when recipient comes online

### 4. **Local Message Storage**
**SQLite Database** (on each device):
```
messages/
  - id (unique)
  - sender_id
  - recipient_id
  - content
  - timestamp
  - status (pending, sent, delivered, synced)
  - is_offline (true if sent in offline mode)

peers/
  - peer_id
  - username
  - last_seen
  - connection_type (direct/relay)

pending_sync/
  - message_id
  - status (waiting for sync)
```

### 5. **Offline Message Queue**
```
When offline:
  Message → Local DB → Retry Queue
  
When online:
  Retry Queue → Server Sync → Confirm Delivery
```

### 6. **Conflict Resolution**
- **Last-Write-Wins**: If same message received from multiple sources, newest timestamp wins
- **Message Deduplication**: Each message has unique ID to prevent duplicates
- **Vector Clocks**: Track message causality in mesh network

---

## Technology Stack by Platform

### Backend (FastAPI)
```
✓ Server API (for online mode)
✓ Sync endpoint (for receiving offline messages)
✓ Conflict resolution logic
✓ Message merging from multiple sources
```

### Frontend (React)
```
✓ Network detection
✓ Mode switching
✓ Local mDNS/UDP discovery
✓ P2P WebSocket connections
✓ Local storage (IndexedDB)
✓ Message queue management
```

### Mobile (Flutter)
```
✓ Network detection
✓ mDNS service discovery
✓ P2P Socket connections
✓ Bluetooth Low Energy (BLE)
✓ SQLite local storage
✓ Background message relay
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Network detection in all clients
- [ ] Server health check mechanism
- [ ] Mode switching (Online/Offline)
- [ ] Local message storage (SQLite/IndexedDB)

### Phase 2: Local Discovery (Week 2)
- [ ] mDNS service discovery (Frontend & Mobile)
- [ ] Peer broadcasting
- [ ] Peer list management
- [ ] Direct P2P connection establishment

### Phase 3: P2P Messaging (Week 2-3)
- [ ] Direct peer-to-peer messaging
- [ ] Message relay logic
- [ ] Mesh routing
- [ ] Offline message queue

### Phase 4: Sync & Conflict Resolution (Week 3)
- [ ] Backend sync endpoint
- [ ] Offline-to-online transition
- [ ] Message deduplication
- [ ] Conflict resolution strategy

### Phase 5: Advanced Features (Week 4)
- [ ] Bluetooth fallback (Mobile)
- [ ] Media file sync
- [ ] Group chat mesh support
- [ ] Disaster recovery dashboard

---

## Key Features in Disaster Mode

### ✅ What Works Offline
- Send/receive messages to anyone on local network
- Create rooms/groups locally
- View message history
- See online peers
- Automatic message relay
- Battery-efficient background mode

### 📝 What's Queued for Sync
- Messages to offline peers (delivered when they come online)
- New contacts/rooms created offline
- Media files
- Status updates

### 🔄 Automatic Sync Process
1. **Detection**: Internet connection restored
2. **Identification**: Check which mode device was in
3. **Upload**: Send all offline messages to server
4. **Merge**: Server merges with messages from other devices
5. **Download**: Receive missing messages from other users
6. **Confirm**: Mark all messages as synced
7. **Resume**: Switch back to server mode

---

## Security in Offline Mode

### Message Encryption
- **E2E Encryption**: All messages encrypted locally before transmission
- **No Plain Text**: Never stored unencrypted, even temporarily
- **Key Exchange**: Pre-shared or ephemeral keys for peer connections

### Network Security
- **Local Network Only**: P2P only works on trusted local network
- **Device Authentication**: Devices verify each other before connection
- **Rate Limiting**: Prevent spam from malicious local peers

### Disaster Resilience
- **Offline Doesn't Mean Unencrypted**: Encryption always ON
- **No Central Key Storage**: Each device manages its own keys
- **Secure Sync**: Messages verified before accepting from other devices

---

## Bandwidth Optimization (Critical for Disaster Scenarios)

### Compression
- **Message Compression**: LZ4 compression before transmission
- **Batch Sending**: Group multiple small messages
- **Differential Sync**: Only send changes, not full history

### Adaptive Protocols
- **WiFi**: Full messages, media supported
- **Bluetooth**: Text only, no media
- **LTE (limited): Text only, heavy compression

### Low-Bandwidth Mode
```
// Disabled in emergency mode
- Video/audio calls (use only text)
- Emoji animations
- Read receipts (defer until online)
- Typing indicators
```

---

## Deployment in Disaster Scenarios

### 1. Emergency Broadcast Mode
- All devices become repeaters
- Extended mesh range
- Battery-saving mode active

### 2. Group Coordination
- Disaster management team can coordinate
- Real-time status updates
- Resource allocation tracking

### 3. Information Dissemination
- One device broadcasts important information
- Other devices relay to extend range
- No internet needed

---

## Testing Offline Features

### Simulation Scenarios
```bash
# Disconnect internet
sudo ifconfig en0 down

# Test local discovery
# Test P2P messaging
# Test relay messaging
# Test sync when connection restored
```

### Network Conditions
- [ ] Complete internet loss
- [ ] Server downtime (backend not running)
- [ ] Intermittent connectivity (WiFi drops)
- [ ] High latency environment
- [ ] Limited bandwidth

---

## User Experience

### Status Indicators
```
🟢 Online (server connected)
🟡 Offline - Local Network (peer connected)
🔴 Offline - No peers (local storage only)
⚪ Connecting...
```

### User Notifications
- "Switched to offline mode - messaging available locally"
- "Connected to 5 peers on your network"
- "2 messages waiting to sync when online"
- "Messages synced! You're back online"

### Transparent Operation
- Users don't need to do anything
- App automatically switches modes
- Messages send/receive same way in both modes
- Sync happens automatically in background

---

## Next Steps

1. Review Architecture (this document)
2. Implement Phase 1: Network detection
3. Add local storage layer
4. Implement Phase 2: mDNS discovery
5. Add P2P messaging
6. Build sync mechanism
7. Test all scenarios

**Total Implementation Time**: 4 weeks for full offline capability

**Start**: Phase 1 - Network Detection (next)
