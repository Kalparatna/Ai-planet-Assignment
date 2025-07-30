"""Adaptive Chunking Service - Provides dynamic chunking strategies for document retrieval"""

import logging
from typing import List, Dict, Any, Optional, Callable
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveChunkingService:
    """Service for dynamically chunking documents based on query and content type"""
    
    def __init__(self):
        # Default chunking parameters
        self.default_chunk_size = 1000
        self.default_chunk_overlap = 100
        
        # Specialized chunkers for different content types
        self.chunkers = {
            "math_problem": self._create_math_problem_chunker(),
            "math_solution": self._create_math_solution_chunker(),
            "pdf_content": self._create_pdf_content_chunker(),
            "web_content": self._create_web_content_chunker(),
        }
    
    def _create_math_problem_chunker(self) -> RecursiveCharacterTextSplitter:
        """Create a chunker optimized for math problems"""
        return RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks for math problems
            chunk_overlap=150,  # Higher overlap to maintain context
            separators=["\n\n", "\n", ".", ";", ":", " ", ""],
        )
    
    def _create_math_solution_chunker(self) -> RecursiveCharacterTextSplitter:
        """Create a chunker optimized for math solutions"""
        return RecursiveCharacterTextSplitter(
            chunk_size=1200,  # Larger chunks for solutions to maintain steps
            chunk_overlap=200,  # Higher overlap for solution continuity
            separators=["\n\n", "\n", "Step", ".", ";", ":", " ", ""],
        )
    
    def _create_pdf_content_chunker(self) -> RecursiveCharacterTextSplitter:
        """Create a chunker optimized for PDF content"""
        return RecursiveCharacterTextSplitter(
            chunk_size=1500,  # Larger chunks for PDF content
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", ";", ":", " ", ""],
        )
    
    def _create_web_content_chunker(self) -> RecursiveCharacterTextSplitter:
        """Create a chunker optimized for web content"""
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", ";", ":", " ", ""],
        )
    
    def get_chunker(self, content_type: str) -> RecursiveCharacterTextSplitter:
        """Get the appropriate chunker for the content type"""
        return self.chunkers.get(
            content_type, 
            RecursiveCharacterTextSplitter(
                chunk_size=self.default_chunk_size,
                chunk_overlap=self.default_chunk_overlap
            )
        )
    
    def chunk_documents(self, documents: List[Document], content_type: str) -> List[Document]:
        """Chunk documents using the appropriate chunker"""
        chunker = self.get_chunker(content_type)
        return chunker.split_documents(documents)
    
    def chunk_text(self, text: str, content_type: str) -> List[Document]:
        """Chunk text using the appropriate chunker"""
        chunker = self.get_chunker(content_type)
        return chunker.create_documents([text])
    
    def adaptive_chunk(self, documents: List[Document], query: str) -> List[Document]:
        """Adaptively chunk documents based on query and document content"""
        # Analyze query to determine optimal chunking strategy
        content_type = self._determine_content_type(query, documents)
        
        # Get appropriate chunker
        chunker = self.get_chunker(content_type)
        
        # Apply chunking
        return chunker.split_documents(documents)
    
    def _determine_content_type(self, query: str, documents: List[Document]) -> str:
        """Determine the content type based on query and documents"""
        query_lower = query.lower()
        
        # Check for math problem indicators in query
        math_problem_indicators = [
            "solve", "calculate", "find", "evaluate", "compute", 
            "determine", "what is", "prove", "equation", "integral",
            "derivative", "area", "volume", "perimeter"
        ]
        
        for indicator in math_problem_indicators:
            if indicator in query_lower:
                return "math_problem"
        
        # Check document metadata for content type hints
        for doc in documents:
            metadata = doc.metadata
            if metadata.get("source") == "pdf":
                return "pdf_content"
            if metadata.get("source") == "web":
                return "web_content"
            if metadata.get("category") == "solution":
                return "math_solution"
        
        # Default to math problem if no other type is determined
        return "math_problem"
    
    def chunk_for_retrieval(self, documents: List[Document]) -> List[Document]:
        """Chunk documents for initial retrieval (typically smaller chunks)"""
        retrieval_chunker = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )
        return retrieval_chunker.split_documents(documents)
    
    def chunk_for_generation(self, documents: List[Document]) -> List[Document]:
        """Chunk documents for generation (typically larger chunks)"""
        generation_chunker = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        return generation_chunker.split_documents(documents)