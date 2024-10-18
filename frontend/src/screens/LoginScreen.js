import React, { useContext, useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { Context } from '../contexts/Context';
import { Link } from 'react-router-dom';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import loginImg from '../assets/loginImg.jpg'
import '../styles/login-screen.css';

const CustomTextField = styled(TextField)({
  '& label.Mui-focused': {
    color: '#000',
  },
  '& .MuiInput-underline:after': {
    borderBottomColor: '#000',
  }
});

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(Context);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      console.log(email, password);
      await login({ email, password });
      setError('');  
      navigate('/chatscreen');
    } catch (error) {
      setError("Login failed. Please check your email and password and try again.");
    }
  };  
  
  return (
    <div className='loginContainer'>
      <div className='formContainer'>
        <h2>Welcome</h2>
        <div className='inputContainer'>
          <PersonIcon className='icon'></PersonIcon>
          <CustomTextField className='input' variant='standard' label='Email' value={email} onChange={(event) => setEmail(event.target.value)} />
        </div>
        <div className='inputContainer'>
          <LockIcon className='icon'></LockIcon>
          <CustomTextField className='input' variant='standard' label='Password' type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </div>
        <Button className='button' variant="contained" onClick={handleLogin}>Login</Button>
        {error && <div className='errorMessage'>{error}</div>}
        <div className='registerContainer'>
          Don't have an account yet?
          <Link to="/registerscreen" className='link'>Register here</Link>
        </div>
      </div>
      <div className='imageContainer'>
        <img src={loginImg} alt="loginImg"  />
        <div className='imageOverlay'></div>
      </div>


    </div>
  );
};

export default LoginScreen;