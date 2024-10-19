// import React, { useState, useEffect, useRef } from 'react';
// import VoiceInput from './VoiceInput';
// import TextToSpeech from './TextToSpeech';
// import { initializeApp } from 'firebase/app';
// import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from 'firebase/auth';
// import axios from 'axios';
// import ReactMarkdown from 'react-markdown';

// const WS_URL = 'ws://127.0.0.1:8000/ws';

// const firebaseConfig = {
//   apiKey: "AIzaSyD79jZxUINuMNLXIUMeB-0iAazkmYqqj5s",
//   authDomain: "disaster-app-7a6aa.firebaseapp.com",
//   projectId: "disaster-app-7a6aa",
//   storageBucket: "disaster-app-7a6aa.appspot.com",
//   messagingSenderId: "407854960194",
//   appId: "1:407854960194:web:62a938304aa026ab4227db",
//   measurementId: "G-39ZJLMHZSF"
// };

// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);


// const ChatbotInterface = () => {
//   const [chats, setChats] = useState([]);
//   const [currentChat, setCurrentChat] = useState(null);
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState('');
//   const [playingStates, setPlayingStates] = useState({});
//   const [showInfoBox, setShowInfoBox] = useState(false);
//   const socketRef = useRef(null);
//   const [user, setUser] = useState(null);
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [token, setToken] = useState(null);
//   const [llmType, setLlmType] = useState('api'); 
//   const [pdfRagMode, setPdfRagMode] = useState(false);
//   const [pdfFiles, setPdfFiles] = useState([]);
//   const [pdfRagReady, setPdfRagReady] = useState(false);

  
  


//   useEffect(() => {
//     if (user && token) {
//       connectWebSocket();
//     }
//     return () => {
//       if (socketRef.current) {
//         socketRef.current.close();
//       }
//     };
//   }, [user, token]);


//   useEffect(() => {
//     connectWebSocket();
//     return () => {
//       if (socketRef.current) {
//         socketRef.current.close();
//       }
//     };
//   }, []);

//   const connectWebSocket = () => {
//     const clientId = Math.random().toString(36).substring(7);
//     socketRef.current = new WebSocket(`${WS_URL}/${clientId}`);

//     socketRef.current.onopen = () => {
//       console.log('WebSocket connection established');
//       fetchChats();
//     };

//     socketRef.current.onmessage = (event) => {
//       if (!event.data) {
//         console.error('Received empty message');
//         return;
//       }

//       try {
//         const data = JSON.parse(event.data);
//         handleWebSocketMessage(data);
//       } catch (error) {
//         console.error('Error parsing WebSocket message:', error, event.data);
//       }
//     };

//     socketRef.current.onerror = (error) => {
//       console.error('WebSocket error:', error);
//     };

//     socketRef.current.onclose = () => {
//       console.log('WebSocket connection closed');
//     };
//   };

