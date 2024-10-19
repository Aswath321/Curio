import sqlite3
import os
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
import shutil

# Initialize embedding model
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

# Initialize Groq
groq_llm = ChatGroq(
    groq_api_key=os.environ['GROQ_API_KEY'],
    model_name="llama3-70b-8192",
    temperature=0.2
)

# Global vector store
global_vector_store = None

# Sample project descriptions
AVAILABLE_PROJECTS = [
    {
        "id": "AP001",
        "name": "Blockchain-based Supply Chain",
        "description": """A system to track products through supply chain using blockchain. 
        Involves smart contracts, distributed ledger, and real-time tracking. 
        Skills: Blockchain, Smart Contracts, distributed systems."""
    },
    {
        "id": "AP002",
        "name": "ML-based Plant Disease Detection",
        "description": """Mobile app using computer vision to identify plant diseases from images. 
        Includes dataset creation, model training, and deployment. 
        Skills: Computer Vision, Deep Learning, Mobile Development."""
    },
    {
        "id": "AP003",
        "name": "Smart Home Energy Management",
        "description": """IoT system for monitoring and optimizing home energy usage. 
        Features real-time monitoring, predictive analytics, and automation. 
        Skills: IoT, Data Analytics, Embedded Systems."""
    },
    {
        "id": "AP004",
        "name": "Natural Language Processing for Legal Documents",
        "description": """System to analyze legal documents using NLP. 
        Features include document classification, information extraction, and summary generation. 
        Skills: NLP, Text Processing, Machine Learning."""
    }
]

def get_db_connection():
    conn = sqlite3.connect('student_projects.db')
    conn.row_factory = sqlite3.Row
    return conn

def extract_student_id(query: str) -> str:
    """Extract student ID from natural language query using Groq"""
    prompt = f"""
    Extract only the student ID from the following query. The student ID format is 'ST' followed by three numbers.
    If multiple IDs are found, return the first one. If no valid student ID is found, return 'NOT_FOUND'.
    Only return the ID itself, nothing else.
    
    Query: {query}
    """
    
    response = groq_llm.predict(prompt)
    return response.strip()

def get_student_details(student_id: str) -> Dict:
    """Fetch student's project history and details from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT pd.*, m.name as milestone_name, m.status as milestone_status
    FROM ProjectData pd
    LEFT JOIN Milestones m ON pd.Project_ID = m.Project_ID
    WHERE pd.Student_ID = ?
    """
    
    cursor.execute(query, (student_id,))
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return None
    
    student_data = {
        "student_id": student_id,
        "projects": [dict(row) for row in rows]
    }
    
    conn.close()
    return student_data

def create_project_embeddings():
    """Create vector store for available projects using ChromaDB"""
    global global_vector_store
    
    # Clear existing vector store if it exists
    if os.path.exists("./chroma_projects_db"):
        shutil.rmtree("./chroma_projects_db")
    
    # Prepare texts and metadata for projects
    texts = []
    metadatas = []
    
    for project in AVAILABLE_PROJECTS:
        text = f"{project['name']}\n{project['description']}"
        metadata = {
            "id": project['id'],
            "name": project['name']
        }
        texts.append(text)
        metadatas.append(metadata)
    
    # Create and persist vector store
    global_vector_store = Chroma.from_texts(
        texts,
        embeddings,
        metadatas=metadatas,
        persist_directory="./chroma_projects_db"
    )
    global_vector_store.persist()
    
    return global_vector_store

def setup_qa_chain(vector_store, student_data: Dict):
    """Set up QA chain with conversation history"""
    message_history = ChatMessageHistory()
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a custom prompt template that includes student data
    prompt_template = f"""
    Based on the student's project history:
    {student_data}
    
    Using the provided context about available projects, suggest which projects would be most suitable.
    Consider the student's demonstrated skills, project complexity, and potential for skill development.
    
    Context: {{context}}
    Question: {{question}}
    
    Please provide detailed reasoning for each suggestion.
    """

    chain = ConversationalRetrievalChain.from_llm(
        llm=groq_llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )
    
    return chain

def generate_project_suggestions(student_data: Dict) -> str:
    """Generate project suggestions using vector store and LLM"""
    global global_vector_store
    
    if global_vector_store is None:
        if os.path.exists("./chroma_projects_db"):
            global_vector_store = Chroma(
                persist_directory="./chroma_projects_db",
                embedding_function=embeddings
            )
        else:
            global_vector_store = create_project_embeddings()
    
    # Set up QA chain
    qa_chain = setup_qa_chain(global_vector_store, student_data)
    
    # Generate query based on student's experience
    query = f"""
    Given a student with experience in:
    {', '.join([p['Project_Name'] for p in student_data['projects']])}
    
    What projects would be most suitable for them to pursue next?
    """
    
    # Get recommendations
    result = qa_chain({"question": query})
    
    return result["answer"]

def process_recommendation_request(query: str) -> str:
    create_project_embeddings()
    """Process natural language query and return project recommendations"""
    # Extract student ID
    student_id = extract_student_id(query)
    
    if student_id == "NOT_FOUND":
        return "Sorry, I couldn't find a valid student ID in your query. Please include a student ID in the format 'ST' followed by three numbers (e.g., ST101)."
    
    # Get student details
    student_data = get_student_details(student_id)
    if not student_data:
        return f"No data found for student {student_id}"
    
    # Generate recommendations
    recommendations = generate_project_suggestions(student_data)
    
    return f"Recommendations for student {student_id}:\n\n{recommendations}"

# if __name__ == "__main__":
#     # Initialize project embeddings
#     create_project_embeddings()
    
#     # Example queries
#     test_queries = [
#         "Can you suggest some projects for student ST101?",
#         "What projects would you recommend for ST101 based on their experience?",
#         "I need project suggestions for student with ID ST101",
#     ]
    
#     for query in test_queries:
#         print(f"\nProcessing query: {query}")
#         print("-" * 50)
#         result = process_recommendation_request(query)
#         print(result)
#         print("=" * 80)