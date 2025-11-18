from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from datetime import datetime

from config import Config
from pdf_processor import PDFProcessor
from vector_store import VectorStore, generate_file_id
from chat_agent import ChatAgent

# Initialize FastAPI app
app = FastAPI(
    title="Agentic RAG PDF Chatbot",
    description="An intelligent chatbot that answers questions from PDF documents using RAG and Gemini API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    Config.validate()
    pdf_processor = PDFProcessor()
    vector_store = VectorStore()
    chat_agent = ChatAgent()
except Exception as e:
    print(f"Error initializing components: {str(e)}")
    raise

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    use_agentic: Optional[bool] = True
    use_history: Optional[bool] = True

class ChatResponse(BaseModel):
    answer: Optional[str]
    sources: List[dict]
    intent: Optional[str] = None
    error: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    file_id: str
    file_name: str
    num_chunks: int
    num_characters: int

class DocumentInfo(BaseModel):
    file_id: str
    file_name: str

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Agentic RAG PDF Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - Upload a PDF document",
            "chat": "/chat - Chat with the uploaded documents",
            "documents": "/documents - List all uploaded documents",
            "clear": "/clear - Clear chat history",
            "delete": "/documents/{file_id} - Delete a specific document",
            "health": "/health - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_api_configured": bool(Config.GOOGLE_API_KEY)
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF document and process it for RAG.
    
    - **file**: PDF file to upload (max 10MB)
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique file ID
        file_id = generate_file_id()
        
        # Save uploaded file
        file_path = os.path.join(Config.UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate PDF
        if not pdf_processor.validate_pdf(file_path):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid PDF file")
        
        # Process PDF
        result = pdf_processor.process_pdf(file_path)
        
        # Add to vector store
        num_chunks = vector_store.add_documents(
            chunks=result['chunks'],
            metadata={"file_name": file.filename},
            file_id=file_id
        )
        
        return UploadResponse(
            message="PDF uploaded and processed successfully",
            file_id=file_id,
            file_name=file.filename,
            num_chunks=num_chunks,
            num_characters=result['num_characters']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the uploaded documents using RAG.
    
    - **query**: Your question about the documents
    - **use_agentic**: Use advanced agentic features (default: true)
    - **use_history**: Include chat history in context (default: true)
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Use agentic or regular chat
        if request.use_agentic:
            result = chat_agent.agentic_chat(request.query)
        else:
            result = chat_agent.chat(request.query, use_history=request.use_history)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return ChatResponse(
            answer=result.get('answer'),
            sources=result.get('sources', []),
            intent=result.get('intent'),
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all uploaded documents.
    """
    try:
        documents = vector_store.get_all_documents()
        return [DocumentInfo(**doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.delete("/documents/{file_id}")
async def delete_document(file_id: str):
    """
    Delete a specific document from the vector store.
    
    - **file_id**: The unique identifier of the document
    """
    try:
        success = vector_store.delete_document(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Try to delete physical file
        for filename in os.listdir(Config.UPLOAD_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(Config.UPLOAD_DIR, filename)
                try:
                    os.remove(file_path)
                except:
                    pass
        
        return {"message": "Document deleted successfully", "file_id": file_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.post("/clear")
async def clear_chat_history():
    """
    Clear the chat history.
    """
    try:
        chat_agent.clear_history()
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")

@app.get("/history")
async def get_chat_history():
    """
    Get the current chat history.
    """
    try:
        history = chat_agent.get_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")

@app.delete("/clear-all")
async def clear_all_data():
    """
    Clear all documents and chat history (use with caution).
    """
    try:
        # Clear vector store
        vector_store.clear_all()
        
        # Clear chat history
        chat_agent.clear_history()
        
        # Clear uploaded files
        for filename in os.listdir(Config.UPLOAD_DIR):
            file_path = os.path.join(Config.UPLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except:
                pass
        
        return {"message": "All data cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
