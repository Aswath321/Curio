import React, { useState } from 'react';
import { Mic } from 'lucide-react';  

const VoiceInput = ({ onInputChange }) => {
  const [isListening, setIsListening] = useState(false);

  const startListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        onInputChange(transcript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } else {
      alert('Speech recognition is not supported in your browser.');
    }
  };

  return (
    <button onClick={startListening} disabled={isListening} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '10px' }}>
      {isListening ? (
        <span style={{ fontSize: '18px' }}>Listening...</span>
      ) : (
        <Mic />  
      )}
    </button>
  );
};

export default VoiceInput;
