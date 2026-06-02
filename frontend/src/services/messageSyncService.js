/**
 * Message Sync Service
 * Handles synchronization of offline messages when coming back online
 */

import OfflineStorageService from './offlineStorageService';

class MessageSyncService {
  constructor(serverUrl = 'http://localhost:8000', deviceId) {
    this.serverUrl = serverUrl;
    this.deviceId = deviceId || this._generateDeviceId();
    this.storage = new OfflineStorageService();
    this.isSyncing = false;
    this.syncCallbacks = [];
  }

  /**
   * Register callback for sync events
   */
  onSyncProgress(callback) {
    this.syncCallbacks.push(callback);
  }

  /**
   * Initialize sync service
   */
  async init() {
    await this.storage.init();
    console.log(`[MessageSync] Service initialized with device ID: ${this.deviceId}`);
  }

  /**
   * Sync all pending messages to server
   */
  async syncPendingMessages() {
    if (this.isSyncing) {
      console.log('[MessageSync] Sync already in progress');
      return { status: 'already_syncing' };
    }

    this.isSyncing = true;
    this._notifyProgress('Preparing to sync...', 0);

    try {
      // Get pending messages
      const pending = await this.storage.getPendingMessages();
      
      if (pending.length === 0) {
        console.log('[MessageSync] No pending messages to sync');
        this._notifyProgress('No messages to sync', 100);
        this.isSyncing = false;
        return { status: 'no_messages', count: 0 };
      }

      console.log(`[MessageSync] Syncing ${pending.length} messages...`);
      this._notifyProgress(`Syncing ${pending.length} messages...`, 10);

      // Prepare batch payload
      const payload = {
        messages: pending,
        device_id: this.deviceId,
        client_mode: 'offline'
      };

      // Send to server
      this._notifyProgress('Sending messages to server...', 30);
      const response = await this._sendToServer('/api/offline/messages/sync', payload);

      // Process response
      if (response.synced_count > 0) {
        this._notifyProgress(`Marking ${response.synced_count} messages as synced...`, 70);
        
        // Mark messages as synced
        for (const msgId of response.synced_messages) {
          await this.storage.markMessageSynced(msgId);
        }
      }

      // Notify server sync is complete
      this._notifyProgress('Notifying server of sync completion...', 90);
      await this._sendToServer('/api/offline/sync-complete', {
        device_id: this.deviceId,
        messages_synced: response.synced_count,
        status: 'complete'
      });

      this._notifyProgress('Sync complete!', 100);
      console.log(`[MessageSync] Sync completed: ${response.synced_count} synced, ${response.failed_count} failed`);

      this.isSyncing = false;
      return {
        status: 'success',
        synced_count: response.synced_count,
        failed_count: response.failed_count,
        total: pending.length
      };

    } catch (error) {
      console.error('[MessageSync] Sync failed:', error);
      this._notifyProgress(`Sync failed: ${error.message}`, 0);
      this.isSyncing = false;
      return {
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * Send message during offline mode
   * Saves to local storage and sync queue
   */
  async sendOfflineMessage(message) {
    try {
      // Save to local storage
      const saved = await this.storage.saveMessage({
        id: message.id || this._generateMessageId(),
        sender_id: message.sender_id,
        recipient_id: message.recipient_id,
        room_id: message.room_id,
        content: message.content,
        status: 'pending',
        is_offline: true
      });

      // Add to sync queue
      await this.storage.addToSyncQueue({
        message_id: saved.id,
        item_type: 'message',
        payload: saved
      });

      console.log(`[MessageSync] Offline message saved: ${saved.id}`);
      return saved;

    } catch (error) {
      console.error('[MessageSync] Failed to save offline message:', error);
      throw error;
    }
  }

  /**
   * Get offline messages for a conversation
   */
  async getConversationHistory(senderId, recipientId) {
    try {
      const messages = await this.storage.getConversationMessages(senderId, recipientId);
      return messages;
    } catch (error) {
      console.error('[MessageSync] Failed to get conversation history:', error);
      return [];
    }
  }

  /**
   * Get pending message count
   */
  async getPendingCount() {
    try {
      const pending = await this.storage.getPendingMessages();
      return pending.length;
    } catch (error) {
      console.error('[MessageSync] Failed to get pending count:', error);
      return 0;
    }
  }

  /**
   * Get storage stats
   */
  async getStorageStats() {
    try {
      return await this.storage.getStats();
    } catch (error) {
      console.error('[MessageSync] Failed to get storage stats:', error);
      return {};
    }
  }

  /**
   * Send data to server
   */
  async _sendToServer(endpoint, data) {
    const url = `${this.serverUrl}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Notify sync progress
   */
  _notifyProgress(message, percentage) {
    const progress = {
      message,
      percentage,
      timestamp: new Date().toISOString()
    };

    this.syncCallbacks.forEach(callback => {
      try {
        callback(progress);
      } catch (error) {
        console.error('[MessageSync] Error in sync callback:', error);
      }
    });
  }

  /**
   * Generate unique message ID
   */
  _generateMessageId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique device ID
   */
  _generateDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
  }

  /**
   * Clear all offline data (e.g., on logout)
   */
  async clearOfflineData() {
    try {
      await this.storage.clearAll();
      console.log('[MessageSync] All offline data cleared');
    } catch (error) {
      console.error('[MessageSync] Failed to clear offline data:', error);
      throw error;
    }
  }
}

export default MessageSyncService;

/**
 * Integration in React Component:
 * 
 * function ChatApp() {
 *   const syncService = new MessageSyncService();
 *   
 *   useEffect(() => {
 *     syncService.init();
 *     
 *     // Listen for mode changes
 *     const unsubscribe = networkDetector.onModeChange(async (isOnline) => {
 *       if (isOnline) {
 *         // Switched to online - sync pending messages
 *         const result = await syncService.syncPendingMessages();
 *         console.log('Sync result:', result);
 *       }
 *     });
 *     
 *     // Track sync progress
 *     syncService.onSyncProgress((progress) => {
 *       console.log('Sync progress:', progress.message, progress.percentage);
 *     });
 *     
 *     return () => unsubscribe();
 *   }, []);
 *   
 *   // When sending a message in offline mode
 *   const handleSendMessage = async (message) => {
 *     if (isOffline) {
 *       await syncService.sendOfflineMessage({
 *         sender_id: userId,
 *         recipient_id: recipientId,
 *         content: message
 *       });
 *     } else {
 *       // Send via API normally
 *     }
 *   };
 * }
 */
