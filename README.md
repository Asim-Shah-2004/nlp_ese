# Agentic RAG PDF Chatbot 🤖📄

An intelligent chatbot that answers questions from PDF documents using Retrieval-Augmented Generation (RAG) powered by Google's Gemini API and FastAPI.

## Features ✨

- **PDF Document Processing**: Upload and process PDF files with automatic text extraction and chunking
- **Vector Store Integration**: Uses ChromaDB for efficient semantic search with sentence transformers
- **Agentic RAG**: Advanced agent that analyzes query intent and adjusts retrieval strategy
- **Gemini AI Integration**: Leverages Google's Gemini Pro model for intelligent responses
- **Chat History**: Maintains conversation context for coherent multi-turn interactions
- **RESTful API**: Clean FastAPI endpoints for easy integration
- **Document Management**: Upload, list, and delete documents as needed

## Architecture 🏗️

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Server             │
│  ┌───────────────────────────┐  │
│  │   /upload    /chat        │  │
│  │   /documents /clear       │  │
│  └───────────────────────────┘  │
└─────────┬───────────────────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌──────────────┐
│   PDF   │ │ Chat Agent   │
│Processor│ │ (Agentic)    │
└────┬────┘ └──────┬───────┘
     │             │
     ▼             ▼
┌─────────────┐ ┌──────────────┐
│Vector Store │ │   Gemini     │
│  (ChromaDB) │ │   API        │
└─────────────┘ └──────────────┘
```

## Prerequisites 📋

- Python 3.8 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

## Installation 🚀

1. **Clone or navigate to the project directory**:
```bash
cd c:\Users\Asim\OneDrive\Desktop\c-hunt\nlp_ese
```

2. **Create and activate a virtual environment** (recommended):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
   ```bash
   Copy-Item .env.example .env
   ```
   - Edit `.env` and add your Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Usage 🎯

### Starting the Server

Run the FastAPI server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### 1. **Upload PDF**
```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/upload" -F "file=@your_document.pdf"
```

Response:
```json
{
  "message": "PDF uploaded and processed successfully",
  "file_id": "uuid-here",
  "file_name": "your_document.pdf",
  "num_chunks": 45,
  "num_characters": 25000
}
```

#### 2. **Chat with Documents**
```bash
POST /chat
Content-Type: application/json

curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "use_agentic": true,
    "use_history": true
  }'
```

Response:
```json
{
  "answer": "Based on the document...",
  "sources": [
    {
      "file_name": "your_document.pdf",
      "chunk_index": 5,
      "relevance_score": 0.892
    }
  ],
  "intent": "FACTUAL_QUESTION",
  "error": null
}
```

#### 3. **List Documents**
```bash
GET /documents

curl -X GET "http://localhost:8000/documents"
```

#### 4. **Delete Document**
```bash
DELETE /documents/{file_id}

curl -X DELETE "http://localhost:8000/documents/{file_id}"
```

#### 5. **Clear Chat History**
```bash
POST /clear

curl -X POST "http://localhost:8000/clear"
```

#### 6. **Get Chat History**
```bash
GET /history

curl -X GET "http://localhost:8000/history"
```

#### 7. **Clear All Data**
```bash
DELETE /clear-all

curl -X DELETE "http://localhost:8000/clear-all"
```

### Python Client Example

```python
import requests

# Upload a PDF
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    print(response.json())

# Ask a question
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'query': 'Summarize the key points in the document',
        'use_agentic': True
    }
)
print(response.json()['answer'])
```

## Configuration ⚙️

Edit `config.py` to customize:

```python
# Model Configuration
GEMINI_MODEL = "gemini-pro"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

## Project Structure 📁

```
nlp_ese/
├── main.py                 # FastAPI application
├── chat_agent.py          # Agentic chat logic with Gemini
├── pdf_processor.py       # PDF text extraction and chunking
├── vector_store.py        # Vector database management
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── README.md             # This file
├── uploads/              # Uploaded PDF files (created automatically)
└── chroma_db/            # Vector database (created automatically)
```

## How It Works 🔍

1. **Upload**: PDFs are uploaded and split into chunks with overlap
2. **Embedding**: Text chunks are converted to vector embeddings using sentence transformers
3. **Storage**: Embeddings are stored in ChromaDB for efficient retrieval
4. **Query**: User questions are converted to embeddings
5. **Retrieval**: Most relevant document chunks are retrieved using similarity search
6. **Agentic Analysis**: The agent analyzes query intent to adjust retrieval strategy
7. **Generation**: Gemini generates contextual answers based on retrieved documents
8. **Response**: Answer is returned with source references

## Agentic Features 🤖

The chatbot includes advanced agentic capabilities:

- **Intent Detection**: Automatically detects query types (factual, summarization, comparison, etc.)
- **Dynamic Retrieval**: Adjusts number of retrieved chunks based on query complexity
- **Context Awareness**: Maintains conversation history for multi-turn interactions
- **Source Attribution**: Provides references to source documents and relevance scores

## Troubleshooting 🔧

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Error**: Verify your Gemini API key is correctly set in `.env`

3. **PDF Processing Error**: Ensure the PDF is not password-protected or corrupted

4. **Memory Issues**: For large PDFs, consider reducing `CHUNK_SIZE` in `config.py`

## Development 💻

To modify the chatbot:

- **Change AI model**: Edit `GEMINI_MODEL` in `config.py`
- **Adjust chunking**: Modify `CHUNK_SIZE` and `CHUNK_OVERLAP` in `config.py`
- **Custom embeddings**: Change `EMBEDDING_MODEL` in `config.py`
- **Add endpoints**: Extend `main.py` with new FastAPI routes

## Performance Tips 🚀

1. **Chunk Size**: Smaller chunks = more precise, larger chunks = more context
2. **Top-K Results**: Increase for complex queries, decrease for simple ones
3. **Embedding Model**: Use larger models for better accuracy (slower but more accurate)

## Security Notes 🔒

- Never commit `.env` file with real API keys
- Use environment variables in production
- Implement authentication for production deployments
- Validate file sizes and types before processing

## License 📄

This project is open source and available under the MIT License.

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Acknowledgments 🙏

- Google Gemini API for powerful language understanding
- ChromaDB for efficient vector storage
- FastAPI for the excellent web framework
- LangChain for text processing utilities

## Support 💬

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Verify your environment setup

---

Made with ❤️ using FastAPI and Google Gemini
