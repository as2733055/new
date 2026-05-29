/**
 * API service for communicating with the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  getToken() {
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API Error');
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return null;
    }

    return await response.json();
  }

  // User endpoints
  async registerUser(username, email, password) {
    return this.request('/users/register', {
      method: 'POST',
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    });
  }

  async loginUser(email, password) {
    const data = await this.request('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (data.access_token) {
      this.setToken(data.access_token);
    }

    return data;
  }

  async getUserProfile(userId) {
    return this.request(`/users/profile/${userId}`);
  }

  async listUsers(skip = 0, limit = 50) {
    return this.request(`/users/list?skip=${skip}&limit=${limit}`);
  }

  async searchUsers(query) {
    return this.request(`/users/search?query=${encodeURIComponent(query)}`);
  }

  // Message endpoints
  async sendMessage(recipientId, encryptedContent, conversationId = null) {
    return this.request('/messages/send', {
      method: 'POST',
      body: JSON.stringify({
        recipient_id: recipientId,
        encrypted_content: encryptedContent,
        conversation_id: conversationId,
      }),
    });
  }

  async getInbox(skip = 0, limit = 50) {
    return this.request(`/messages/inbox?skip=${skip}&limit=${limit}`);
  }

  async getSentMessages(skip = 0, limit = 50) {
    return this.request(`/messages/sent?skip=${skip}&limit=${limit}`);
  }

  async getMessage(messageId) {
    return this.request(`/messages/${messageId}`);
  }

  async markMessageRead(messageId) {
    return this.request(`/messages/${messageId}/read`, {
      method: 'POST',
      body: JSON.stringify({
        message_id: messageId,
      }),
    });
  }

  // Conversation endpoints
  async createConversation(participantIds, name = null, isGroup = false) {
    return this.request('/messages/conversation/create', {
      method: 'POST',
      body: JSON.stringify({
        participant_ids: participantIds,
        name,
        is_group: isGroup,
      }),
    });
  }

  async getConversation(conversationId) {
    return this.request(`/messages/conversation/${conversationId}`);
  }

  async getUserConversations() {
    return this.request('/messages/conversation');
  }
}

export default new APIService();
