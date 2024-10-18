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
  const [localChatHistory, setLocalChatHistory] = useState([]);
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  const [audioUrls, setAudioUrls] = useState({});
  const [loadingAudio, setLoadingAudio] = useState(true);

  const { name, logout, createChat, chatRooms, getChatRooms, getChatMessages, chatHistory, sendMessage, searchedUsers, searchUsers, setSearchedUsers } = useContext(Context);

  useEffect(() => {
    const fetchAudioForMessages = async () => {
      setLoadingAudio(true);
      const audioPromises = localChatHistory.map(async (msg, index) => {
        if (msg.type === 'audio') {
          return { index, url: `http://localhost:5000/assets/audio/${selectedChat}/${name}/${msg.message}` };
        }
        return { index, url: null };
      });

      const results = await Promise.all(audioPromises);
      const updatedAudioUrls = results.reduce((acc, { index, url }) => {
        if (url) {
          acc[index] = url;
        }
        return acc;
      }, {});

      setAudioUrls((prev) => ({ ...prev, ...updatedAudioUrls }));
    };

    fetchAudioForMessages();
  }, [localChatHistory]);

  useEffect(() => {
      setLoadingAudio(false);
    }, [audioUrls]);

  useEffect(() => {
    async function getChats() {
      await getChatRooms();
    }
    getChats();
  }, []);

  useEffect(() => {
    if (selectedChat && chatHistory) {
      setLocalChatHistory(chatHistory);
    }
  }, [chatHistory, selectedChat]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 400);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  useEffect( () => {
    async function search() {
        if (debouncedSearchTerm) {
            await searchUsers(searchTerm);
        } else {
            setSearchedUsers(null);
        }
    }
    search();
  }, [debouncedSearchTerm]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleChatSelect = async (chatId) => {
    setSelectedChat(chatId);
    await getChatMessages(chatId);
  };

  const handleSendMessage = async () => {
    if (message.trim() !== '') {
      console.log('Sending message:', message);
      await sendMessage(message);

      setLocalChatHistory(prevHistory => [
        ...prevHistory,
        { sender: name, message }
      ]);

      setMessage('');
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
          onChange={(e) => setSearchTerm(e.target.value)}
          fullWidth
          className="search-box"
        />
        <List className="chat-list">
          {searchedUsers ? (
            searchedUsers
              .filter(user => user.username !== name)  
              .map((user) => (
                <ListItem key={user.username}>
                  <ListItemAvatar>
                    <Avatar>{user.username[0]}</Avatar>
                  </ListItemAvatar>
                  <ListItemText primary={user.username} />
                </ListItem>
              ))
          ) : (
            chatRooms?.map((room) => (
              <ListItem key={room.chat_id} button onClick={() => handleChatSelect(room.chat_id)}>
                <ListItemAvatar>
                  <Avatar>{room.user1 === name ? room.user2[0] : room.user1[0]}</Avatar>
                </ListItemAvatar>
                <ListItemText primary={room.user1 === name ? room.user2 : room.user1} />
              </ListItem>
            ))
          )}
        </List>
      </div>

      <div className="chat-section">
        {selectedChat ? (
          <>
            <ul className="message-list">
              {localChatHistory.map((msg, index) => (
                <li key={index} className={msg.sender === name ? 'sent' : 'received'}>
                  <strong>{msg.sender}</strong>
                  {msg.type === 'text' ? (
                    <p>{msg.message}</p>
                  ) : msg.type === 'audio' ? (
                      <>
                        {loadingAudio ? (
                          <p>Loading audio...</p>
                        ) : (
                          <>
                            <br />
                            <audio controls>
                              <source src={audioUrls[index]} type="audio/wav" />
                              Your browser does not support the audio tag.
                            </audio>
                            </>
                        )}
                      </>
                      ) : null}

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
    </div >
  );
};

export default ChatScreen;
