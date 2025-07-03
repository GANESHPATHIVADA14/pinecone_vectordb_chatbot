# app.py
import os
import logging
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- ADD THESE IMPORTS ---
from fastapi.middleware.cors import CORSMiddleware

from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
# --- CORRECTED IMPORTS ---
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini


# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Check for API keys
if not GOOGLE_API_KEY or not PINECONE_API_KEY:
    raise ValueError("API keys for Google and Pinecone must be set in the .env file.")

# Constants
INDEX_NAME = "uber-chatbot-index"

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- FastAPI App Setup ---
app = FastAPI(
    title="RAG Chatbot API",
    description="A backend for a RAG chatbot using LlamaIndex, Gemini, and Pinecone.",
    version="1.0.0",
)

# --- ADD THIS CORS MIDDLEWARE SECTION ---
# This allows your frontend to communicate with this backend.
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "null", # Allows opening the HTML file directly
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# Pydantic model for the request body
class ChatRequest(BaseModel):
    query: str

# Global variable to hold the chat engine
chat_engine = None

@app.on_event("startup")
def startup_event():
    """
    Initialize the chatbot on server startup.
    This function is called once when the FastAPI application starts.
    """
    global chat_engine
    logging.info("--- Server starting up: Initializing Chat Engine ---")

    # --- 1. Configure LlamaIndex Global Settings ---
    logging.info("Configuring LlamaIndex settings with Gemini models...")
    Settings.llm = Gemini(model_name="models/gemini-1.5-flash", api_key=GOOGLE_API_KEY)
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=GOOGLE_API_KEY)
    logging.info("Settings configured.")

    # --- 2. Initialize Pinecone and connect to the existing index ---
    logging.info(f"Connecting to Pinecone index: '{INDEX_NAME}'")
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pc.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        
        # --- 3. Load the index from the vector store ---
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        logging.info("Successfully loaded index from Pinecone.")
        
        # --- 4. Create the Chat Engine ---
        chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)
        logging.info("✅ Chat engine is ready!")

    except Exception as e:
        logging.error(f"Failed to initialize chat engine: {e}")
        raise RuntimeError("Could not initialize the chat engine. Please check logs.")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Receives a query, interacts with the chat engine, and returns the response.
    """
    if not chat_engine:
        raise HTTPException(status_code=503, detail="Chat engine is not available.")
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logging.info(f"Received query: {request.query}")
    
    response = await chat_engine.achat(request.query)
    
    return {"response": str(response)}

@app.get("/")
def root():
    return {"message": "RAG Chatbot API is running. Send POST requests to /chat"}