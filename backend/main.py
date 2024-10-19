import google.generativeai as genai
import re
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel
import json
import datetime
import boto3
import random
import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from botocore.exceptions import ClientError 
from components.student_progress import progress
from typing import List, Dict
from flask import Flask, request, jsonify
from typing import List, Optional
from flask_cors import CORS
import random
import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
load_dotenv()
import time
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, File, UploadFile, Form
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from components.youtube import youtube_function
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from PIL import Image
from components.flash_card import flash_card_store
import io
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import google.generativeai as genai
import os
import google.generativeai as genai
from typing import Dict, Any
import json
import warnings
from langchain_community.chat_message_histories import ChatMessageHistory
import vertexai
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_vertexai import VertexAI
import asyncio
import typing
from components.amazon_scrape import scrape_amazon
from components.whatsapp import whatsapp_message
from components.gmail import call_mail
from components.calender import schedule_calender
from components.rem import schedule_reminder
from components.image import get_description
from components.recipe import get_recipes
from components.github import github_action
from components.news import get_news
import networkx as nx
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import io
import networkx as nx
from typing import Dict, List, Any
from components.pdf import file_response_api, reset_system, store_files_api 
import spacy
from collections import Counter
import firebase_admin
from firebase_admin import credentials, auth
from local_llm.ollama_script import initialisation
from local_llm.pdf_rag import store_pdfs
from local_llm.pdf_rag import pdf_response
from agent import AIAgent
import logging
from dotenv import load_dotenv
load_dotenv()
import os
import speech_recognition as sr
from gtts import gTTS
import pygame
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import threading
import time
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel



groq_api_key = os.environ['GROQ_API_KEY']
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0.7
)


logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 

cred = credentials.Certificate("/Users/aswath/Desktop/ethos/ethos/backend/firebase.json")
firebase_admin.initialize_app(cred)


AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


lst_res=[]
agent=AIAgent()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()

            if 'type' not in data or 'token' not in data or 'llm_type' not in data:
                await manager.send_personal_message(json.dumps({"error": "Message type, token, or LLM type is missing"}), client_id)
                continue

            try:
                decoded_token = auth.verify_id_token(data['token'])
                uid = decoded_token['uid']
            except Exception as e:
                await manager.send_personal_message(json.dumps({"error": "Invalid authentication token"}), client_id)
                continue

            llm_type = data['llm_type']
            role=data['role']

            if role=='student':
                if "student_progress" in agent.dic_tools:
                    del agent.dic_tools["student_progress"]
                    agent.workflow = agent.get_workflow() 

            elif role=='admin':
                if "recommend_project" in agent.dic_tools:
                    del agent.dic_tools["recommend_project"]
                    agent.workflow = agent.get_workflow() 
              

            if llm_type == 'local':
                # Handle local LLM requests (no database operations)
                if data['type'] == 'add_message':
                    response = await process_local_llm(data['message'])
                    await manager.send_personal_message(json.dumps({
                        "type": "message_added",
                        "response": response
                    }), client_id)
            
            else:
                # Handle API LLM requests (with database operations)
                if data['type'] == 'create_chat':
                    chat = await create_chat(uid, llm_type)
                    await manager.send_personal_message(json.dumps({"type": "chat_created", "chat_id": chat['chat_id']}), client_id)
                elif data['type'] == 'get_chats':
                    chats = await get_chats(uid, llm_type)
                    await manager.send_personal_message(json.dumps({"type": "chats_list", "chats": chats}), client_id)
                elif data['type'] == 'get_chat':
                    chat = await get_chat(data['chat_id'], uid, llm_type)
                    await manager.send_personal_message(json.dumps({"type": "chat", "chat": chat}), client_id)
                elif data['type'] == 'add_message':
                    response = await add_message(data['chat_id'], data['message'], uid)
                    await manager.send_personal_message(json.dumps({
                        "type": "message_added",
                        "response": response
                    }), client_id)
                else:
                    await manager.send_personal_message(json.dumps({"error": "Unhandled message type"}), client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)




class SummaryRequest(BaseModel):
    text: str

@app.post("/get_summary")
async def get_summary(request: SummaryRequest):
    print("\nhee\n")
    return "consice summary"

def upload_file_to_s3(file_path, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_path: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Upload the file
    s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    )
    try:
        response = s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

