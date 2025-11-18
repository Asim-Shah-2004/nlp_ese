import PyPDF2
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config
import os

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for processing."""
        if not text:
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a PDF file and return extracted text and chunks."""
        # Extract text
        full_text = self.extract_text_from_pdf(pdf_path)
        
        # Create chunks
        chunks = self.chunk_text(full_text)
        
        # Get metadata
        file_name = os.path.basename(pdf_path)
        
        return {
            "file_name": file_name,
            "full_text": full_text,
            "chunks": chunks,
            "num_chunks": len(chunks),
            "num_characters": len(full_text)
        }
    
    def validate_pdf(self, file_path: str) -> bool:
        """Validate if the file is a valid PDF."""
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except:
            return False
