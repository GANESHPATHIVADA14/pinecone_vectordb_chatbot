# pinecone_vectordb_chatbot
Running the Application
The application consists of two parts: the backend server and the frontend UI. Both must be running.
1. Run the Backend Server
In your terminal (with the virtual environment activated), start the FastAPI server using Uvicorn:
Generated bash
uvicorn app:app --reload
Use code with caution.
Bash
The server will start, and you should see a line indicating it's running:
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Leave this terminal window open.
2. Launch the Frontend UI
This part is simple. You do not need a terminal.
Open your computer's file explorer.
Navigate to the frontend sub-folder inside your project directory.
Double-click the index.html file.
This will open the user interface in your default web browser, and you can start chatting with your document.
API Endpoints
The FastAPI backend exposes the following endpoints:
Method	Path	Description
GET	/	A root endpoint to confirm that the API is running.
POST	/chat	Takes a query, retrieves context, and returns a synthesized answer from the LLM.
POST	/retrieve	Takes a query and returns the raw, most relevant text chunks from the vector database.
How It Works
Ingestion Flow (ingest.py)
Load Document: SimpleDirectoryReader from LlamaIndex reads the content of the specified PDF.
Chunking: The document is split into smaller, manageable text chunks.
Embedding: Each chunk is passed to the Gemini embedding model to be converted into a numerical vector.
Upsert to Pinecone: The chunks (as vectors) and their metadata are "upserted" (updated/inserted) into the specified Pinecone index.
Querying Flow (app.py and frontend/)
User Query: The user types a question into the web UI and clicks "Send".
API Call: The JavaScript frontend sends a POST request with the query to the /chat endpoint on the FastAPI backend.
Retrieval: The backend uses the same Gemini embedding model to turn the user's query into a vector. It then queries the Pinecone index to find the most similar (i.e., most relevant) text chunks from the document.
Augmentation: The retrieved chunks are combined with the original query into a detailed prompt.
Generation: This augmented prompt is sent to the Gemini gemini-1.5-flash model. The LLM uses the provided context to generate a relevant, accurate answer.
Response: The backend sends the generated answer back to the frontend, which then displays it in the chat window.