class RagQuery(BaseModel):
    query: str
    llm_type: str
  
S3_BUCKET_NAME = "curio-storage"
CLOUDFRONT_DOMAIN = "d354mhz4g8k4e8.cloudfront.net"

@app.get("/list_s3_files")
async def list_s3_files():
    s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    )
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        files = []
        for obj in response.get('Contents', []):
            files.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            })
        return {"status": "success", "files": files}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

class FileKeyRequest(BaseModel):
    file_key: str

@app.post("/get_s3_file_url")
async def get_s3_file_url(request: FileKeyRequest):
    cloudfront_url = f"https://{CLOUDFRONT_DOMAIN}/{request.file_key}"
    return {"status": "success", "url": cloudfront_url}

class S3FileInfo(BaseModel):
    name: str
    url: str
@app.post("/upload_files")
async def upload_files(
    local_files: List[UploadFile] = File(None),
    s3_files: List[str] = Form(None),
    llm_type: str = Form(...)
):
    try:
        reset_system()
        logger.info(f"Received request with llm_type: {llm_type}")
        logger.info(f"Number of local files received: {len(local_files) if local_files else 0}")
        logger.info(f"Number of S3 files received: {len(s3_files) if s3_files else 0}")

        if not local_files and not s3_files:
            raise HTTPException(status_code=422, detail="No files provided")

        if llm_type not in ['api', 'local']:
            raise HTTPException(status_code=422, detail="Invalid llm_type")

        file_paths = []
        s3_file_urls = []

        # Process local files
        if local_files:
            upload_dir = "uploaded_files"
            os.makedirs(upload_dir, exist_ok=True)
            for file in local_files:
                file_path = os.path.join(upload_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())
                file_paths.append(file_path)

            # Upload local files to S3
            s3_bucket_name = "curio-storage"
            for file_path in file_paths:
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension == '.pdf':
                    s3_folder = 'pdfs/'
                elif file_extension == '.docx':
                    s3_folder = 'documents/'
                elif file_extension == '.csv':
                    s3_folder = 'csvs/'
                else:
                    logger.error("Invalid file type")
                    continue
                
                s3_object_name = s3_folder + os.path.basename(file_path)
                if upload_file_to_s3(file_path, s3_bucket_name, s3_object_name):
                    logger.info(f"File {file_path} uploaded to S3 successfully")
                else:
                    logger.error(f"Failed to upload {file_path} to S3")
            print(7)

        # Process S3 files
        if s3_files:
            for s3_file_info in s3_files:
                s3_file = json.loads(s3_file_info)
                s3_file_urls.append(s3_file['url'])

        # Process files based on llm_type
        if llm_type == 'api':
            result = store_files_api(file_paths, s3_file_urls)
            logger.info(result)
        elif llm_type == 'local':
            # Implement local processing if needed
            pass

        return {"status": "success", "message": "Files processed successfully"}

    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        logger.info("Temporary files cleaned up")

@app.post("/rag_query")
async def rag_query(query: dict):
    try:
        if query['llm_type'] == 'local':
            print('not implemented...')
        if query['llm_type'] == 'api':
            answer = file_response_api(query['query'])
        return {"status": "success", "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset_system")
async def reset_system_endpoint():
    try:
        reset_system()
        return {"status": "success", "message": "System reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting system: {str(e)}")
        return {"status": "error", "message": str(e)}

class flashCardQuery(BaseModel):
    query: str

