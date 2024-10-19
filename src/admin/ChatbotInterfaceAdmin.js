import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import VoiceInput from '../VoiceInput';
import TextToSpeech from '../TextToSpeech';
import ReactMarkdown from 'react-markdown';
import CryptoJS from 'crypto-js';
import { PlusCircle, Users, RefreshCw, LogOut, Paperclip, Speech,Puzzle,StickyNote, SendHorizontal, Search,Linkedin } from 'lucide-react';
import WelcomeSection from '../WelcomeSection';
import '../FlashCard.css';
import StudentProjectDashboard from '../StudentProjectDashboard';
import BeatLoader from "react-spinners/BeatLoader";



const WS_URL = 'ws://127.0.0.1:8000/ws';



const ChatbotInterface = () => {
    const { user, logout } = useAuth();
    const [fileRagMode, setFileRagMode] = useState(false);
    const navigate = useNavigate();
    const [isClosing, setIsClosing] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showInfoBox, setShowInfoBox] = useState(false);
    const [chats, setChats] = useState([]);
    const [currentChat, setCurrentChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [playingStates, setPlayingStates] = useState({});
    const socketRef = useRef(null);
    const [token, setToken] = useState(null);
    const [llmType, setLlmType] = useState('api');
    const [pdfRagMode, setPdfRagMode] = useState(false);
    const [pdfFiles, setPdfFiles] = useState([]);
    const [pdfRagReady, setPdfRagReady] = useState(false);
    const [flashCardMode, setFlashCardMode] = useState(false);
    const [flashCardReady, setFlashCardReady] = useState(false);
    const [flashcards, setFlashcards] = useState([]);
    const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
    const [showAnswer, setShowAnswer] = useState(false);
    const [isFlashcardChat, setIsFlashcardChat] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [showSearchResults, setShowSearchResults] = useState(false);
    const modalRef = useRef(null);
    const [showWelcome, setShowWelcome] = useState(true);
    const [studentId,setStudentId] = useState('');
    const [playingMessageId, setPlayingMessageId] = useState(null);
    const [isLinkedInSession, setIsLinkedInSession] = useState(false);
    const [files, setFiles] = useState([]);
    const [ragReady, setRagReady] = useState(false);
    const [s3Files, setS3Files] = useState([]);
    const [selectedS3Files, setSelectedS3Files] = useState([]);
    const [showFileSection, setShowFileSection] = useState(false);

  useEffect(() => {
    if (user && token) {
      connectWebSocket();
    }
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [user, token]);

  useEffect(() => {
    if (user) {
      user.getIdToken().then(setToken);
    }
  }, [user]);



  const encryptMessage = (message, secretKey) => {
    return CryptoJS.AES.encrypt(message, secretKey).toString();
};

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);


  useEffect(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      createNewChat();
    }
  }, [socketRef.current]);

  useEffect(() => {
    // Function to detect clicks outside the modal
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        setIsClosing(true);
        setTimeout(() => setShowInfoBox(false), 300); 
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [modalRef]);
  
  const handleWelcomeVisibility = (messages, flashcardMode, pdfMode) => {
    if (messages.length > 0 || flashCardMode || pdfRagMode) {
      setShowWelcome(false);
    }
  };
  // Call handleWelcomeVisibility function when relevant state changes
  useEffect(() => {
    handleWelcomeVisibility(messages, flashCardMode, fileRagMode);
  }, [messages, flashCardMode, fileRagMode]);
  

  const connectWebSocket = () => {
    setLoading(true);
    const clientId = Math.random().toString(36).substring(7);
    socketRef.current = new WebSocket(`${WS_URL}/${clientId}`);

    socketRef.current.onopen = () => {
      console.log('WebSocket connection established');
      fetchChats();
      createNewChat();
      setLoading(false);
    };

    socketRef.current.onmessage = (event) => {
      if (!event.data) {
        console.error('Received empty message');
        return;
      }

      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error, event.data);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setLoading(false); 
    };

    socketRef.current.onclose = () => {
      console.log('WebSocket connection closed');
      setLoading(false); 
    };
  };

  const handleSearch = async () => {
    if (searchQuery.trim() === '') {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/search_chats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
        setShowSearchResults(true);
      } else {
        console.error('Error searching chats');
      }
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };


  const handleSearchResultClick = (chatId) => {
    setCurrentChat(chatId);
    fetchMessages(chatId);
    setShowSearchResults(false);
    setSearchQuery('');
  };

