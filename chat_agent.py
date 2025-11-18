import google.generativeai as genai
from typing import List, Dict, Optional
from config import Config
from vector_store import VectorStore

class ChatAgent:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Initialize model
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # Initialize vector store
        self.vector_store = VectorStore()
        
        # Chat history
        self.chat_history = []
    
    def _build_context(self, relevant_docs: List[Dict]) -> str:
        """Build context from relevant documents."""
        if not relevant_docs:
            return "No relevant context found in the documents."
        
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            content = doc['content']
            metadata = doc['metadata']
            file_name = metadata.get('file_name', 'Unknown')
            
            context_parts.append(
                f"[Document {i} - {file_name}]\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, chat_history: List[Dict] = None) -> str:
        """Build the prompt for the Gemini model."""
        
        # Build conversation history
        history_text = ""
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role.upper()}: {content}\n"
        
        prompt = f"""You are an intelligent AI assistant specialized in answering questions based on PDF documents. 
Your task is to provide accurate, helpful, and contextual answers based on the information provided.

**CONTEXT FROM DOCUMENTS:**
{context}

**CONVERSATION HISTORY:**
{history_text}

**USER QUESTION:**
{query}

**INSTRUCTIONS:**
1. Answer the question based primarily on the provided context from the documents.
2. If the context contains relevant information, use it to formulate your answer.
3. If the context doesn't fully answer the question, acknowledge what information is available and what is missing.
4. Be concise but thorough in your explanations.
5. If you're citing specific information, you can reference which document it came from.
6. Maintain conversation continuity by considering the chat history.
7. If the question is not related to the documents, politely redirect to document-related queries.

**ANSWER:**"""
        
        return prompt
    
    def chat(self, query: str, use_history: bool = True) -> Dict:
        """
        Process a chat query using RAG approach.
        
        Args:
            query: User's question
            use_history: Whether to include chat history in the prompt
            
        Returns:
            Dictionary containing answer and relevant sources
        """
        try:
            # Step 1: Retrieve relevant documents
            relevant_docs = self.vector_store.search(query, top_k=Config.TOP_K_RESULTS)
            
            if not relevant_docs:
                return {
                    "answer": "I don't have any documents uploaded yet. Please upload a PDF document first so I can answer your questions about it.",
                    "sources": [],
                    "error": None
                }
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(relevant_docs)
            
            # Step 3: Build prompt with context and history
            history = self.chat_history if use_history else None
            prompt = self._build_prompt(query, context, history)
            
            # Step 4: Generate response using Gemini
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Step 5: Update chat history
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": answer})
            
            # Step 6: Format sources
            sources = [
                {
                    "file_name": doc['metadata'].get('file_name'),
                    "chunk_index": doc['metadata'].get('chunk_index'),
                    "relevance_score": round(1 - doc['distance'], 3)  # Convert distance to similarity score
                }
                for doc in relevant_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "error": None
            }
            
        except Exception as e:
            return {
                "answer": None,
                "sources": [],
                "error": f"Error generating response: {str(e)}"
            }
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
    
    def get_history(self) -> List[Dict]:
        """Get the chat history."""
        return self.chat_history
    
    def agentic_chat(self, query: str) -> Dict:
        """
        Enhanced agentic chat that can decide on actions.
        This is a more advanced version that analyzes the query type.
        """
        try:
            # Analyze query intent
            intent_prompt = f"""Analyze this user query and determine its intent:
Query: "{query}"

Classify the intent as one of:
1. FACTUAL_QUESTION - User wants specific information from documents
2. SUMMARIZATION - User wants a summary of document content
3. COMPARISON - User wants to compare information across documents
4. GENERAL_CHAT - User is having a general conversation
5. CLARIFICATION - User is asking for clarification on previous answer

Respond with just the category name."""

            intent_response = self.model.generate_content(intent_prompt)
            intent = intent_response.text.strip()
            
            # Adjust retrieval strategy based on intent
            if "SUMMARIZATION" in intent:
                top_k = 10  # Get more chunks for summarization
            elif "COMPARISON" in intent:
                top_k = 8
            else:
                top_k = Config.TOP_K_RESULTS
            
            # Retrieve with adjusted strategy
            relevant_docs = self.vector_store.search(query, top_k=top_k)
            
            if not relevant_docs:
                return self.chat(query)  # Fall back to regular chat
            
            context = self._build_context(relevant_docs)
            
            # Enhanced prompt based on intent
            enhanced_prompt = self._build_prompt(query, context, self.chat_history)
            enhanced_prompt += f"\n\n**DETECTED INTENT:** {intent}\nAdjust your response style accordingly."
            
            response = self.model.generate_content(enhanced_prompt)
            answer = response.text
            
            # Update history
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": answer})
            
            sources = [
                {
                    "file_name": doc['metadata'].get('file_name'),
                    "chunk_index": doc['metadata'].get('chunk_index'),
                    "relevance_score": round(1 - doc['distance'], 3)
                }
                for doc in relevant_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "intent": intent,
                "error": None
            }
            
        except Exception as e:
            # Fallback to regular chat if agentic features fail
            return self.chat(query)
