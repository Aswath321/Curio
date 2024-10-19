import os
import sys
from dotenv import load_dotenv
import PyPDF2
import traceback
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK data for sentence tokenization
nltk.download('punkt', quiet=True)

# ASCII Art Title (omitted for brevity)
title = "FlashCard"
print(title)

# Load environment variables
load_dotenv()

# Get API key from user or environment variable
# Configure the ChatGroq
try:
    llm = ChatGroq(
        groq_api_key="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",
        model_name="llama3-70b-8192"
    )
    print("API key configured successfully.")
except Exception as e:
    print(f"Error configuring API key: {str(e)}")
    sys.exit(1)



# Function to extract text from PDF file
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        print(f"Successfully extracted text from {file_path}")
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise

# Function to split text into chunks
def split_text_into_chunks(text, max_chunk_size=3000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_flashcards(chunk):
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant tasked with creating flashcards from given text."),
            ("human", """
            Given the following text, generate a set of flashcards. Focus on the most important points and include any key definitions.
            Format the output as a JSON array of objects, where each object represents a flashcard with 'question' and 'answer' fields.
            Generate at least 5 flashcards, or more if necessary to cover all important information in this chunk of text.
            IMPORTANT: Provide ONLY the JSON array, without any additional text or formatting.
            Text: {input_text}
            """)
        ])

        chain = prompt_template | llm

        print("Sending request to ChatGroq API...")
        response = chain.invoke({"input_text": chunk})
        print("Response received from ChatGroq API.")

        # Check if the response contains JSON-like content
        content = response.content.strip()

        # Try to load the content directly as JSON
        try:
            flashcards = json.loads(content)
        except json.JSONDecodeError:
            print("Error decoding JSON. Raw response content:")
            print(content)
            return []

        return flashcards
    except Exception as e:
        print(f"Error generating flashcards: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return []


deckname = 'deck1'

# Get filename and deck name from user
def flash_card_store(filename):
    filename = filename
    # Extract text from PDF
    pdf_path = f"/Users/aswath/Desktop/ethos/ethos/backend/{filename}"
    try:
        pdf_text = extract_text_from_pdf(pdf_path)
        print("Text extracted successfully.")
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the PDF: {str(e)}")
        sys.exit(1)

    # Split text into chunks
    chunks = split_text_into_chunks(pdf_text)
    print(f"Text split into {len(chunks)} chunks.")

    # Generate flashcards for each chunk
    all_flashcards = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {len(chunks)}...")
        chunk_flashcards = generate_flashcards(chunk)
        all_flashcards.extend(chunk_flashcards)

    # Save all flashcards to a JSON file
    output_path = "/Users/aswath/Desktop/ethos/ethos/backend/components/decks/deck1.json"
    try:
        with open(output_path, 'w') as file:
            json.dump(all_flashcards, file, indent=2)
        print(f"File written successfully to: {output_path}")
        print(f"Total flashcards generated: {len(all_flashcards)}")
    except Exception as e:
        print(f"An error occurred while saving the file: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()