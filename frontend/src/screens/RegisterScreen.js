import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Context } from '../contexts/Context';
import { Link } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import loginImg from '../assets/loginImg.jpg'
import '../styles/register-screen.css'

const CustomTextField = styled(TextField)({
    '& label.Mui-focused': {
        color: '#000',
    },
    '& .MuiInput-underline:after': {
        borderBottomColor: '#000',
    }
});

const RegisterScreen = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [language, setLanguage] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const { register } = useContext(Context);
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            await register(name, email, language, password);
            navigate('/chatscreen');
            setError('');
        } catch (error) {
            if (error.message.includes("User with the same email or name already exists!")) {
                setError("A user with the same email or name already exists!");
            } else {
                setError("Registration failed. Please check all the fields and try again.");
            }
        }
    };

    return (
        <div className="register-body">
            <div className="form-container">
                <h1 className="title">Register here</h1>
                <div className="input-container">
                    <CustomTextField
                        className="input"
                        variant='standard'
                        label="Username "
                        value={name}
                        onChange={e => setName(e.target.value)}
                        required
                    />
                </div>
                <div className="input-container">
                    <CustomTextField
                        className="input"
                        variant='standard'
                        label="Email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        type="email"
                        required
                    />
                </div>
                <div className="input-container">
                    <CustomTextField
                        className="input"
                        variant='standard'
                        label="Language"
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                        type="language"
                        required
                    />
                </div>
                <div className="input-container">
                    <CustomTextField
                        className="input"
                        variant='standard'
                        label="Password"
                        onChange={e => setPassword(e.target.value)}
                        value={password}
                        type="password"
                        required
                    />
                </div>
                <Button className="button" variant="contained" onClick={handleRegister}>Register</Button>
                {error && <div className="error-message">{error}</div>}
                <div className="register-container">
                    Already have an account? <Link to="/" className="link">Login here</Link>
                </div>
            </div>
            <div className="image-container">
                <img src={loginImg} alt="loginImg"/>
                <div className="image-overlay"></div>
            </div>
        </div>
    );
};

export default RegisterScreen;