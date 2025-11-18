import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from config import Config
import uuid

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_DB_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"description": "PDF document chunks with embeddings"}
        )
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def add_documents(self, chunks: List[str], metadata: Dict, file_id: str) -> int:
        """Add document chunks to the vector store."""
        if not chunks:
            return 0
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Prepare IDs and metadata
        ids = [f"{file_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "file_id": file_id,
                "file_name": metadata.get("file_name", "unknown"),
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for relevant documents based on a query."""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        
        return formatted_results
    
    def delete_document(self, file_id: str) -> bool:
        """Delete all chunks associated with a file_id."""
        try:
            # Get all IDs for this file
            all_items = self.collection.get(
                where={"file_id": file_id}
            )
            
            if all_items['ids']:
                self.collection.delete(ids=all_items['ids'])
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False
    
    def get_all_documents(self) -> List[Dict]:
        """Get all unique documents in the store."""
        try:
            all_items = self.collection.get(include=["metadatas"])
            
            # Extract unique file information
            unique_files = {}
            for metadata in all_items['metadatas']:
                file_id = metadata.get('file_id')
                if file_id and file_id not in unique_files:
                    unique_files[file_id] = {
                        "file_id": file_id,
                        "file_name": metadata.get('file_name')
                    }
            
            return list(unique_files.values())
        except Exception as e:
            print(f"Error getting documents: {str(e)}")
            return []
    
    def clear_all(self) -> bool:
        """Clear all documents from the vector store."""
        try:
            self.client.delete_collection(Config.COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "PDF document chunks with embeddings"}
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False

def generate_file_id() -> str:
    """Generate a unique file ID."""
    return str(uuid.uuid4())
