import React, { useState } from 'react';
import { Mic } from 'lucide-react';
import './LiveChat.css'

const VoiceControl = () => {
    const [isActive, setIsActive] = useState(false);

    // Handle voice toggle with immediate state update
    const handleVoiceToggle = async () => {
        // First update the state to ensure UI responsiveness
        const newState = !isActive;
        setIsActive(newState);

        const endpoint = newState ? '/start-voice' : '/stop-voice';  // Reversed logic to match state

        try {
            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                // If the request fails, revert the state
                setIsActive(!newState);
                throw new Error(`Failed to ${newState ? 'start' : 'stop'} voice`);
            }

            const data = await response.json();
            console.log(data.message);
        } catch (error) {
            console.error('Error:', error);
            // Optionally show an error message to the user here
        }
    };

    return (
        <div className="voice-control-container">
            <div className="voice-control-content">
                <button
                    onClick={handleVoiceToggle}
                    className={`voice-control-mic-btn ${isActive ? 'mic-active' : ''}`}
                    aria-label="Toggle voice"
                    aria-pressed={isActive}
                >
                    <Mic className={`voice-control-mic-icon ${isActive ? 'mic-on' : 'mic-off'}`} />
                </button>
                <div className="voice-control-status">
                    <span>{isActive ? 'Tap to interrupt' : 'Tap to speak'}</span>
                </div>
            </div>

            {isActive && (
                <div className="voice-visualization">
                    <div className="voice-circle circle-1"></div>
                    <div className="voice-circle circle-2"></div>
                    <div className="voice-circle circle-3"></div>
                </div>
            )}
        </div>
    );
};

export default VoiceControl;