//   const handleSignUp = async (e) => {
//     e.preventDefault();
//     try {
//       const userCredential = await createUserWithEmailAndPassword(auth, email, password);
//       setUser(userCredential.user);
//       const token = await userCredential.user.getIdToken();
//       setToken(token);
//     } catch (error) {
//       console.error("Error signing up:", error.message);
//       window.alert("Account already exists, Please try again with a new account!");
//     }
//   };

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     try {
//       const userCredential = await signInWithEmailAndPassword(auth, email, password);
//       setUser(userCredential.user);
//       const token = await userCredential.user.getIdToken();
//       setToken(token);
//     } catch (error) {
//       console.error("Error logging in:", error.message);
//       window.alert("Invalid credentials, Please try again!");
//     }
//   };

//   const handleLogout = async () => {
//     try {
//       await signOut(auth);
//       setUser(null);
//       setToken(null);
//       setChats([]);
//       setCurrentChat(null);
//       setMessages([]);
//       if (socketRef.current) {
//         socketRef.current.close();
//       }
//     } catch (error) {
//       console.error("Error logging out:", error.message);
//     }
//   };


//   const handlePdfRagClick = () => {
//     setPdfRagMode(true);
//     setPdfRagReady(false);
//     setPdfFiles([]);
//     setCurrentChat(null);
//     setMessages([]); 
//     setShowInfoBox(false);
//   };


//   const handleFileUpload = (event) => {
//     const files = Array.from(event.target.files);
//     setPdfFiles(files);
//   };



//   const handlePdfRagSubmit = async () => {
//     if (pdfFiles.length === 0) {
//       alert("Please upload at least one PDF file.");
//       return;
//     }
//     const formData = new FormData();
//     pdfFiles.forEach((file) => {
//       formData.append('files', file);  // Use the same key 'files' for all files
//     });
//     formData.append('llm_type', llmType);
//     try {
//       const response = await fetch('http://localhost:8000/upload_pdfs', {
//         method: 'POST',
//         body: formData,
//       });

//       if (response.ok) {
//         const result = await response.json();
//         if (result.status === 'success') {
//           setPdfRagReady(true);
//           alert("PDFs processed successfully. You can now ask questions.");
//         } else {
//           alert("Error processing PDFs. Please try again.");
//         }
//       } else {
//         alert("Error uploading PDFs. Please try again.");
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       alert("An error occurred. Please try again.");
//     }
//   };

//   const handleBotResponse = (botResponse) => {
//     try {
//       const parsedResponse = JSON.parse(botResponse);
//       setMessages((prevMessages) => [...prevMessages, { text: parsedResponse, sender: 'bot' }]);
//     } catch (error) {
//       console.error('Error parsing bot response:', error);
//       setMessages((prevMessages) => [...prevMessages, { text: botResponse, sender: 'bot' }]);
//     }
//   };

//   const handleWebSocketMessage = (data) => {
//     switch (data.type) {
//       case 'chat':
//         setMessages(JSON.parse(data.chat.messages));
//         break;
//       case 'message_added':
//         if (data.response.status === 'success' && data.response.bot_response) {
//           handleBotResponse(data.response.bot_response);
//         }
//         break;
//       case 'chats_list':
//         setChats(data.chats.filter(chat => chat.llm_type === llmType));
//         break;
//       case 'chat_created':
//         setChats((prevChats) => [...prevChats, { id: data.chat_id, llm_type: llmType }]);
//         setCurrentChat(data.chat_id);
//         setMessages([]);
//         setShowInfoBox(true);
//         break;
//       default:
//         console.warn('Unhandled message type:', data.type);
//     }
//   };

//   const sendWebSocketMessage = (type, payload) => {
//     if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
//       const message = JSON.stringify({ type, token, llm_type: llmType, ...payload });
//       console.log('Sending WebSocket message:', message);
//       socketRef.current.send(message);
//     } else {
//       console.error('WebSocket is not connected');
//     }
//   };


//   const fetchChats = () => {
//     sendWebSocketMessage('get_chats');
//   };

//   const fetchMessages = (chatId) => {
//     sendWebSocketMessage('get_chat', { chat_id: chatId });
//   };

//   const createNewChat = () => {
//     sendWebSocketMessage('create_chat');
//     setPdfRagMode(false);
//   };

  
//   const StructuredOutput = ({ output }) => {
//     if (typeof output === 'object' && output.text) {
//       return <div>{output.text}</div>;
//     }
//     return <ReactMarkdown>{output}</ReactMarkdown>;
//   };


//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (input.trim()) {
//       const userMessage = { text: input, sender: 'user' };
//       setMessages([...messages, userMessage]);
//       setInput('');
//       setShowInfoBox(false);

//       try {
//         if (pdfRagMode && pdfRagReady) {
//           // Send message to PDF RAG endpoint with llm_type
//           const response = await fetch('http://localhost:8000/pdf_rag_query', {
//             method: 'POST',
//             headers: {
//               'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ query: input, llm_type: llmType }),
//           });

//           if (response.ok) {
//             const result = await response.json();
//             setMessages(prevMessages => [...prevMessages, { text: result.answer, sender: 'bot' }]);
//           } else {
//             alert("Error querying PDF RAG. Please try again.");
//           }
//         } else {
//           // Existing WebSocket logic
//           if (!currentChat) {
//             createNewChat();
//           }

//           sendWebSocketMessage('add_message', {
//             chat_id: currentChat,
//             message: input,
//           });
//         }
//       } catch (e) {
//         console.error('Error sending message:', e);
//       }
//     }
//   };


//   const handleTogglePlay = (messageId) => {
//     setPlayingStates((prevStates) => ({
//       ...prevStates,
//       [messageId]: !prevStates[messageId],
//     }));
//   };

//   const toggleLlmType = () => {
//     setLlmType(prevType => prevType === 'api' ? 'local' : 'api');
//     setCurrentChat(null);
//     setMessages([]);
//     fetchChats();
//   };

//   useEffect(() => {
//     if (currentChat) {
//       fetchMessages(currentChat);
//     }
//   }, [currentChat]);

//   return (
//     <div className="chat-container">
//       {!user ? (
//         <div className="auth-container">
//           <h2>Login or Sign Up</h2>
//           <form onSubmit={handleLogin}>
//             <input
//               type="email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               placeholder="Email"
//               required
//             />
//             <input
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               placeholder="Password"
//               required
//             />
//             <button type="submit">Login</button>
//           </form>
//           <button onClick={handleSignUp}>Sign Up</button>
//         </div>
//       ) : (
//         <>
//           <div className="chat-sidebar">
//             <h2>Chats</h2>
//             <button onClick={createNewChat} className="new-chat-btn">
//               New Chat
//             </button>
//             <button onClick={toggleLlmType} className="new-chat-btn">
//               {llmType === 'api' ? 'Switch to Local LLM' : 'Switch to API LLM'}
//             </button>
//             <button onClick={handleLogout} className="new-chat-btn">
//               Logout
//             </button>
//             <button onClick={handlePdfRagClick} className="new-chat-btn">
//               PDF RAG ({llmType})
//             </button>
//             {chats.map((chat) => (
//               <div
//                 key={chat.id}
//                 onClick={() => {
//                   setCurrentChat(chat.id);
//                   setShowInfoBox(false);
//                   fetchMessages(chat.id);
//                   setPdfRagMode(false);
//                 }}
//                 className={`chat-item ${currentChat === chat.id ? 'active' : ''}`}
//               >
//                 Chat {typeof chat.id === 'string' ? chat.id.slice(0, 8) : chat.id}...
//               </div>
//             ))}
//           </div>

//       <div className="chat-main">

//       {pdfRagMode && !pdfRagReady && (
//               <div className="pdf-rag-upload">
//                 <h3>Upload PDF Documents</h3>
//                 <input type="file" accept=".pdf" multiple onChange={handleFileUpload} />
//                 <button onClick={handlePdfRagSubmit}>Process PDFs</button>
//               </div>
//             )}
//         {showInfoBox && (
//              <div className="info-box">
//              <h3>For the day</h3>
             
//              <p><b>Reminders:</b></p>
//              <ul>
//                <li>Complete Linux Online Course <b>[LOW]</b></li>
//                <li>Buy Groceries <b>[MEDIUM]</b></li>
//                <li>Submit project report by 5 PM <b>[HIGH]</b></li>
//              </ul>
             
//              <p><b>Meetings:</b></p>
//              <ul>
//                <li>Scrum Meeting at 8 PM</li>
//                <li>Client presentation at 4 PM</li>
//                <li>Meeting with Suresh at 12:30 PM</li>
//              </ul>
           
//              <p><b>Weather:</b></p>
//              <ul>
//                <li>Sunny with a high of 75°F (24°C)</li>
//                <li>Chance of rain in the evening (20%)</li>
//                <li>Wind speed: 10 mph</li>
//              </ul>
             
//              <p><b>Personalized News Recommendation:</b></p>
//            <ul>
//              <li>
//                <a 
//                  href="https://www.theverge.com/2024/9/12/24242704/sony-playstation-ps5-update-adaptive-charging-controller-batteries" 
//                  target="_blank" 
//                  rel="noopener noreferrer" 
//                  style={{ color: 'white', textDecoration: 'underline' }}>
//                  Sony PlayStation PS5 Update
//                </a>
//              </li>
//              <li>
//                <a 
//                  href="https://gizmodo.com/wallace-and-gromit-vengeance-most-fowl-netflix-norbot-smart-gnome-2000492265" 
//                  target="_blank" 
//                  rel="noopener noreferrer" 
//                  style={{ color: 'white', textDecoration: 'underline' }}>
//                  Wallace and Gromit: Vengeance Most Fowl
//                </a>
//              </li>
//              <li>
//                <a 
//                  href="https://finance.yahoo.com/news/buy-100-000-annuity-much-193617734.html" 
//                  target="_blank" 
//                  rel="noopener noreferrer" 
//                  style={{ color: 'white', textDecoration: 'underline' }}>
//                  Why buy a $100,000 Annuity
//                </a>
//              </li>
//            </ul>
   
             
//              <p><b>Mail:</b></p>
//              <ul>
//                <li>You have 8 unread emails in your inbox.</li>
//                <li>You have 2 new important messages</li>
//              </ul>
//            </div>
           
//         )}
//         <div className="chat-messages">
//           {messages.map((msg, index) => (
//             <div key={index} className={`message ${msg.sender}`}>
//               <StructuredOutput output={msg.text} />
//               {msg.sender === 'bot' && (
//                 <TextToSpeech
//                   text={msg.text}
//                   isPlaying={!!playingStates[index]}
//                   onTogglePlay={() => handleTogglePlay(index)}
//                 />
//               )}
//             </div>
//           ))}
//         </div>
//         <form onSubmit={handleSubmit} className="chat-input-form">
//               <input
//                 type="text"
//                 value={input}
//                 onChange={(e) => setInput(e.target.value)}
//                 placeholder={pdfRagMode ? "Ask a question about the PDFs..." : "Type your message..."}
//                 className="chat-input"
//               />
//               <VoiceInput onInputChange={setInput} />
//               <button type="submit" className="send-btn">
//                 Send
//               </button>
//             </form>
//           </div>
//         </>
//       )}
//     </div>
//   );
// };


// export default ChatbotInterface;

import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './Login';
import Signup from './SignUp';
import ChatbotInterfaceStudent from './student/ChatbotInterfaceStudent';
import ChatbotInterfaceAdmin from './admin/ChatbotInterfaceAdmin';
import StudentIntermediatePage from './student/StudentIntermediatePage';
import AdminIntermediatePage from './admin/AdminIntermediatePage';
import LiveChat from './LiveChat';
import MysteryGame from './MysteryGame';
import { AuthProvider, useAuth } from './AuthContext';

const PrivateRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <ChatbotInterfaceStudent />
              </PrivateRoute>
            }
          />
    
         
          <Route
          path="/admin"
          element={
            <PrivateRoute>
              <ChatbotInterfaceAdmin />
            </PrivateRoute>
          }
        />
          <Route
            path="/live-chat"
            element={
              <PrivateRoute>
                <LiveChat />
              </PrivateRoute>
            }
          />
          <Route
            path="/mystery-game"
            element={
              <PrivateRoute>
                <MysteryGame />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;