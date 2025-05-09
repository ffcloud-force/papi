import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Chat.css';

const Chat = () => {
  const [searchParams] = useSearchParams();
  const caseId = searchParams.get('caseId');
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [answerDiscussionId, setAnswerDiscussionId] = useState(null);
  const [topic, setTopic] = useState('');
  const [possibleTopics, setPossibleTopics] = useState([]);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [caseInfo, setCaseInfo] = useState(null);
  const [existingDiscussions, setExistingDiscussions] = useState([]);
  const messagesEndRef = useRef(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load case info when component mounts
  useEffect(() => {
    if (caseId) {
      fetchCaseInfo();
    } else {
      setError('No case ID provided. Please select a case from your dashboard.');
    }
  }, [caseId]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch case information
  const fetchCaseInfo = async () => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      // Fetch case details
      const response = await fetch(`${API_URL}/cases/get_case/${caseId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch case information');
      }
      
      const data = await response.json();
      setCaseInfo(data);
      
      // Check for existing discussions
      await checkExistingDiscussions();
      
    } catch (err) {
      console.error('Error fetching case info:', err);
      setError(err.message || 'Failed to load case information. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Check for existing discussions for this case
  const checkExistingDiscussions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/chat/case_discussions?case_id=${caseId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch case discussions');
      }
      
      const data = await response.json();
      setExistingDiscussions(data.discussions);
      
      // If there are existing discussions, load the most recent one
      if (data.discussions && data.discussions.length > 0) {
        const mostRecentDiscussion = data.discussions[0]; // Already sorted by last_message_at
        if (mostRecentDiscussion.answer_discussions && mostRecentDiscussion.answer_discussions.length > 0) {
          const mostRecentAnswerDiscussion = mostRecentDiscussion.answer_discussions[0];
          setAnswerDiscussionId(mostRecentAnswerDiscussion.id);
          await fetchChatHistory(mostRecentAnswerDiscussion.id);
          return true; // Discussions exist
        }
      }
      
      // If no discussions exist, fetch question sets
      await fetchQuestionSets();
      return false; // No discussions exist
      
    } catch (err) {
      console.error('Error checking for existing discussions:', err);
      // Continue to fetch question sets if there's an error
      await fetchQuestionSets();
      return false;
    }
  };
  
  // Fetch question sets to use as possible topics
  const fetchQuestionSets = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const questionsResponse = await fetch(`${API_URL}/cases/get_case_questions/${caseId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (questionsResponse.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (questionsResponse.ok) {
        const questionData = await questionsResponse.json();
        
        if (questionData.status === 'completed' && questionData.question_sets) {
          // Extract topics from question sets
          const topics = questionData.question_sets.map(set => set.topic);
          setPossibleTopics(['General', ...topics]);
          setShowTopicSelector(true);
        } else {
          // If questions are still processing or there was an error
          startCaseDiscussion(); // Start with general topic
        }
      } else {
        startCaseDiscussion(); // Start with general topic
      }
    } catch (err) {
      console.error('Error fetching question sets:', err);
      startCaseDiscussion(); // Start with general topic on error
    }
  };

  // Start a new case discussion with optional topic
  const startCaseDiscussion = async (topic = null) => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      // Send case_id and topic as query parameters
      const response = await fetch(`${API_URL}/chat/start_case_discussion?case_id=${caseId}${topic ? `&topic=${encodeURIComponent(topic)}` : ''}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to start case discussion');
      }
      
      const data = await response.json();
      setAnswerDiscussionId(data.answer_discussion_id);
      setMessages([{
        text: data.initial_message,
        sender: 'bot'
      }]);
      setShowTopicSelector(false);
    } catch (err) {
      console.error('Error starting case discussion:', err);
      setError(err.message || 'Failed to start case discussion. Please try again.');
    }
  };

  // Fetch chat history for a specific answer discussion
  const fetchChatHistory = async (discussionId) => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/chat/chat_history?answer_discussion_id=${discussionId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }
      
      const data = await response.json();
      
      // Convert the messages to the format used by the component
      const formattedMessages = data.messages.map(msg => ({
        id: msg.id,
        text: msg.content,
        sender: msg.role.toLowerCase() === 'user' ? 'user' : 'bot'
      }));
      
      setMessages(formattedMessages);
      setShowTopicSelector(false);
    } catch (err) {
      console.error('Error fetching chat history:', err);
      setError(err.message || 'Failed to load chat history.');
    } finally {
      setLoading(false);
    }
  };

  // Send a message
  const handleSend = async (e) => {
    e.preventDefault();
    if (input.trim() === '' || !answerDiscussionId) return;
    
    // Add user message to UI immediately
    const newMessage = { text: input, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, newMessage]);
    
    const currentInput = input;
    setInput(''); // Clear input field
    setLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          answer_discussion_id: answerDiscussionId,
          message_data: currentInput
        })
      });
      
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      const data = await response.json();
      
      // Add bot response to messages
      setMessages(prevMessages => [
        ...prevMessages, 
        { text: data.bot_response, sender: 'bot' }
      ]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message. Please try again.');
      // Show an error message in the chat
      setMessages(prevMessages => [
        ...prevMessages, 
        { text: 'Sorry, there was an error processing your request.', sender: 'bot' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Select topic and start discussion
  const handleTopicSelect = (selectedTopic) => {
    startCaseDiscussion(selectedTopic === 'General' ? null : selectedTopic);
  };

  // Render topic selector
  const renderTopicSelector = () => {
    return (
      <div className="topic-selector">
        <h2>Select a topic to discuss about this case</h2>
        <div className="topics-list">
          {possibleTopics.map((topicOption, index) => (
            <button
              key={index}
              className="topic-button"
              onClick={() => handleTopicSelect(topicOption)}
            >
              {topicOption}
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-container">
      <h1>Chat with PAPI</h1>
      {caseInfo && (
        <div className="case-info-banner">
          <h2>Case: {caseInfo.filename}</h2>
          {topic && <p className="chat-topic">Topic: {topic}</p>}
        </div>
      )}
      
      {error && <div className="error-message">{error}</div>}
      
      {loading && !answerDiscussionId ? (
        <div className="loading">Loading case information...</div>
      ) : showTopicSelector ? (
        renderTopicSelector()
      ) : (
        <>
          <div className="chat-messages">
            {loading && messages.length === 0 ? (
              <div className="loading">Loading conversation...</div>
            ) : messages.length === 0 ? (
              <div className="empty-chat">
                <p>No messages yet. Start a conversation!</p>
              </div>
            ) : (
              <>
                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.sender}`}>
                    {msg.text}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
            {loading && messages.length > 0 && (
              <div className="loading-indicator">Bot is typing...</div>
            )}
          </div>
          
          <form className="chat-input-form" onSubmit={handleSend}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message here..."
              className="chat-input"
              disabled={loading || !answerDiscussionId}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={loading || !answerDiscussionId}
            >
              Send
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default Chat;
