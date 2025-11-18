import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    GEMINI_MODEL = "gemini-pro"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
    
    # File Upload Configuration
    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".pdf"}
    
    # Vector Store Configuration
    CHROMA_DB_DIR = "chroma_db"
    COLLECTION_NAME = "pdf_documents"
    
    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return True

# Create necessary directories
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.CHROMA_DB_DIR, exist_ok=True)
