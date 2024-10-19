import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faVolumeUp, faWaveSquare } from '@fortawesome/free-solid-svg-icons';

const TextToSpeech = ({ text, isPlaying, onTogglePlay }) => {

  const handlePlay = () => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => {
      onTogglePlay(false); 
    };
    speechSynthesis.speak(utterance);
    onTogglePlay(true); 
  };

  const handleStop = () => {
    speechSynthesis.cancel();
    onTogglePlay(false); 
  };

  return (
    <button
      onClick={isPlaying ? handleStop : handlePlay}
      style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '10px' }}
    >
      {isPlaying ? (
        <FontAwesomeIcon icon={faWaveSquare}  size="1.6x" color="black" />
      ) : (
        <FontAwesomeIcon icon={faVolumeUp}  size="1.6x" color="black" />
      )}
    </button>
  );
};

export default TextToSpeech;
