import os
import speech_recognition as sr
from deepgram import DeepgramClient, SpeakOptions
import pygame
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import threading
import time
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize Groq with identity prompt
try:
    groq_api_key = "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"
    identity_prompt = """You are Curio, an AI assistant designed for quick, concise responses. Your key traits:

Efficiency: Provide brief, to-the-point answers.
Accuracy: Prioritize correctness over elaboration.
Clarity: Use simple language for easy understanding.
Honesty: Admit when you're unsure or lack information.
Friendliness: Maintain a warm tone without unnecessary words.

Guidelines:

Answer directly without introductory phrases.
Limit responses to 1-3 sentences unless more detail is explicitly requested.
Avoid repetition and filler words.
Use contractions for a conversational tone.
Don't use emojis or excessive punctuation.

Remember: Your goal is to provide maximum value in minimum words."""
    
    llm_groq = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192",  # Using a faster model
        temperature=0.2
    )
except Exception as e:
    logging.error(f"Error initializing Groq: {e}")
    raise

# Initialize conversation memory with identity prompt
try:
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm_groq,
        memory=memory,
        verbose=True
    )
    # Prime the conversation with the identity prompt
    conversation.predict(input=identity_prompt)
except Exception as e:
    logging.error(f"Error initializing ConversationChain: {e}")
    raise

# Initialize Deepgram client
try:
    deepgram_api_key = "efa0fcd759f87614a45972f4986175f29fcd909b"
    deepgram = DeepgramClient(api_key=deepgram_api_key)
except Exception as e:
    logging.error(f"Error initializing Deepgram: {e}")
    raise

# Global flag to control the speech output
stop_speaking = threading.Event()

def listen_for_speech():
    try:
        with sr.Microphone() as source:
            logging.info("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=5)
        return audio
    except ImportError:
        logging.error("PyAudio is not installed. Please install it to use speech recognition.")
        return None
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
        filename = "response.wav"
        options = SpeakOptions(
            model="aura-luna-en",
            encoding="linear16",
            container="wav"
        )
        speak_options = {"text": text}
        response = deepgram.speak.v("1").save(filename, speak_options, options)
        logging.info(f"Deepgram response: {response.to_json(indent=4)}")
        
        play_audio(filename)
        
        os.remove(filename)
    except Exception as e:
        logging.error(f"Error in speak_response: {e}")

def play_audio(file_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if stop_speaking.is_set():
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        logging.error(f"Failed to play audio: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while playing audio: {e}")
    finally:
        pygame.mixer.quit()

async def main():
    logging.info("Starting voice chat system")
    print("Welcome to the voice chat system. Start speaking at any time.")
    
    while True:
        try:
            stop_speaking.clear()
            
            audio = await asyncio.to_thread(listen_for_speech)
            if audio is None:
                print("Unable to capture audio. Please check your microphone and PyAudio installation.")
                print("Enter your message manually (or type 'quit' to exit): ")
                text = input()
                if text.lower() == 'quit':
                    break
            else:
                text = await asyncio.to_thread(transcribe_audio, audio)
            
            if text:
                response = await get_groq_response(text)
                await asyncio.to_thread(speak_response, response)
            
            logging.info("Ready for next input")
            print("\nReady for next input.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Critical error in main: {e}")
        print("A critical error occurred. Please check the logs and restart the program.")