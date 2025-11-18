# Quick Start Guide 🚀

Get your Agentic RAG PDF Chatbot running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web server)
- Google Generative AI (Gemini)
- PyPDF2 (PDF processing)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- LangChain (text processing)

## Step 2: Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

## Step 3: Configure Environment

```bash
# Copy the example env file
Copy-Item .env.example .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_key_here
```

Or manually create a `.env` file with:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Step 4: Verify Setup

```bash
# Run the test script
python test_setup.py
```

You should see all tests passing ✅

## Step 5: Start the Server

```bash
# Start the FastAPI server
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will start at: http://localhost:8000

## Step 6: Use the Chatbot

### Option A: Web Interface (Easiest)

1. Open `frontend.html` in your browser
2. Upload a PDF document
3. Start asking questions!

### Option B: API Documentation

Visit http://localhost:8000/docs for interactive API documentation

### Option C: cURL Commands

**Upload a PDF:**
```bash
curl -X POST "http://localhost:8000/upload" -F "file=@your_document.pdf"
```

**Ask a question:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "use_agentic": true
  }'
```

### Option D: Python Code

```python
import requests

# Upload PDF
with open('document.pdf', 'rb') as f:
    r = requests.post('http://localhost:8000/upload', files={'file': f})
    print(r.json())

# Chat
r = requests.post('http://localhost:8000/chat', 
    json={'query': 'Summarize the document', 'use_agentic': True})
print(r.json()['answer'])
```

## Common Issues

### Problem: Import errors
**Solution:** Run `pip install -r requirements.txt`

### Problem: API key error
**Solution:** Check your `.env` file has the correct API key

### Problem: Port already in use
**Solution:** Use a different port:
```bash
uvicorn main:app --port 8001
```

### Problem: PDF processing fails
**Solution:** Ensure PDF is not password-protected

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize settings in `config.py`
- Check API docs at http://localhost:8000/docs
- Try different types of questions (factual, summarization, comparison)

## Features to Try

1. **Upload multiple PDFs** - The system can search across all documents
2. **Conversation history** - Ask follow-up questions
3. **Agentic features** - The bot adapts its retrieval strategy based on your question type
4. **Source attribution** - See which document chunks were used for each answer

Enjoy your AI-powered PDF chatbot! 🎉
