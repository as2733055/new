/**
 * User List Component
 */
import React, { useState, useEffect } from 'react';
import './UserList.css';
import apiService from '../services/apiService';

function UserList({ onlineUsers, currentUserId, onUserSelect }) {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchQuery, users, onlineUsers]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await apiService.listUsers();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length > 1) {
      try {
        const data = await apiService.searchUsers(query);
        setUsers(data.users || []);
      } catch (error) {
        console.error('Search failed:', error);
      }
    } else if (query.length === 0) {
      loadUsers();
    }
  };

  const filterUsers = () => {
    let filtered = users.filter((u) => u.user_id !== currentUserId);
    setFilteredUsers(filtered);
  };

  const isOnline = (userId) => onlineUsers.includes(userId);

  return (
    <div className="user-list">
      <div className="search-box">
        <input
          type="text"
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          disabled={loading}
        />
      </div>

      {loading && <p className="loading">Loading users...</p>}

      <div className="users">
        {filteredUsers.length === 0 ? (
          <p className="no-users">No users found</p>
        ) : (
          filteredUsers.map((user) => (
            <div
              key={user.user_id}
              className="user-item"
              onClick={() => onUserSelect(user)}
            >
              <div className="user-avatar">
                {user.username[0].toUpperCase()}
              </div>
              <div className="user-details">
                <div className="user-name">{user.username}</div>
                <div className="user-email">{user.email}</div>
              </div>
              {isOnline(user.user_id) && <div className="online-badge">●</div>}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default UserList;
