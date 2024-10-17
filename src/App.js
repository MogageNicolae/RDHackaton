import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ContextProvider from './contexts/Context';
import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import ChatScreen from './screens/ChatScreen';

function App() {
  return (
    <ContextProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LoginScreen/>} />
          <Route path="/chatscreen" element={<ChatScreen/>} />
          <Route path="/registerscreen" element={<RegisterScreen/>} />
        </Routes>
      </Router>
    </ContextProvider>
  );
}

export default App;