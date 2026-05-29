/**
 * Chat Window Component
 */
import React, { useState, useEffect, useRef } from 'react';
import './ChatWindow.css';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import apiService from '../services/apiService';
import webSocketService from '../services/webSocketService';
import { FrontendEncryption } from '../services/encryptionService';

function ChatWindow({ conversation, currentUser, onlineUsers }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadMessages();
    setupWebSocketHandlers();
  }, [conversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const data = await apiService.getConversation(conversation.conversation_id);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketHandlers = () => {
    webSocketService.onMessage((data) => {
      if (data.sender_id === conversation.participants.find((p) => p !== currentUser.user_id)) {
        // Decrypt and add message
        handleReceivedMessage(data);
      }
    });

    webSocketService.onTyping((data) => {
      if (data.sender_id === conversation.participants.find((p) => p !== currentUser.user_id)) {
        setTyping(data.sender_id);
        setTimeout(() => setTyping(null), 3000);
      }
    });
  };

  const handleReceivedMessage = async (data) => {
    try {
      // Decrypt message using current user's private key
      const decryptedContent = await FrontendEncryption.decryptMessage(
        JSON.parse(data.encrypted_content),
        currentUser.private_key
      );

      const newMessage = {
        message_id: Date.now().toString(),
        sender_id: data.sender_id,
        recipient_id: currentUser.user_id,
        encrypted_content: data.encrypted_content,
        decrypted_content: decryptedContent,
        created_at: data.timestamp || new Date().toISOString(),
        is_read: false,
      };

      setMessages([...messages, newMessage]);
    } catch (error) {
      console.error('Failed to decrypt message:', error);
    }
  };

  const handleSendMessage = async (messageText) => {
    try {
      // Get recipient's public key
      const recipientId = conversation.participants.find((p) => p !== currentUser.user_id);
      const recipientUser = await apiService.getUserProfile(recipientId);

      // Encrypt message
      const publicKey = await FrontendEncryption.loadPublicKey(recipientUser.public_key);
      const encryptedData = await FrontendEncryption.encryptMessage(messageText, publicKey);

      // Send via API
      const message = await apiService.sendMessage(
        recipientId,
        JSON.stringify(encryptedData),
        conversation.conversation_id
      );

      // Add to local state with decrypted content for display
      setMessages([
        ...messages,
        {
          ...message,
          decrypted_content: messageText,
        },
      ]);

      // Also send via WebSocket for real-time
      webSocketService.sendMessage(recipientId, JSON.stringify(encryptedData));
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message: ' + error.message);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const otherUserId = conversation.participants.find((p) => p !== currentUser.user_id);
  const isOnline = onlineUsers.includes(otherUserId);

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>{conversation.name || 'Direct Message'}</h2>
        <span className={`status-badge ${isOnline ? 'online' : 'offline'}`}>
          {isOnline ? '● Online' : '○ Offline'}
        </span>
      </div>

      <MessageList
        messages={messages}
        currentUserId={currentUser.user_id}
        loading={loading}
      />

      {typing && <div className="typing-indicator">User is typing...</div>}

      <div ref={messagesEndRef} />

      <MessageInput
        onSendMessage={handleSendMessage}
        onTyping={() => {
          const recipientId = conversation.participants.find((p) => p !== currentUser.user_id);
          webSocketService.sendTypingNotification(recipientId);
        }}
      />
    </div>
  );
}

export default ChatWindow;
