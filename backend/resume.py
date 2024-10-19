import sqlite3
import os
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
import shutil
from dotenv import load_dotenv
load_dotenv()

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

def extract_skills_from_resume(pdf_path: str) -> Dict:
    """Extract skills and experience from resume PDF"""
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    # Combine all pages into one text
    resume_text = " ".join([page.page_content for page in pages])
    
    # Use Groq to extract skills and experience
    prompt = f"""
    Analyze the following resume content and extract:
    1. Technical skills
    2. Projects worked on
    3. Areas of expertise
    
    Format the response as a JSON-like dictionary with these three keys.
    Resume content: {resume_text}
    """
    
    response = groq_llm.predict(prompt)
    
    # Parse the response into a dictionary
    # Note: In a production environment, you'd want more robust parsing
    try:
        import json
        skills_dict = json.loads(response)
    except:
        # Fallback to a basic dictionary if parsing fails
        skills_dict = {
            "technical_skills": response.split("Technical skills:")[-1].split("Projects")[0].strip(),
            "projects": response.split("Projects:")[-1].split("Areas")[0].strip(),
            "expertise": response.split("Areas of expertise:")[-1].strip()
        }
    
    return skills_dict

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

def setup_qa_chain(vector_store, resume_data: Dict):
    """Set up QA chain with resume data"""
    message_history = ChatMessageHistory()
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a custom prompt template that includes resume data
    prompt_template = f"""
    Based on the candidate's resume analysis:
    Technical Skills: {resume_data['technical_skills']}
    Previous Projects: {resume_data['projects']}
    Areas of Expertise: {resume_data['expertise']}
    
    Using the provided context about available projects, suggest which projects would be most suitable.
    Consider the candidate's demonstrated skills, project complexity, and potential for skill development.
    
    Context: {{context}}
    Question: {{question}}
    
    Please provide detailed reasoning for each suggestion, including:
    1. Why the project is a good fit based on existing skills
    2. What new skills the candidate could develop
    3. How it aligns with their expertise
    """

    chain = ConversationalRetrievalChain.from_llm(
        llm=groq_llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )
    
    return chain

def generate_project_suggestions(resume_data: Dict) -> str:
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
    qa_chain = setup_qa_chain(global_vector_store, resume_data)
    
    # Generate query based on resume analysis
    query = f"""
    Given a candidate with:
    Technical Skills: {resume_data['technical_skills']}
    Previous Projects: {resume_data['projects']}
    Areas of Expertise: {resume_data['expertise']}
    
    What projects would be most suitable for them to pursue next?
    """
    
    # Get recommendations
    result = qa_chain({"question": query})
    
    return result["answer"]

def process_resume_for_recommendations(pdf_path: str) -> str:
    """Process resume and return project recommendations"""
    try:
        # Extract skills from resume
        resume_data = extract_skills_from_resume(pdf_path)
        
        # Create/update project embeddings
        create_project_embeddings()
        
        # Generate recommendations
        recommendations = generate_project_suggestions(resume_data)
        
        return f"Based on your resume analysis, here are the recommended projects:\n\n{recommendations}"
    
    except Exception as e:
        return f"Error processing resume: {str(e)}"

if __name__ == "__main__":
    # Example usage
    resume_path = "/Users/aswath/Desktop/ethos/ethos/backend/naren_resume (2).pdf"
    recommendations = process_resume_for_recommendations(resume_path)
    print(recommendations)