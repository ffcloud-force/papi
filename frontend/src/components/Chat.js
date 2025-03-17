import React, { useState } from 'react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() === '') return;
    
    // Get user id from local storage
    const user_id = localStorage.getItem('user_id');
    console.log("user_id from localStorage:", user_id);

    // Add user message
    const newMessages = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');
    
    // call the chat endpoint
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    fetch(`${API_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: input,
        // TODO: get user_id from local storage
        user_id: "123"
      }),
    })
    .then(response => response.json())
    .then(data => setMessages([...newMessages, { text: data.message, sender: 'bot' }]))
    .catch(error => {
      console.error('Error:', error);
      setMessages([...newMessages, { text: 'Sorry, there was an error processing your request.', sender: 'bot' }]);
    });
  };

  return (
    <div className="chat-container">
      <h1>Chat with PAPI</h1>
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>No messages yet. Start a conversation!</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))
        )}
      </div>
      <form className="chat-input-form" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message here..."
          className="chat-input"
        />
        <button type="submit" className="send-button">Send</button>
      </form>
    </div>
  );
};

export default Chat;
