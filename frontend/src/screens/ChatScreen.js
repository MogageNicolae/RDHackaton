import React, {useState, useEffect, useContext, useRef} from 'react';
import { useNavigate } from 'react-router-dom';
import { Context } from '../contexts/Context';
import { styled } from '@mui/material/styles';
import { TextField, Button, Avatar, List, ListItem, ListItemAvatar, ListItemText } from '@mui/material';
import '../styles/chat-screen.css';
import {sendAudioMessageInChat} from "../services/ApiService";

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

  const {
    userToken, name, chatId, logout, createChat, chatRooms, getChatRooms, getChatMessages, chatHistory, sendMessage, searchedUsers, searchUsers, setSearchedUsers } = useContext(Context);

  useEffect(() => {
    const fetchAudioForMessages = async () => {
      setLoadingAudio(true);
      const audioPromises = localChatHistory.map(async (msg, index) => {
        console.log(msg)
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

  const handleUserSelect = async (selectedUser) => {
    const existingChat = chatRooms.find(room =>
      (room.user1 === name && room.user2 === selectedUser.username) ||
      (room.user2 === name && room.user1 === selectedUser.username)
    );

    if (existingChat) {
      handleChatSelect(existingChat.chat_id);
    } else {
      const newChatId = await createChat(selectedUser.username);
      if (newChatId) {
        handleChatSelect(newChatId);
        await getChatRooms();
      }
    }
    setSearchedUsers(null);
    setSearchTerm('');
  };

  const handleSendMessage = async () => {
    if (message.trim() !== '') {
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
                <ListItem key={user.username} button onClick={() => handleUserSelect(user)}>
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
              <AudioRecorder chat_id={chatId} sender={name} token={userToken} setLocalChatHistory={setLocalChatHistory}/>
              <CustomTextField
                  variant="outlined"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
                fullWidth
              />
              <Button variant="contained" color="primary" style={{minWidth: "75px"}} onClick={handleSendMessage}>
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

const AudioRecorder = ({chat_id, sender, token, setLocalChatHistory}) => {
  const [recordedUrl, setRecordedUrl] = useState('');
  const [recordedBlob, setRecordedBlob] = useState(null);
  const mediaStream = useRef(null);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const [recording, setRecording] = useState(false);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(
        { audio: true }
      );
      mediaStream.current = stream;
      mediaRecorder.current = new MediaRecorder(stream);
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.current.push(e.data);
        }
      };
      setRecording(true)
      mediaRecorder.current.onstop = () => {
        const newRecordedBlob = new Blob(
          chunks.current, { type: 'audio/webm' }
        );
        setRecordedBlob(newRecordedBlob);
        const url = URL.createObjectURL(newRecordedBlob);
        setRecordedUrl(url);
        chunks.current = [];
      };
      mediaRecorder.current.start();
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setRecording(false)
    }
  };

  const stopRecording = () => {
    setRecording(false)
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach((track) => {
        track.stop();
      });
    }
  };

  const sendAudio = async () => {
    try {
      const file = new File([recordedBlob], 'audio.webm', { type: 'audio/webm' });
      const fileName = await sendAudioMessageInChat(chat_id, sender, file, token);
      setLocalChatHistory(prevHistory => [
        ...prevHistory,
        { sender, message: fileName, type: 'audio' }
      ]);
    } catch (error) {
      console.error('Error sending audio message:', error);
    }
  }

  return (
    <div style={{maxWidth: "30%"}}>
      <audio controls src={recordedUrl}/>
      {recordedUrl ?
        <Button variant="contained" color="primary" style={{maxWidth: "50%", fontSize: "12px", marginRight:"10px"}}
                onClick={sendAudio}>
            Send Audio
        </Button>
        :
        <Button variant="contained" color="primary" style={{maxWidth: "50%", fontSize: "12px", marginRight:"10px"}}
                onClick={recording ? stopRecording : startRecording}>
          {recording ? 'Stop Recording' : 'Start Recording'}
        </Button>
      }

      <Button variant="contained" color="primary" style={{maxWidth: "50%", fontSize: "12px"}}
              disabled={!recordedUrl} onClick={() => {setRecordedUrl(''); setRecordedBlob(null)}}>
        Clear Recording
      </Button>
    </div>
  );
};

export default ChatScreen;