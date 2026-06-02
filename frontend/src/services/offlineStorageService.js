/**
 * Offline Message Storage Service
 * Uses IndexedDB to store messages locally when offline
 * Automatically syncs when connection restored
 */

class OfflineStorageService {
  constructor(dbName = 'ChatAppOfflineDB', version = 1) {
    this.dbName = dbName;
    this.version = version;
    this.db = null;
    this.isReady = false;
  }

  /**
   * Initialize the database
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => {
        console.error('[OfflineStorage] Failed to open database');
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        this.isReady = true;
        console.log('[OfflineStorage] Database initialized');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        this._setupSchema(event.target.result);
      };
    });
  }

  /**
   * Setup database schema
   */
  _setupSchema(db) {
    console.log('[OfflineStorage] Setting up schema...');

    // Offline messages store
    if (!db.objectStoreNames.contains('messages')) {
      const msgStore = db.createObjectStore('messages', { keyPath: 'id' });
      msgStore.createIndex('status', 'status', { unique: false });
      msgStore.createIndex('timestamp', 'timestamp', { unique: false });
      msgStore.createIndex('sender_recipient', ['sender_id', 'recipient_id'], { unique: false });
    }

    // Sync queue store
    if (!db.objectStoreNames.contains('syncQueue')) {
      const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
      syncStore.createIndex('status', 'status', { unique: false });
      syncStore.createIndex('created_at', 'created_at', { unique: false });
    }

    // Peer devices store
    if (!db.objectStoreNames.contains('peerDevices')) {
      db.createObjectStore('peerDevices', { keyPath: 'device_id' });
    }

    // Local rooms store
    if (!db.objectStoreNames.contains('rooms')) {
      db.createObjectStore('rooms', { keyPath: 'id' });
    }

    // User data store
    if (!db.objectStoreNames.contains('userData')) {
      db.createObjectStore('userData', { keyPath: 'key' });
    }
  }

  /**
   * Save offline message to local storage
   */
  async saveMessage(message) {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');

      const messageData = {
        id: message.id || `msg_${Date.now()}_${Math.random()}`,
        sender_id: message.sender_id,
        recipient_id: message.recipient_id,
        room_id: message.room_id,
        content: message.content,
        timestamp: message.timestamp || new Date().toISOString(),
        status: message.status || 'pending', // pending, sent, delivered, synced
        is_offline: message.is_offline !== undefined ? message.is_offline : true,
        created_at: new Date().toISOString()
      };

      const request = store.add(messageData);

      request.onsuccess = () => {
        console.log(`[OfflineStorage] Message saved: ${messageData.id}`);
        resolve(messageData);
      };

      request.onerror = () => {
        console.error('[OfflineStorage] Failed to save message:', request.error);
        reject(request.error);
      };
    });
  }

  /**
   * Get all pending messages
   */
  async getPendingMessages() {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['messages'], 'readonly');
      const store = transaction.objectStore('messages');
      const index = store.index('status');

      const request = index.getAll('pending');

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Get messages for a specific conversation
   */
  async getConversationMessages(senderId, recipientId) {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['messages'], 'readonly');
      const store = transaction.objectStore('messages');
      const index = store.index('sender_recipient');

      const request = index.getAll([senderId, recipientId]);

      request.onsuccess = () => {
        resolve(request.result.sort((a, b) => 
          new Date(a.timestamp) - new Date(b.timestamp)
        ));
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Mark message as synced
   */
  async markMessageSynced(messageId) {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');

      const getRequest = store.get(messageId);

      getRequest.onsuccess = () => {
        const message = getRequest.result;
        if (message) {
          message.status = 'synced';
          const updateRequest = store.put(message);

          updateRequest.onsuccess = () => {
            console.log(`[OfflineStorage] Message marked as synced: ${messageId}`);
            resolve(message);
          };

          updateRequest.onerror = () => {
            reject(updateRequest.error);
          };
        }
      };

      getRequest.onerror = () => {
        reject(getRequest.error);
      };
    });
  }

  /**
   * Add to sync queue
   */
  async addToSyncQueue(item) {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');

      const queueItem = {
        id: `sync_${Date.now()}_${Math.random()}`,
        message_id: item.message_id,
        item_type: item.item_type || 'message',
        payload: item.payload,
        status: item.status || 'pending',
        retry_count: 0,
        created_at: new Date().toISOString()
      };

      const request = store.add(queueItem);

      request.onsuccess = () => {
        console.log(`[OfflineStorage] Added to sync queue: ${queueItem.id}`);
        resolve(queueItem);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Get sync queue items
   */
  async getSyncQueue() {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readonly');
      const store = transaction.objectStore('syncQueue');
      const index = store.index('status');

      const request = index.getAll('pending');

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Save peer device
   */
  async savePeerDevice(device) {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['peerDevices'], 'readwrite');
      const store = transaction.objectStore('peerDevices');

      const deviceData = {
        device_id: device.device_id,
        username: device.username,
        user_id: device.user_id,
        ip_address: device.ip_address,
        port: device.port,
        connection_type: device.connection_type || 'direct',
        is_online: device.is_online !== undefined ? device.is_online : true,
        last_seen: new Date().toISOString()
      };

      const request = store.put(deviceData);

      request.onsuccess = () => {
        console.log(`[OfflineStorage] Peer device saved: ${deviceData.device_id}`);
        resolve(deviceData);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Get all peer devices
   */
  async getAllPeerDevices() {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['peerDevices'], 'readonly');
      const store = transaction.objectStore('peerDevices');

      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * Clear all data (for logout or reset)
   */
  async clearAll() {
    if (!this.isReady) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(
        ['messages', 'syncQueue', 'peerDevices', 'rooms', 'userData'],
        'readwrite'
      );

      const stores = [
        'messages',
        'syncQueue',
        'peerDevices',
        'rooms',
        'userData'
      ];

      let completed = 0;

      stores.forEach(storeName => {
        const store = transaction.objectStore(storeName);
        const request = store.clear();

        request.onsuccess = () => {
          completed++;
          if (completed === stores.length) {
            console.log('[OfflineStorage] All data cleared');
            resolve();
          }
        };

        request.onerror = () => {
          reject(request.error);
        };
      });
    });
  }

  /**
   * Get storage statistics
   */
  async getStats() {
    if (!this.isReady) await this.init();

    const messages = await this._getCount('messages');
    const syncQueue = await this._getCount('syncQueue');
    const peerDevices = await this._getCount('peerDevices');

    return {
      messages,
      syncQueue,
      peerDevices,
      totalItems: messages + syncQueue + peerDevices,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Helper: get count of items in a store
   */
  async _getCount(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.count();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }
}

export default OfflineStorageService;

/**
 * Usage in React Component:
 * 
 * import OfflineStorageService from './services/OfflineStorageService';
 * 
 * function ChatApp() {
 *   useEffect(() => {
 *     const storage = new OfflineStorageService();
 *     storage.init();
 *   }, []);
 *   
 *   const saveMessage = async (message) => {
 *     const storage = new OfflineStorageService();
 *     await storage.saveMessage(message);
 *   };
 * }
 */