@app.post("/upload_pdfs_flashcard")
async def upload_pdfs_flashcard(files: List[UploadFile] = File(...),user_id: str = Form(...)):
    upload_dir = "uploaded_pdfs_flashcards"
    os.makedirs(upload_dir, exist_ok=True)
    pdf_paths = []
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        pdf_paths.append(file_path)
        flash_card_store(pdf_paths[0])
    
    try:
        # Create a new chat for flashcards
        chat_id = str(uuid.uuid4())
        print(1)
        conn = get_db_connection()
        cursor = conn.cursor()
        print(2)
        
        cursor.execute("INSERT INTO chats (id, user_id, llm_type) VALUES (?, ?, ?)", (chat_id, user_id, "api"))
        conn.commit()
        print(3)

        flashcards = generate_flashcards()
        print(flashcards)

        for card in flashcards:
            cursor.execute("INSERT INTO flashcards (chat_id, question, answer) VALUES (?, ?, ?)", 
                           (chat_id, card['question'], card['answer']))
        print(5)
        conn.commit()
        conn.close()

        return {"status": "success", "message": "PDFs processed and flashcards created", "chat_id": chat_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class Flashcard(BaseModel):
    question: str
    answer: str

class SearchQuery(BaseModel):
    query: str

@app.post("/search_chats")
async def search_chats(search_query: SearchQuery, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id as chat_id, m.text as snippet
            FROM chats c
            JOIN messages m ON c.id = m.chat_id
            WHERE c.user_id = ? AND m.text LIKE ?
            LIMIT 5
        """, (user_id, f"%{search_query.query}%"))
        
        results = [{"chatId": row[0], "snippet": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return results
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def generate_flashcards():
    try:
        file_path='/Users/aswath/Desktop/ethos/ethos/backend/components/decks/deck1.json'
        with open(file_path, 'r') as file:
            flashcards = json.load(file)  
        
        return flashcards  
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return []

def get_db_connection():
    connection = sqlite3.connect("chat1.db")
    connection.row_factory = sqlite3.Row
    return connection

async def create_chat(user_id: str, llm_type: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    chat_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO chats (id, user_id, llm_type) VALUES (?, ?, ?)", (chat_id, user_id, llm_type))
    conn.commit()
    conn.close()

    return {"chat_id": chat_id}


async def get_chats(user_id: str, llm_type: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT chats.id, chats.llm_type, 
        (SELECT text FROM messages WHERE messages.chat_id = chats.id ORDER BY id LIMIT 1) as first_message,
        (SELECT MAX(id) FROM messages WHERE messages.chat_id = chats.id) as last_message_id
        FROM chats
        WHERE chats.user_id = ?
        AND EXISTS (SELECT 1 FROM messages WHERE messages.chat_id = chats.id)
        ORDER BY last_message_id DESC
    """, (user_id,))

    chats = cursor.fetchall()
    conn.close()

    return [{"id": chat[0], "llm_type": chat[1], "name": chat[2] or "New Chat"} for chat in chats]

async def get_chat(chat_id: str, user_id: str, llm_type: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
    chat = cursor.fetchone()
    
    if not chat:
        conn.close()
        raise HTTPException(status_code=404, detail="Chat not found")

    cursor.execute("SELECT COUNT(*) FROM flashcards WHERE chat_id = ?", (chat_id,))
    flashcard_count = cursor.fetchone()[0]

    if flashcard_count > 0:
        cursor.execute("SELECT question, answer FROM flashcards WHERE chat_id = ?", (chat_id,))
        flashcards = [{"question": row[0], "answer": row[1]} for row in cursor.fetchall()]
        conn.close()
        return {
            "chat_id": chat_id,
            "is_flashcard": True,
            "flashcards": flashcards,
            "llm_type": llm_type
        }
    else:
        # This is a regular chat
        cursor.execute("SELECT id, text, sender FROM messages WHERE chat_id = ? ORDER BY id", (chat_id,))
        messages = cursor.fetchall()
        conn.close()
        return {
            "chat_id": chat_id,
            "is_flashcard": False,
            "messages": json.dumps([{"text": msg[1], "sender": msg[2]} for msg in messages]),
            "llm_type": llm_type
        }


async def process_local_llm(message: str) -> Dict[str, Any]:
    bot_response = initialisation(message)
    return {
        "status": "success",
        "message": {"text": message, "sender": "user"},
        "bot_response": {"text": bot_response, "sender": "bot"}
    }


async def add_message(chat_id: str, message_text: str, user_id: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
 
    cursor.execute("SELECT id FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")

    sender = 'user'

    cursor.execute("INSERT INTO messages (chat_id, text, sender) VALUES (?, ?, ?)", (chat_id, message_text, sender))
    user_message_id = cursor.lastrowid

    agent.knowledge_graph.update_from_text(message_text)
    agent.save_knowledge_graph(user_id)

    cursor.execute("SELECT text, sender FROM messages WHERE chat_id = ?", (chat_id,))
    message_rows = cursor.fetchall()

    chat_history = [
        {"role": "user" if row[1] == "user" else "assistant", "content": row[0]}
        for row in message_rows
    ]


    state = {'user_q': message_text,
             'chat_history': chat_history, 
             'lst_res': lst_res, 
             'output': {}}
    
    g = agent.get_workflow()
        
    out = g.invoke(input=state)
    agent_out = out['output'].tool_output
    print(agent_out)
    agent.knowledge_graph.update_from_text(agent_out)
    agent.save_knowledge_graph(user_id)
    bot_response = agent_out
    if 'student_progress' in agent.used_tools:
        bot_response=progress(message_text)
    cursor.execute("INSERT INTO messages (chat_id, text, sender) VALUES (?, ?, ?)", (chat_id, bot_response, 'bot'))
    bot_message_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": {"id": user_message_id, "text": message_text, "sender": "user"},
        "bot_response": {"id": bot_message_id, "text": bot_response, "sender": "bot"}
    }

import subprocess
import threading
process = None
stop_event = threading.Event()




scenarios = [
    {
        "title": "The Vanishing Heiress",
        "setup": "A wealthy heiress has disappeared from her mansion. The last person to see her was her butler.",
        "clues": [
            "A broken vase was found in the study.",
            "The security cameras were disabled an hour before the disappearance.",
            "A large sum of money was withdrawn from the heiress's account recently."
        ],
        "red_herrings": [
            "The gardener was fired last week.",
            "A neighbor reported hearing a dog barking at midnight."
        ],
        "solution": "The butler and the heiress staged the disappearance to claim insurance money."
    },
    {
        "title": "The Poisoned Professor",
        "setup": "A university professor is found dead in his office. Initial reports suggest poisoning.",
        "clues": [
            "A half-empty cup of coffee is on the desk.",
            "The professor's research notes are missing.",
            "A graduate student was seen arguing with the professor the day before."
        ],
        "red_herrings": [
            "The cleaning staff reported the office door was locked from the inside.",
            "An anonymous note warning about danger was found in the professor's mailbox."
        ],
        "solution": "The graduate student poisoned the professor to steal his groundbreaking research."
    },
    {
        "title": "The Museum Heist",
        "setup": "A priceless artifact has been stolen from the city museum during a power outage.",
        "clues": [
            "The security guard's log shows an unscheduled maintenance check.",
            "A museum employee called in sick on the day of the heist.",
            "Traces of a rare pollen were found near the empty display case."
        ],
        "red_herrings": [
            "A famous art thief was released from prison last month.",
            "The museum director recently increased the insurance on the artifact."
        ],
        "solution": "The sick employee and the maintenance worker collaborated to stage the theft during the orchestrated power outage."
    }
]



current_scenario = None
chain = None
attempts = 0
max_attempts = 2
clue_given = False

def select_random_scenario():
    return random.choice(scenarios)

def create_prompt_template(scenario):
    template = f"""
    You are an AI detective assistant helping a human solve the mystery of {scenario['title']}.
    Current scenario: {scenario['setup']}
    Known clues:
    {', '.join(scenario['clues'])}
    Red herrings:
    {', '.join(scenario['red_herrings'])}
    Solution: {scenario['solution']}

    Your role is to guide the human through the investigation, offer insights, and help them piece together the clues. 
    Don't reveal the solution outright, but provide hints and ask thought-provoking questions to lead them towards it.
    If the user's response is irrelevant, kindly inform them and ask them to focus on the case.
    
    Human: {{human_input}}
    AI: 
    """
    return PromptTemplate(template=template, input_variables=["human_input"])

@app.post('/api/mystery-game/start')
def start_game():
    global current_scenario, chain, attempts, clue_given
    current_scenario = select_random_scenario()
    prompt = create_prompt_template(current_scenario)
    memory = ConversationBufferMemory(return_messages=True)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    attempts = 0
    clue_given = False

    intro_message = f"Welcome, detective! We have a new case: {current_scenario['title']}\n{current_scenario['setup']}\n\nLet's begin the investigation. What would you like to do first?"
    return {"message": intro_message}

class UserInput(BaseModel):
    input: str

@app.post('/api/mystery-game/input')
def process_input(user_input: UserInput):
    global attempts, clue_given
    
    if "solution" in user_input.input.lower():
        if attempts < max_attempts:
            response = chain.run(human_input=user_input.input)
            attempts += 1
            if attempts == max_attempts and not clue_given:
                additional_clue = f"\n\nHere's an additional clue to help you:\n{random.choice(current_scenario['clues'])}"
                response += additional_clue
                clue_given = True
                attempts = 0
            return {"message": response, "game_over": False}
        else:
            solution = f"\nI'm sorry, but that's not the correct solution. Here's what actually happened:\n{current_scenario['solution']}"
            return {"message": solution, "game_over": True}
    else:
        response = chain.run(human_input=user_input.input)
        game_over = "case closed" in response.lower()
        return {"message": response, "game_over": game_over}






recognizer = sr.Recognizer()
conversation = None
stop_event = asyncio.Event()

# Initialize Groq and conversation
def initialize_groq():
    global conversation
    try:
        groq_api_key = os.environ['GROQ_API_KEY']
        identity_prompt = """You are an AI assistant named Curio. You are helpful, cheerful, and knowledgeable. 
        You always try to provide accurate and concise information. If you're unsure about something, you admit it. 
        You have a friendly demeanor and enjoy engaging in conversations on various topics. 
        You are conversing with a human so your response should be like speaking to a close friend. Use emotions if necessary.
        Don't use emojis. Keep the response as short and concise as possible"""
        
        llm_groq = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-70b-8192",
            temperature=0.2
        )
        
        memory = ConversationBufferMemory()
        conversation = ConversationChain(
            llm=llm_groq,
            memory=memory,
            verbose=True
        )
        conversation.predict(input=identity_prompt)
    except Exception as e:
        logging.error(f"Error initializing Groq: {e}")
        raise






# Voice chat functions
def listen_for_speech():
    try:
        with sr.Microphone() as source:
            logging.info("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=5)
        return audio
    except Exception as e:
        logging.error(f"Error in listen_for_speech: {e}")
        return None

def transcribe_audio(audio):
    if audio is None:
        return ""
    try:
        text = recognizer.recognize_google(audio)
        logging.info(f"Transcribed: {text}")
        return text
    except sr.UnknownValueError:
        logging.warning("Could not understand audio")
        return ""
    except sr.RequestError as e:
        logging.error(f"Error in speech recognition service: {e}")
        return ""

async def get_groq_response(text):
    try:
        response = await asyncio.to_thread(conversation.predict, input=text)
        logging.info(f"Groq response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error getting Groq response: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def speak_response(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        
        pygame.mixer.init()
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if stop_event.is_set():
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        
        pygame.mixer.quit()
        os.remove("response.mp3")
    except Exception as e:
        logging.error(f"Error in speak_response: {e}")

async def voice_chat_loop():
    while not stop_event.is_set():
        try:
            audio = await asyncio.to_thread(listen_for_speech)
            if stop_event.is_set():
                break
            text = await asyncio.to_thread(transcribe_audio, audio)
            if text:
                response = await get_groq_response(text)
                await asyncio.to_thread(speak_response, response)
        except Exception as e:
            logging.error(f"Error in voice_chat_loop: {e}")

@app.post("/start-voice")
async def start_voice(background_tasks: BackgroundTasks):
    if not conversation:
        initialize_groq()
    stop_event.clear()
    background_tasks.add_task(voice_chat_loop)
    return {"message": "Voice chat started"}

@app.post("/stop-voice")
async def stop_voice():
    stop_event.set()
    return {"message": "Voice chat stopped"}



class Milestone(BaseModel):
    name: str
    status: str
    completionDate: Optional[str]

class FilePaths(BaseModel):
    pdf: List[str]
    csv: List[str]
    other: List[str]

class ProjectData(BaseModel):
    Student_ID: str
    Project_ID: str
    Project_Name: str
    Milestone_Name: str
    Milestone_Status: str
    Overall_Status: str
    Overall_Completion_Percentage: int
    Update_Date: str
    Time_Spent: int
    Uploaded_Files: int
    Next_Deadline: str
    File_Paths: FilePaths
    milestones: List[Milestone]

def load_mock_data():
    return [
        {
            "Student_ID": "ST101",
            "Project_ID": "P001",
            "Project_Name": "AI Healthcare Analysis",
            "Milestone_Name": "Data Collection",
            "Milestone_Status": "Completed",
            "Overall_Status": "On Track",
            "Overall_Completion_Percentage": 75,
            "Update_Date": "2024-03-15",
            "Time_Spent": 45,
            "Uploaded_Files": 8,
            "Next_Deadline": "2024-04-01",
            "File_Paths": {
                "pdf": ["/path/to/report1.pdf", "/path/to/analysis1.pdf"],
                "csv": ["/path/to/dataset1.csv", "/path/to/results1.csv"],
                "other": ["/path/to/notes.txt", "/path/to/image.jpg"]
            },
            "milestones": [
                {"name": "Project Initiation", "status": "completed", "completionDate": "2024-01-15"},
                {"name": "Requirements Gathering", "status": "completed", "completionDate": "2024-02-01"},
                {"name": "Data Collection", "status": "completed", "completionDate": "2024-03-15"},
                {"name": "Data Analysis", "status": "in progress", "completionDate": None},
                {"name": "Model Development", "status": "pending", "completionDate": None}
            ]
        },
    ]

def get_db1_connection():
    conn = sqlite3.connect('/Users/aswath/Desktop/ethos/ethos/backend/student_projects.db')
    conn.row_factory = sqlite3.Row  
    return conn

@app.get("/api/student/{student_id}/projects")
async def get_student_data(student_id: str):
    conn = get_db1_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ProjectData WHERE Student_ID = ?", (student_id,))
    student_projects = cursor.fetchall()

    if not student_projects:
        raise HTTPException(status_code=404, detail="Student not found")

    project_ids = [project['Project_ID'] for project in student_projects]
    placeholders = ','.join(['?' for _ in project_ids])
    cursor.execute(f"SELECT * FROM Milestones WHERE Project_ID IN ({placeholders})", project_ids)
    all_milestones = cursor.fetchall()

    milestones_by_project = {}
    for milestone in all_milestones:
        project_id = milestone['Project_ID']
        if project_id not in milestones_by_project:
            milestones_by_project[project_id] = []
        milestones_by_project[project_id].append(dict(milestone))

    projects = []
    for project in student_projects:
        project_dict = dict(project)
        project_dict['milestones'] = milestones_by_project.get(project['Project_ID'], [])
        projects.append(project_dict)

    conn.close()
    return projects



@app.get("/api/student/{student_id}/metrics")
async def get_student_metrics(student_id: str):
    conn = get_db1_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ProjectData WHERE Student_ID = ?", (student_id,))
    student_projects = cursor.fetchall()

    if not student_projects:
        raise HTTPException(status_code=404, detail="Student not found")

    deadlines = []
    total_time = 0
    total_files = 0
    total_completion = 0

    for project in student_projects:
        total_time += project['Time_Spent']
        total_files += project['Uploaded_Files']
        total_completion += project['Overall_Completion_Percentage']

        if project['Next_Deadline']:
            deadlines.append({"date": project['Next_Deadline'], "milestone": project['Milestone_Name']})

    if not deadlines:
        raise HTTPException(status_code=404, detail="No upcoming deadlines found")

    conn.close()

    return {
        "totalProjects": len(student_projects),
        "totalTime": total_time,
        "totalFiles": total_files,
        "averageCompletion": total_completion // len(student_projects),
        "nextDeadline": min(deadlines, key=lambda x: x['date'])
    }



@app.get("/api/student/{student_id}/files")
async def get_student_files(student_id: str):
    conn = get_db1_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Project_ID FROM ProjectData WHERE Student_ID = ?", (student_id,))
    project_ids = [row['Project_ID'] for row in cursor.fetchall()]

    if not project_ids:
        raise HTTPException(status_code=404, detail="Student not found")

    files = {"pdf": [], "csv": [], "other": []}

    for project_id in project_ids:
        cursor.execute("SELECT * FROM FilePaths WHERE Project_ID = ?", (project_id,))
        file_paths = cursor.fetchone()

        if file_paths:
            files["pdf"].append(file_paths['pdf'])
            files["csv"].append(file_paths['csv'])
            files["other"].append(file_paths['other'])

    conn.close()

    return files




@app.get("/api/peer-data")
async def get_peer_data():
    return {
        "averageCompletion": 70
    }

class Project(BaseModel):
    id: int
    name: str
    deadline: str  

projects_data = [
    {"id": 1, "name": "Project Alpha", "deadline": "2024-10-30"},
    {"id": 2, "name": "Project Beta", "deadline": "2024-11-15"},
    {"id": 3, "name": "Project Gamma", "deadline": "2024-12-01"},
]

@app.get("/projects", response_model=List[Project])
async def get_projects():
    return projects_data