const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error("Error logging out:", error.message);
    }
  };


  const handlePdfRagClick = () => {
    setFileRagMode(true);
    setRagReady(false);
    setPdfFiles([]);
    setCurrentChat(null);
    setMessages([]);
    setFlashCardMode(false);
    setShowFileSection(false);
  };

  const handleFlashCards=()=>{
    setFlashCardMode(true);
    setFlashCardReady(false);
    setPdfFiles([]);
    setCurrentChat(null);
    setMessages([]); 
    setShowInfoBox(false);
    setFileRagMode(false);
  }

  const selectChat = (chatId) => {
    setCurrentChat(chatId);
    fetchMessages(chatId);
    setPdfRagMode(false);
    setFlashCardMode(false);
  };

  const handleFileUpload = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(prevFiles => [...prevFiles, ...selectedFiles]);
  };



  const handlePdfRagSubmit = async () => {
    if (selectedS3Files.length === 0 && files.length === 0) {
      alert("Please upload at least one file or select from S3.");
      return;
    }
    
    setLoading(true);
    const formData = new FormData();

        // Add locally uploaded files
        files.forEach((file) => {
          formData.append('local_files', file);
        });

        // Add selected S3 files
        selectedS3Files.forEach((file) => {
          formData.append('s3_files', JSON.stringify({ name: file.name, url: file.url }));
        });

        formData.append('llm_type', 'api');

        try {
          const response = await fetch('http://localhost:8000/upload_files', {
            method: 'POST',
            body: formData,
          });

  
      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          setRagReady(true);
          setLoading(false);
          alert("Files processed successfully. You can now ask questions.");
        } else {
          setLoading(false);
          alert("Error processing files. Please try again.");
        }
      } else {
        setLoading(false);
        alert("Error uploading files. Please try again.");
      }
    } catch (error) {
      setLoading(false);
      console.error('Error:', error);
      alert("An error occurred. Please try again.");
    }
  };
  const getFileButtonColor = (fileType) => {
    switch(fileType.toLowerCase()) {
        case 'pdf':
            return 'bg-red-500';
        case 'docx':
            return 'bg-blue-500';
        case 'csv':
            return 'bg-green-500';
        default:
            return 'bg-gray-500';
    }
};
const fetchS3Files = async () => {
  setLoading(true);
  try {
    const response = await fetch('http://localhost:8000/list_s3_files');
    if (response.ok) {
      const data = await response.json();
      setShowFileSection(true);
      setS3Files(data.files);

     } else {
      console.error('Failed to fetch S3 files');
    }setLoading(false);
  } catch (error) {
    console.error('Error fetching S3 files:', error);
  }
};

