import React, { createContext, useState, useEffect } from "react";
import { registerUser, loginUser, createChatRoom, chatMessages, getAllChatRooms, sendMessageInChat, searchForUsers } from "../services/ApiService";
import { responsiveFontSizes } from "@mui/material";

export const Context = createContext();

const ContextProvider = ({ children }) => {
  const [userToken, setUserToken] = useState(() => localStorage.getItem('token'));
  const [userId, setUserId] = useState(() => localStorage.getItem('userId'));
  const [name, setName] = useState(() => localStorage.getItem('name'));
  const [chatId, setChatId] = useState(null);
  const [chatHistory, setChatHistory] = useState(null);
  const [chatRooms, setChatRooms] = useState(null);
  const [searchedUsers, setSearchedUsers] = useState(null);

  const register = async (name, email, language, password) => {
    try {
      await registerUser({ name, email, language, password });
      const loginData = { email, password };
      await login(loginData);
    } catch (error) {
      console.error("Error registering user:", error);
      throw error;
    }
  };

  const login = async (credentials) => {
    try {
      console.log("Login started with credentials:", credentials);
      const response = await loginUser(credentials);
      const token = response.token;
      const userId = response.user_id;
      const name = response.username;
      localStorage.setItem('token', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('name', name);
      setUserToken(token);
      setUserId(userId);
      setName(name);
      console.log("Login successful with token: ", token, " and id: ", userId, "and name: ", name);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('name');
    setUserToken(null);
    setUserId(null);
    setName(null);
    setChatId(null);
    setChatHistory(null);
    setChatRooms(null);
    setSearchedUsers(null);
    console.log("logged out");
  };

  const createChat = async (user2) => {
    try {
      console.log("creating chat room..")
      const response = await createChatRoom({ name, user2 }, userToken);
      console.log("successful, the chat id is: ", response);
      setChatId(response);
    } catch (error) {
      console.error("Error creating chat:", error);
      throw error;
    }
  }

  const sendMessage = async (message) => {
    try {
      console.log("sending the message: ", message)
      const response = await sendMessageInChat({ chat_id: chatId, sender: name, message }, userToken);
      console.log("successfully sent the message, response: ", response);
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  }

  const getChatMessages = async (chat_id) => {
    try {
      console.log("getting chat history..");
      const response = await chatMessages(chat_id, userToken, name);
      setChatId(chat_id);
      setChatHistory(response);
      console.log("successfully gotten the chat history: ", response);
    } catch (error) {
      console.error("Error getting chat history:", error);
      throw error;
    }
  }

  const getChatRooms = async () => {
    try {
      console.log("getting chat rooms..");
      const response = await getAllChatRooms(name, userToken);
      setChatRooms(response);
      console.log("successfully gotten the chat rooms: ", response);
    } catch (error) {
      console.error("Error getting chat rooms:", error);
      throw error;
    }
  }

  const searchUsers = async (name) => {
    try {
      console.log("searching for users with name: ", name);
      const response = await searchForUsers(name);
      setSearchedUsers(response);
      console.log("successfully searched for users: ", response);
    } catch (error) {
      console.error("Error searching for users:", error);
      throw error;
    }
  }

  return (
    <Context.Provider value={{ userToken, userId, name, chatId, chatHistory, chatRooms, searchedUsers, setSearchedUsers, searchUsers, sendMessage, getChatRooms, getChatMessages, createChat, register, login, logout }}>
      {children}
    </Context.Provider>
  );
};

export default ContextProvider;