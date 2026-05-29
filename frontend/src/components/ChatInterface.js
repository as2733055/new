/**
 * Main Chat Interface Component
 */
import React, { useState, useEffect } from 'react';
import './ChatInterface.css';
import UserList from './UserList';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import apiService from '../services/apiService';
import webSocketService from '../services/webSocketService';

function ChatInterface({ currentUser, onLogout }) {
  const [activeTab, setActiveTab] = useState('conversations');
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [users, setUsers] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConversations();
    setupWebSocket();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await apiService.getUserConversations();
      setConversations(data || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = async () => {
    try {
      const token = apiService.getToken();
      await webSocketService.connect(token);

      webSocketService.onStatus((data) => {
        if (data.type === 'online_users') {
          setOnlineUsers(data.users || []);
        } else if (data.type === 'user_status') {
          console.log('User status:', data);
        }
      });
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const handleUserSelect = async (user) => {
    try {
      // Check if conversation already exists
      let conversation = conversations.find(
        (c) =>
          !c.is_group &&
          c.participants.includes(user.user_id) &&
          c.participants.includes(currentUser.user_id)
      );

      if (!conversation) {
        // Create new conversation
        conversation = await apiService.createConversation(
          [currentUser.user_id, user.user_id],
          null,
          false
        );
        setConversations([...conversations, conversation]);
      }

      setSelectedConversation(conversation);
      setActiveTab('chat');
    } catch (error) {
      console.error('Failed to create/select conversation:', error);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    setActiveTab('chat');
  };

  const handleLogout = () => {
    webSocketService.disconnect();
    onLogout();
  };

  return (
    <div className="chat-interface">
      <div className="header">
        <h1>🔒 Encrypted Messenger</h1>
        <div className="user-info">
          <span>{currentUser?.username}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>

      <div className="main-container">
        <div className="sidebar">
          <div className="tab-buttons">
            <button
              className={`tab-btn ${activeTab === 'conversations' ? 'active' : ''}`}
              onClick={() => setActiveTab('conversations')}
            >
              Conversations
            </button>
            <button
              className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              Users
            </button>
          </div>

          <div className="sidebar-content">
            {activeTab === 'conversations' && (
              <ConversationList
                conversations={conversations}
                selectedConversation={selectedConversation}
                onSelect={handleConversationSelect}
                loading={loading}
              />
            )}

            {activeTab === 'users' && (
              <UserList
                onlineUsers={onlineUsers}
                currentUserId={currentUser?.user_id}
                onUserSelect={handleUserSelect}
              />
            )}
          </div>
        </div>

        <div className="chat-area">
          {selectedConversation ? (
            <ChatWindow
              conversation={selectedConversation}
              currentUser={currentUser}
              onlineUsers={onlineUsers}
            />
          ) : (
            <div className="no-conversation">
              <p>Select a conversation or user to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