const handleS3FileSelect = async (fileKey) => {
  try {
    const response = await fetch('http://localhost:8000/get_s3_file_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_key: fileKey }),
    });
    if (response.ok) {
      const data = await response.json();
      const fileUrl = data.url;
      const fileName = fileKey.split('/').pop();
      setSelectedS3Files(prev => [...prev, { name: fileName, url: fileUrl }]);
    } else {
      console.error('Failed to get S3 file URL');
    }
  } catch (error) {
    console.error('Error selecting S3 file:', error);
  }
};

  const handleFlashCardSubmit = async () => {
    if (pdfFiles.length === 0) {
      alert("Please upload at least one PDF file.");
      return;
    }
    const formData = new FormData();
    pdfFiles.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('user_id',user);
    try {
      const response = await fetch('http://localhost:8000/upload_pdfs_flashcard', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          setFlashCardReady(true);
          setCurrentChat(result.chat_id);
          fetchMessages(result.chat_id);
          setChats(prevChats => [...prevChats, { id: result.chat_id, llm_type: llmType }]);
          alert("PDFs processed successfully. Flashcards are ready.");
        } else {
          alert("Error processing PDFs. Please try again.");
        }
      } else {
        alert("Error uploading PDFs. Please try again.");
      }
    } catch (error) {
      console.error('Error:', error);
      alert("An error occurred. Please try again.");
    }
  };


  const handleBotResponse = (botResponse) => {
    try {
        // Log the bot response
        console.log(botResponse);

        // Match the student ID pattern (e.g., ST123)
        const studentIdMatch = botResponse.text.match(/ST\d+/);
        console.log("STUDENT MATCH", studentIdMatch, "Match");

        // Extract the student ID if a match is found
        const student_id = studentIdMatch ? studentIdMatch[0] : null;
        // Log the extracted student ID
        console.log("Extracted Student ID:", student_id);
        
        // Update the student ID state
        setStudentId(student_id);
        
        // Check if the message contains a valid student ID
        const isStudentDashboard = !!student_id; // Use extracted student_id instead of studentId

        // Update the messages state
        setMessages((prevMessages) => [
            ...prevMessages,
            {
                id: botResponse.id,
                text: botResponse.text,
                sender: botResponse.sender,
                isStudentDashboard: isStudentDashboard,
                studentId: student_id // Use extracted student_id here
            }
        ]);
    } catch (error) {
        console.error('Error handling bot response:', error);
        setMessages((prevMessages) => [
            ...prevMessages,
            {
                text: "Error processing message",
                sender: 'bot',
                isStudentDashboard: false
            }
        ]);
    }
};


  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'chat':
        if (data.chat.is_flashcard) {
          setIsFlashcardChat(true);
          setFlashcards(data.chat.flashcards);
          setCurrentFlashcardIndex(0);
          setShowAnswer(false);
          setChats(prevChats => {
            if (!prevChats.some(chat => chat.id === data.chat.chat_id)) {
              return [...prevChats, { id: data.chat.chat_id, llm_type: llmType }];
            }
            return prevChats;
          });
        } else {
          setIsFlashcardChat(false);
          const messages = JSON.parse(data.chat.messages);
          const processedMessages = messages.map(message => {
            if (message.sender === 'bot') {
              // Extract student ID using the same pattern as handleBotResponse
              const studentIdMatch = message.text.match(/ST\d+/);
              console.log("Student ID Match:", studentIdMatch); // Debug log
              if (studentIdMatch) {
                return {
                  id: message.id,
                  text: message.text,
                  sender: message.sender,
                  isStudentDashboard: true,
                  studentId: studentIdMatch[0]
                };
              }
            }
            // Return unmodified message if not a bot message or no student ID
            return {
              id: message.id,
              text: message.text,
              sender: message.sender,
              isStudentDashboard: false
            };
          });
          setMessages(processedMessages);
        }
        break;
      case 'message_added':
        if (data.response.status === 'success' && data.response.bot_response) {
          handleBotResponse(data.response.bot_response);
        }
        break;
      case 'chats_list':
        setChats(data.chats.filter(chat => chat.llm_type === llmType));
        break;
      case 'chat_created':
        setChats((prevChats) => [...prevChats, { id: data.chat_id, llm_type: llmType }]);
        setCurrentChat(data.chat_id);
        setMessages([]);
        setShowWelcome(true);
        break;
      default:
        console.warn('Unhandled message type:', data.type);
    }
  };
  const startLinkedInSession = async () => {
    try {
        // Call the backend FastAPI endpoint
        window.open('http://127.0.0.1:5000/', '_blank');
        // const response = await fetch('http://localhost:8000/start_group_chat', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify({ /* Add any necessary payload here */ }),
        // });

            // If the request was successful, open a new tab
        

    } catch (error) {
        console.error('Error starting group chat:', error);
    }
};

  const sendWebSocketMessage = (type, payload) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, token, llm_type: llmType,role :'admin', ...payload });
      console.log('Sending WebSocket message:', message);
      socketRef.current.send(message);
    } else {
      console.error('WebSocket is not connected');
    }
  };


  const fetchChats = () => {
    sendWebSocketMessage('get_chats');
  };

  const fetchMessages = (chatId) => {
    sendWebSocketMessage('get_chat', { chat_id: chatId });
  };

  const createNewChat = () => {
    sendWebSocketMessage('create_chat');
    setFileRagMode(false);
    setFlashCardMode(false);
    setShowWelcome(true);
    setMessages([]);
    setCurrentChat(null);
    setShowFileSection(false);
  };

  const startGroupChat = async () => {
    try {
        // Call the backend FastAPI endpoint
        window.open('http://127.0.0.1:5000/', '_blank');
        // const response = await fetch('http://localhost:8000/start_group_chat', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify({ /* Add any necessary payload here */ }),
        // });

            // If the request was successful, open a new tab
        

    } catch (error) {
        console.error('Error starting group chat:', error);
    }
};

  

