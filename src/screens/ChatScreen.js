import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Context } from '../contexts/Context';
import { styled } from '@mui/material/styles';
import { TextField, Button, Avatar, List, ListItem, ListItemAvatar, ListItemText } from '@mui/material';
import '../styles/chat-screen.css';

const CustomTextField = styled(TextField)({
  '& label.Mui-focused': {
    color: '#000',
  },
  '& .MuiInput-underline:after': {
    borderBottomColor: '#000',
  }
});

const ChatScreen = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedChat, setSelectedChat] = useState(null);
  const [message, setMessage] = useState('');
  const [localChatHistory, setLocalChatHistory] = useState([]); // Local state to store chat messages

  const { name, logout, createChat, chatRooms, getChatRooms, getChatMessages, chatHistory, sendMessage } = useContext(Context);

  useEffect(() => {
    async function getChats() {
      await getChatRooms();
    }
    getChats();
    console.log("chat rooms: ", chatRooms);
  }, [getChatRooms, chatRooms]);

  useEffect(() => {
    // Sync chatHistory from context with local state when selected chat changes
    if (selectedChat && chatHistory) {
      setLocalChatHistory(chatHistory);
    }
  }, [chatHistory, selectedChat]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    // Add search logic here
  };

  const handleChatSelect = async (chatId) => {
    setSelectedChat(chatId);
    await getChatMessages(chatId); // Fetch messages for the selected chat
  };

  const handleSendMessage = async () => {
    if (message.trim() !== '') {
      console.log('Sending message:', message);
      await sendMessage(selectedChat, message); // Send message to backend

      // Optimistically update chat messages in the local state
      setLocalChatHistory(prevHistory => [
        ...prevHistory, 
        { sender: name, message } // Append new message
      ]);

      setMessage(''); // Clear message input
    }
  };

  return (
    <div className="chat-screen-container">
      <div className="menu-section">
        <Avatar className="avatar">{name ? name[0] : ''}</Avatar>
        <h2>{name}</h2>
        <Button variant="contained" background-color="black" onClick={handleLogout}>Logout</Button>
      </div>
      
      <div className="chats-section">
        <CustomTextField
          variant="outlined"
          label="Search users..."
          value={searchTerm}
          onChange={handleSearch}
          fullWidth
          className="search-box"
        />
        <List className="chat-list">
          {chatRooms?.map((room) => (
            <ListItem key={room.chat_id} button onClick={() => handleChatSelect(room.chat_id)}>
              <ListItemAvatar>
                <Avatar>{room.user1 === name ? room.user2[0] : room.user1[0]}</Avatar>
              </ListItemAvatar>
              <ListItemText primary={room.user1 === name ? room.user2 : room.user1} />
            </ListItem>
          ))}
        </List>
      </div>
      
      <div className="chat-section">
        {selectedChat ? (
          <>
            <ul className="message-list">
              {localChatHistory.map((msg, index) => (
                <li key={index} className={msg.sender === name ? 'sent' : 'received'}>
                  <strong>{msg.sender}</strong>
                  <p>{msg.message}</p>
                </li>
              ))}
            </ul>
            <div className="message-input">
              <CustomTextField
                variant="outlined"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
                fullWidth
              />
              <Button variant="contained" color="primary" onClick={handleSendMessage}>
                Send
              </Button>
            </div>
          </>
        ) : (
          <p className="no-chat-selected">Select a chat to start messaging</p>
        )}
      </div>
    </div>
  );
};

export default ChatScreen;
