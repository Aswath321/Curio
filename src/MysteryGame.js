import React, { useState, useEffect, useRef } from 'react';
import { SendHorizontal } from 'lucide-react';
import './MysteryGame.css';
import axios from 'axios';

const MysteryGame = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [gameOver, setGameOver] = useState(false);
  const [error, setError] = useState(null);
  const [caseInfo, setCaseInfo] = useState({
    title: '',
    description: '',
    crimeScene: '',
    suspects: []
  });
  
  const messageListRef = useRef(null);

  useEffect(() => {
    startGame();
  }, []);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const startGame = async () => { 
    try {
      const response = await axios.post('http://localhost:8000/api/mystery-game/start');
      const introMessage = response.data.message;
      setMessages([{ type: 'curio', content: introMessage }]);
      
      // Extract case info from the intro message
      const titleMatch = introMessage.match(/We have a new case: (.+)/);
      const descriptionMatch = introMessage.match(/We have a new case: .+\n(.+)/);
      
      if (titleMatch && descriptionMatch) {
        setCaseInfo(prevInfo => ({
          ...prevInfo,
          title: titleMatch[1],
          description: descriptionMatch[1]
        }));
      }
      
      setGameOver(false);
      setError(null);
    } catch (error) {
      console.error('Error starting the game:', error);
      setError('Failed to start the game. Please try again.');
    }
  };

  const sendInput = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/mystery-game/input', { input: userInput });
      setMessages(prevMessages => [
        ...prevMessages,
        { type: 'user', content: userInput },
        { type: 'curio', content: response.data.message }
      ]);
      setUserInput('');
      setGameOver(response.data.game_over);
      
      // Update case info if new details are provided
      const crimeSceneMatch = response.data.message.match(/Crime Scene Details:\s*(.+?)(?=\n\n|\n[A-Z]|$)/s);
      if (crimeSceneMatch) {
        setCaseInfo(prevInfo => ({
          ...prevInfo,
          crimeScene: crimeSceneMatch[1].trim()
        }));
      }
      
      const suspectsMatch = response.data.message.match(/Suspects:\s*(.+?)(?=\n\n|\n[A-Z]|$)/s);
      if (suspectsMatch) {
        const suspectsList = suspectsMatch[1].split('\n').map(suspect => {
          const [fullName, designation] = suspect.split(':').map(s => s.trim());
          const [name] = fullName.split(',');
          return { name, designation };
        }).filter(suspect => suspect.name && suspect.designation);
        
        setCaseInfo(prevInfo => ({
          ...prevInfo,
          suspects: suspectsList
        }));
      }
      
      setError(null);
    } catch (error) {
      console.error('Error sending input:', error);
      setError('Failed to process your input. Please try again.');
    }
  };

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (userInput.trim() !== '') {
      sendInput();
    }
  };

  return (
    <div className="mg-game-container">
      
      <div className="mg-chat-area">
      <h1 className="mg-case-title">Solve the {caseInfo.title} mystery!</h1>
        <div className="mg-chat-content">
          {error && <div className="mg-error-message">{error}</div>}
          <div ref={messageListRef} className="mg-message-list">
            {messages.map((message, index) => (
              <div key={index} className={`mg-message mg-message-${message.type}`}>
                {message.content}
              </div>
            ))}
          </div>
          {!gameOver ? (
            <form onSubmit={handleSubmit} className="mg-input-form">
              <input
                type="text"
                value={userInput}
                onChange={handleInputChange}
                className="mg-input-field"
                placeholder="Enter your response..."
              />
              <button type="submit" className="mg-send-button">
                <SendHorizontal size={24} />
              </button>
            </form>
          ) : (
            <button onClick={startGame} className="mg-play-again">
              Play Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
  
};

export default MysteryGame;