const StructuredOutput = ({ output, isStudentDashboard, studentId }) => {
  if (isStudentDashboard) {
    return (
      <div className="height-80px width-100px">
        <StudentProjectDashboard studentID={studentId} />
      </div>
    );
  }
  
  // For non-dashboard messages, render as markdown
  const displayText = typeof output === 'string' ? output : String(output);
  return <ReactMarkdown>{displayText}</ReactMarkdown>;
};
  const fetchFlashcards = async () => {
    try {
      const response = await fetch('http://localhost:8000/get_flashcards');
      if (response.ok) {
        const result = await response.json();
        setFlashcards(result.flashcards);
        setCurrentFlashcardIndex(0);
        setShowAnswer(false);
      } else {
        alert("Error fetching flashcards. Please try again.");
      }
    } catch (error) {
      console.error('Error:', error);
      alert("An error occurred while fetching flashcards. Please try again.");
    }
  };

  const handleNextFlashcard = () => {
    if (currentFlashcardIndex < flashcards.length - 1) {
      setCurrentFlashcardIndex(currentFlashcardIndex + 1);
      setShowAnswer(false);
    }
  };

  const handlePreviousFlashcard = () => {
    if (currentFlashcardIndex > 0) {
      setCurrentFlashcardIndex(currentFlashcardIndex - 1);
      setShowAnswer(false);
    }
  };

  const toggleAnswer = () => {
    setShowAnswer(!showAnswer);
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    if (input.trim()) {
      const userMessage = { text: input, sender: 'user' };
      setMessages([...messages, userMessage]);
      setInput('');

      try {
        if (fileRagMode && ragReady) {
          // Send message to PDF RAG endpoint with llm_type
          const response = await fetch('http://localhost:8000/rag_query', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: input, llm_type: llmType }),
          });
          setLoading(false);

          if (response.ok) {
            const result = await response.json();
            setMessages(prevMessages => [...prevMessages, { text: result.answer, sender: 'bot' }]);
          } else {
            alert("Error querying PDF RAG. Please try again.");
          }
        } 
        else if (flashCardMode && flashCardReady){
          const response = await fetch('http://localhost:8000/pdf_rag_query_flashcard', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({query: input}),
          });
          setLoading(false);

          if (response.ok) {
            const result = await response.json();
            setMessages(prevMessages => [...prevMessages, { text: result.answer, sender: 'bot' }]);
          } else {
            alert("Error querying PDF RAG. Please try again.");
          }
        
        }
        
        else {
          // Existing WebSocket logic
          if (!currentChat) {
            createNewChat();
          }
          setLoading(true);
          sendWebSocketMessage('add_message', {
            chat_id: currentChat,
            message: input,
          });
        }
      } catch (e) {
        setLoading(false);
        console.error('Error sending message:', e);
      }
    }
  };

  const toTitleCase = (str) => {
    return str
      .toLowerCase()
      .replace(/(?:^|\s)\w/g, (match) => match.toUpperCase());
  };


  const handleTogglePlay = (messageId) => {
    setPlayingMessageId(prevId => prevId === messageId ? null : messageId);
  };

  const toggleLlmType = () => {
    setLlmType(prevType => prevType === 'api' ? 'local' : 'api');
    setCurrentChat(null);
    setMessages([]);
    fetchChats();
  };

  useEffect(() => {
    if (currentChat) {
      fetchMessages(currentChat);
    }
  }, [currentChat]);

  return (
    
    <div className="chat-container">
          <div className="chat-sidebar">
            <div className="header-container">
          <h2>Chats</h2>
          <div className="header-icons">
            <button 
              onClick={() => navigate('/mystery-game')} 
              className="icon-btn"
              title="Want a break? Play this Mystery Game"
            >
              <Puzzle size={24} />
            </button>
            <button 
              onClick={() => navigate('/live-chat')} 
              className="icon-btn"
              title="Talk with Curio"
            >
              <Speech size={29} />
            </button>
          </div>
          </div>
            <div className="button-grid">
              <button onClick={createNewChat} className="grid-btn">
                <PlusCircle size={24} />
                <span>New Chat</span>
              </button>
              <button onClick={startGroupChat} className="grid-btn">
                <Users size={24} />
                <span>Start Group Chat</span>
              </button>
              <button onClick={toggleLlmType} className="grid-btn">
                <RefreshCw size={24} />
                <span>{llmType === 'api' ? 'Switch to Private' : 'Switch to Public'}</span>
              </button>
              <button onClick={handleLogout} className="grid-btn">
                <LogOut size={24} />
                <span>Logout</span>
              </button>
            </div>
              
            <div className="search-container">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyUp={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search Chat History"
                className="search-input"
              />
              <button onClick={handleSearch} className="search-btn">
                <Search />
              </button>
            </div>
        {showSearchResults && (
          <div className="search-results">
            {searchResults.map((result) => (
              <div
                key={result.chatId}
                onClick={() => handleSearchResultClick(result.chatId)}
                className="search-result-item"
              >
                {result.snippet}
              </div>
            ))}
          </div>
        )}

            {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => {
                setCurrentChat(chat.id);
                setShowInfoBox(false);
                fetchMessages(chat.id);
                setFileRagMode(false);
                setFlashCardMode(false);
              }}
              className={`chat-item ${currentChat === chat.id ? 'active' : ''}`}
            >
              {/* {chat.is_flashcard ? 'Flashcard: ' : 'Chat: '} */}
              {chat.name ? toTitleCase(chat.name.slice(0, 25)) : 'Unnamed Chat'}...
            </div>
          ))}
          </div>

      <div className="chat-main">
        
      {loading && (
  <div className="loader-overlay">
    <BeatLoader color="#3498db" size={15} margin={2} />
  </div>
)}
      {showWelcome && <WelcomeSection />}

            {flashCardMode && !flashCardReady && (
              <div className="flash-cards">
                <h3 className='pdf-rag-upload'>Upload PDF Document to generate flash cards</h3>
                <input type="file" accept=".pdf" multiple onChange={handleFileUpload} />
                <button onClick={handleFlashCardSubmit}>Process PDFs</button>
              </div>
            )}
         


