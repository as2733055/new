/**
 * Message Input Component
 */
import React, { useState } from 'react';
import './MessageInput.css';

function MessageInput({ onSendMessage, onTyping }) {
  const [messageText, setMessageText] = useState('');

  const handleSend = async (e) => {
    e.preventDefault();

    if (!messageText.trim()) {
      return;
    }

    try {
      await onSendMessage(messageText);
      setMessageText('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const handleInputChange = (e) => {
    setMessageText(e.target.value);
    if (onTyping) {
      onTyping();
    }
  };

  return (
    <div className="message-input">
      <form onSubmit={handleSend}>
        <textarea
          value={messageText}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Press Enter to send)"
          rows="3"
        />
        <button type="submit" disabled={!messageText.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default MessageInput;
