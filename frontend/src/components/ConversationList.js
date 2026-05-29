/**
 * Conversation List Component
 */
import React from 'react';
import './ConversationList.css';

function ConversationList({ conversations, selectedConversation, onSelect, loading }) {
  if (loading) {
    return <p className="loading">Loading conversations...</p>;
  }

  return (
    <div className="conversation-list">
      {conversations.length === 0 ? (
        <p className="no-conversations">
          No conversations yet. Start chatting with a user.
        </p>
      ) : (
        conversations.map((conversation) => (
          <div
            key={conversation.conversation_id}
            className={`conversation-item ${
              selectedConversation?.conversation_id === conversation.conversation_id
                ? 'active'
                : ''
            }`}
            onClick={() => onSelect(conversation)}
          >
            <div className="conversation-header">
              <h3>{conversation.name || 'Direct Message'}</h3>
              <span className="message-count">{conversation.message_count}</span>
            </div>
            <p className="conversation-participants">
              {conversation.is_group ? `${conversation.participants.length} members` : 'Direct'}
            </p>
            <p className="conversation-date">
              {new Date(conversation.created_at).toLocaleDateString()}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

export default ConversationList;
