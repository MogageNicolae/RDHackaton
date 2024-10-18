const baseURL = 'http://localhost:5000';

export const registerUser = async (userData) => {
    try {
        console.log(JSON.stringify(userData));
        const response = await fetch(`${baseURL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        if (!response.ok) {
            const errorBody = await response.json();
            if(errorBody.username == "A user with that username already exists." || errorBody.email == "user with this email already exists.") {
                throw new Error("User with the same email or username already exists!");
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Registering user failed: ", error);
        throw error;
    }
};

export const loginUser = async (credentials) => {
    try {
        console.log("service loging, see credentials: ", credentials);
        const response = await fetch(`${baseURL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Login failed: ", error);
        throw error;
    }
};

export const createChatRoom = async (users, token) => {
    try {
        console.log(JSON.stringify(users));
        console.log("creating chatroom with users: ", JSON.stringify(users));
        console.log("creating chatroom with token: ", token);
        const response = await fetch(`${baseURL}/chat/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(users)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Creating chat failed: ", error);
        throw error;
    }
} 

export const sendMessageInChat = async (messageData, token) => {
    try {
        console.log("sending message in chatroom: ", messageData);
        const response = await fetch(`${baseURL}/chat/send_message/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(messageData)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response;
    } catch (error) {
        console.error("Sending message failed: ", error);
        throw error;
    }
}

export const sendAudioMessageInChat = async (chatId, senderName, audioFile, token) => {
    try {
        console.log("sending audio message in chatroom: ", chatId);
        const formData = new FormData();
        formData.append('file', audioFile, 'audio.webm');
        formData.append('chat_id', chatId);
        formData.append('sender', senderName);
        const response = await fetch(`${baseURL}/chat/send_message/audio`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Sending audio message failed: ", error);
        throw error;
    }
}

export const chatMessages = async (chatId, token, sender) => {
    try {
        console.log("getting chat messages from chat: ", chatId);
        const response = await fetch(`${baseURL}/chat/${chatId}?sender=${sender}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Getting chat messages failed: ", error);
        throw error;
    }
} 

export const getAllChatRooms = async (name, token) => {
    try {
        console.log("getting chat rooms for user with name: ", name);
        const response = await fetch(`${baseURL}/chat/history?username=${encodeURIComponent(name)}`,{
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        } );
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Getting chat rooms failed: ", error);
        throw error;
    }
}

export const searchForUsers = async (name) => {
    try {
        console.log("searching for users with name: ", name);
        const response = await fetch(`${baseURL}/user/${encodeURIComponent(name)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Searching for users failed: ", error);
        throw error;
    }
}
