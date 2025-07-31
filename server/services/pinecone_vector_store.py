"""
Pinecone Vector Store Manager - Real implementation with Pinecone
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    # Fallback for older versions
    GoogleGenerativeAIEmbeddings = None

# Configure logging
logger = logging.getLogger(__name__)

class PineconeVectorStoreManager:
    """Real Pinecone vector store manager"""
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "developer-quickstart-py")
        self.cloud = os.getenv("PINECONE_CLOUD", "aws")
        self.region = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        
        if not self.api_key:
            logger.error("PINECONE_API_KEY not found in environment variables")
            raise ValueError("PINECONE_API_KEY is required")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize embeddings
        try:
            if GoogleGenerativeAIEmbeddings:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
                logger.info("Initialized Google Generative AI embeddings")
            else:
                raise ImportError("GoogleGenerativeAIEmbeddings not available")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            # Fallback to mock embeddings
            from .vector_store_manager import MockEmbeddings
            self.embeddings = MockEmbeddings()
        
        # Initialize or create index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or create Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # Google embeddings dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.region
                    )
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
            
            # Get index reference
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {e}")
            raise
    
    def create_vector_store(self, index_name: str = None, documents: List[Document] = None) -> PineconeVectorStore:
        """Create a Pinecone vector store"""
        try:
            if index_name and index_name != self.index_name:
                # Handle different index name if needed
                logger.warning(f"Requested index {index_name}, using configured index {self.index_name}")
            
            # Create PineconeVectorStore
            vector_store = PineconeVectorStore(
                index=self.index,
                embedding=self.embeddings,
                text_key="text"
            )
            
            # Add documents if provided
            if documents:
                logger.info(f"Adding {len(documents)} documents to vector store")
                vector_store.add_documents(documents)
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            # Fallback to mock vector store
            from .vector_store_manager import MockVectorStore
            return MockVectorStore(documents)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0.0)
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"total_vector_count": 0, "dimension": 0, "index_fullness": 0.0}
    
    def delete_index(self, index_name: str = None):
        """Delete Pinecone index"""
        try:
            name_to_delete = index_name or self.index_name
            self.pc.delete_index(name_to_delete)
            logger.info(f"Deleted Pinecone index: {name_to_delete}")
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)
            
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0
            
            similarity = dot_product / (norm_vec1 * norm_vec2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0