{isFlashcardChat && flashcards.length > 0 ? (
  <div className="chat-messages flashcard-wrapper">
    {flashCardMode && !flashCardReady && (
      <div className="upload-section">
        <h3 className='pdf-rag-upload'>Upload PDF Document to generate flash cards</h3>
        <input type="file" accept=".pdf" multiple onChange={handleFileUpload} />
        <button onClick={handleFlashCardSubmit}>Process PDFs</button>
      </div>
    )}
    
    
    <div className="flashcard-container">
      <button 
        className="nav-arrow left"
        onClick={handlePreviousFlashcard}
        disabled={currentFlashcardIndex === 0}
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
      </button>

      <div className="flashcard">
        <div className="flashcard-inner">
          <div className="flashcard-progress">
            <div 
              className="progress-bar" 
              style={{ width: `${((currentFlashcardIndex + 1) / flashcards.length) * 100}%` }}
            ></div>
            <span className="progress-text">
              {currentFlashcardIndex + 1} / {flashcards.length}
            </span>
          </div>

          <div className={`flashcard-content ${showAnswer ? 'flipped' : ''}`}>
            <div className="card-front">
              <h3>Question</h3>
              <div className="card-text">
                <p>{flashcards[currentFlashcardIndex].question}</p>
              </div>
              <button onClick={toggleAnswer} className="flip-button">
                Flip Card
              </button>
            </div>
            <div className="card-back">
              <h3>Answer</h3>
              <div className="card-text">
                <p>{flashcards[currentFlashcardIndex].answer}</p>
              </div>
              <button onClick={toggleAnswer} className="flip-button">
                Show Question
              </button>
            </div>
          </div>
        </div>
      </div>

      <button 
        className="nav-arrow right"
        onClick={handleNextFlashcard}
        disabled={currentFlashcardIndex === flashcards.length - 1}
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
        </svg>
      </button>
    </div>
  </div>
) : null}

            {!isFlashcardChat && (<>
            <div className="chat-messages">
            {fileRagMode && (
             <div className="pdf-rag-upload">
             <h3>Upload File(s)</h3>
             <input 
               type="file" 
               accept=".pdf,.docx,.csv" 
               multiple 
               onChange={handleFileUpload}
             />
             <div className="button-container">
               <button onClick={fetchS3Files}>Choose from Uploaded Files</button>
               <button onClick={handlePdfRagSubmit}>Process Files</button>
             </div>

             {/* Only show these sections if we're in the current chat */}
             {showFileSection &&(
               <>
                 <div className="s3-file-list">
                   <h4>Your Files:</h4>
                   <div className="file-buttons-container">
                   {s3Files
                     .filter(file => !file.key.endsWith('/'))
                     .map((file) => {
                         const fileType = file.key.split('.').pop().toLowerCase();
                         const buttonColor = getFileButtonColor(fileType);

                         return (
                             <button
                                 key={file.key}
                                 className={`s3-file-button px-3 py-1 rounded-md text-white ${buttonColor}`}
                                 onClick={() => handleS3FileSelect(file.key)}
                             >
                                 <span>{file.key.split('/').pop()}</span>
                             </button>
                         );
                     })}
                   </div>
                 </div>
                 
                 <div className="selected-s3-files">
                   <h4>Selected Files:</h4>
                   {[...files, ...selectedS3Files].map((file, index) => (
                     <div key={index}>{file.name}</div>
                   ))}
                 </div>
               </>
             )}
           </div>
         )}

            {
              messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <StructuredOutput 
                  output={msg.text} 
                  isStudentDashboard={msg.isStudentDashboard}
                  studentId={msg.studentId}
                />
                {msg.sender === 'bot' && !msg.isStudentDashboard && (
                  <TextToSpeech
                    key={`tts-${index}`}
                    text={msg.text}
                    isPlaying={playingMessageId === index}
                    onTogglePlay={() => handleTogglePlay(index)}
                  />
                )}
              </div>
            ))}
            </div>
            </>
            )}

<form onSubmit={handleSubmit} className="chat-input-form">
            <div className="input-icons">
            <button type="button" onClick={handlePdfRagClick} className="icon-btn" title="PDF RAG">
            <Paperclip size={24} />
            </button>
            <button type="button" onClick={handleFlashCards} className="icon-btn" title="Generate FlashCards">
            <StickyNote size={24} />
            </button>
            <button type="button" onClick={startLinkedInSession} className="icon-btn" title="LinkedIn Automation">
              <Linkedin size={24} />
            </button>
            </div>
            <VoiceInput onInputChange={setInput} className="icon-btn" title="Audio Input" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isLinkedInSession ? "Chat with LinkedIn Automation..." : (pdfRagMode ? "Ask a question about the PDF..." : "Type your message...")}

              className="chat-input"
            />
            <button type="submit" className="send-btn">
              <SendHorizontal size={24} />
            </button>
            </form>
          </div>
        
    </div>
  );
};


export default ChatbotInterface;

