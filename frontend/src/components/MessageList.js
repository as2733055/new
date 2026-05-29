/**
 * Message List Component
 */
import React from 'react';
import './MessageList.css';

function MessageList({ messages, currentUserId, loading }) {
  return (
    <div className="message-list">
      {loading && <p className="loading">Loading messages...</p>}

      {messages.length === 0 && !loading && (
        <p className="no-messages">No messages yet. Start the conversation!</p>
      )}

      {messages.map((message) => (
        <div
          key={message.message_id}
          className={`message ${
            message.sender_id === currentUserId ? 'sent' : 'received'
          }`}
        >
          <div className="message-content">
            {message.decrypted_content || '[Encrypted message]'}
          </div>
          <div className="message-time">
            {new Date(message.created_at).toLocaleTimeString()}
          </div>
        </div>
      ))}
    </div>
  );
}

export default MessageList;
