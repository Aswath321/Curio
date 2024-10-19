import PyPDF2
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import os
import shutil
from langchain_groq import ChatGroq


# Initialize HuggingFace SentenceTransformer for embeddings
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

# Global variable to store the vector store
global_vector_store = None


def process_pdf_files(file_paths):
    texts = []
    metadatas = []
    for file_path in file_paths:
        # Read the PDF file
        pdf = PyPDF2.PdfReader(file_path)
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()
            
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=50)
        file_texts = text_splitter.split_text(pdf_text)
        texts.extend(file_texts)

        # Create a metadata for each chunk
        file_metadatas = [{"source": f"{i}-{os.path.basename(file_path)}"} for i in range(len(file_texts))]
        metadatas.extend(file_metadatas)
    
    return texts, metadatas

def create_vectorstore(texts, metadatas):
    global global_vector_store
    
    # Clear existing vector store if it exists
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    
    # Create new embeddings
    global_vector_store = Chroma.from_texts(
        texts,
        embeddings,
        metadatas=metadatas,
        persist_directory="./chroma_db"  # Persist the vector store
    )
    global_vector_store.persist()  # Explicitly persist the vector store
    return global_vector_store

def setup_qa_chain(docsearch):
    # Initialize message history for conversation
    message_history = ChatMessageHistory()
    
    # Memory for conversational context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOllama(model="llama3.1"),
        retriever=docsearch.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )
    

def store_pdfs(pdf_files_list):
    global global_vector_store
    # Process PDF files
    texts, metadatas = process_pdf_files(pdf_files_list)
    
    # Create new vector store
    global_vector_store = create_vectorstore(texts, metadatas)
    
    print(f"Processing {len(pdf_files_list)} files done. A new RAG system has been created. You can now ask questions!")

def pdf_response(query):
    global global_vector_store
    
    if global_vector_store is None:
        # If the vector store doesn't exist, load it from the persisted directory
        if os.path.exists("./chroma_db"):
            global_vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        else:
            return "No PDFs have been uploaded yet. Please upload PDFs before asking questions."
    
    # Setup QA chain
    qa_chain = setup_qa_chain(global_vector_store)
    
    # Call the chain with user's input
    res = qa_chain({"question": query})
    answer = res["answer"]
    source_documents = res["source_documents"]
    
    print("\nAnswer:", answer)
    
    # Process source documents if available
    if source_documents:
        print("\nSources:")
        for idx, doc in enumerate(source_documents):
            print(f"Source {idx + 1}: {doc.metadata['source']}")
    else:
        print("\nNo sources found")
    
    print("\n" + "-"*50 + "\n")
    
    return answer