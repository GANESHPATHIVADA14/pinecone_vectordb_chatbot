# ingest.py
import os
import logging
import sys
from dotenv import load_dotenv

from pinecone import Pinecone, PodSpec
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Check for API keys
if not GOOGLE_API_KEY or not PINECONE_API_KEY:
    raise ValueError("API keys for Google and Pinecone must be set in the .env file.")

# PDF and Pinecone settings from your notebook
PDF_PATH = "/home/ganesh-pathivada/Downloads/attention.pdf" # IMPORTANT: Make sure this path is correct
INDEX_NAME = "uber-chatbot-index"
PINECONE_ENVIRONMENT = "us-east-1" # Note: Pinecone Serverless doesn't use environment
EMBEDDING_DIM = 768  # Correct dimension for "models/embedding-001"

def main():
    """
    Main function to process PDF, create embeddings, and store them in Pinecone.
    """
    logging.info("--- Starting Ingestion Process ---")

    # --- 1. Configure LlamaIndex Global Settings ---
    logging.info("Configuring LlamaIndex settings with Gemini models...")
    Settings.llm = Gemini(
        model="models/gemini-1.5-flash",
        api_key=GOOGLE_API_KEY
    )
    Settings.embed_model = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key=GOOGLE_API_KEY
    )
    Settings.chunk_size = 1000
    Settings.chunk_overlap = 200
    logging.info("Settings configured.")

    # --- 2. Load Documents ---
    try:
        logging.info(f"Loading documents from: {PDF_PATH}")
        documents = SimpleDirectoryReader(input_files=[PDF_PATH]).load_data()
        if not documents:
            logging.error("No documents were loaded. Check the PDF path and file content.")
            return
        logging.info(f"Successfully loaded {len(documents)} document chunk(s).")
    except Exception as e:
        logging.error(f"Error loading the PDF file: {e}")
        logging.error(f"Please check that the path is correct: {PDF_PATH}")
        return

    # --- 3. Initialize Pinecone ---
    logging.info("Initializing Pinecone client...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # --- 4. Create Pinecone Index if it doesn't exist ---
    if INDEX_NAME not in pc.list_indexes().names():
        logging.info(f"Creating new Pinecone index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=PodSpec(environment=PINECONE_ENVIRONMENT)
        )
        logging.info("Index created successfully.")
    else:
        logging.info(f"Pinecone index '{INDEX_NAME}' already exists. Will add/update vectors.")

    # --- 5. Setup LlamaIndex Vector Store and Storage Context ---
    pinecone_index = pc.Index(INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # --- 6. Create Index and Store Embeddings ---
    logging.info("Creating index and storing embeddings in Pinecone... This may take a moment.")
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    logging.info("--- Finished Ingestion Process ---")

if __name__ == "__main__":
    main()