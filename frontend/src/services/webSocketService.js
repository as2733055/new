/**
 * WebSocket service for real-time messaging
 */

const WS_BASE_URL = (process.env.REACT_APP_WS_URL || 'ws://localhost:8000').replace(/^http/, 'ws');

class WebSocketService {
  constructor() {
    this.ws = null;
    this.token = null;
    this.messageHandlers = [];
    this.statusHandlers = [];
    this.typingHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect(token) {
    return new Promise((resolve, reject) => {
      this.token = token;
      const wsUrl = `${WS_BASE_URL}/ws/chat/${token}`;

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.requestOnlineUsers();
          resolve();
        };

        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  sendMessage(recipientId, encryptedContent, timestamp = null) {
    this.send({
      type: 'message',
      recipient_id: recipientId,
      encrypted_content: encryptedContent,
      timestamp: timestamp || new Date().toISOString(),
    });
  }

  sendTypingNotification(recipientId) {
    this.send({
      type: 'typing',
      recipient_id: recipientId,
    });
  }

  sendStatus() {
    this.send({
      type: 'status',
    });
  }

  requestOnlineUsers() {
    this.send({
      type: 'online_users',
    });
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  onStatus(handler) {
    this.statusHandlers.push(handler);
  }

  onTyping(handler) {
    this.typingHandlers.push(handler);
  }

  handleMessage(data) {
    const type = data.type;

    if (type === 'message') {
      this.messageHandlers.forEach((handler) => handler(data));
    } else if (type === 'user_status') {
      this.statusHandlers.forEach((handler) => handler(data));
    } else if (type === 'typing') {
      this.typingHandlers.forEach((handler) => handler(data));
    } else if (type === 'online_users') {
      this.statusHandlers.forEach((handler) => handler(data));
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => {
        this.connect(this.token).catch(() => {});
      }, this.reconnectDelay);
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export default new WebSocketService();
