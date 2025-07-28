"""
Vector Store Manager - Handles Pinecone vector database operations
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeEmbeddings
from langchain_core.documents import Document

# Configure logging
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages Pinecone vector store operations"""
    
    def __init__(self):
        # Pinecone configuration
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.cloud = os.getenv("PINECONE_CLOUD", "aws")
        self.embedding_model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize embedding model with fallback
        self.embeddings = self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embedding model with fallback"""
        try:
            # Try Pinecone's native embedding model first
            embeddings = PineconeEmbeddings(
                api_key=self.pinecone_api_key,
                model=self.embedding_model_name
            )
            logger.info(f"Using Pinecone embeddings with model: {self.embedding_model_name}")
            return embeddings
        except Exception as e:
            logger.warning(f"Failed to initialize Pinecone embeddings: {e}")
            # Fallback to HuggingFace embeddings
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Using HuggingFace embeddings as fallback")
            return embeddings
    
    def create_vector_store(self, index_name: str, documents: List[Document] = None) -> PineconeVectorStore:
        """Create or get existing vector store"""
        try:
            # Check if index exists, create if not
            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                model_dimension = self._get_model_dimension()
                
                self.pc.create_index(
                    name=index_name,
                    dimension=model_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.environment
                    )
                )
                logger.info(f"Created Pinecone index: {index_name}")
            
            # Get the index
            index = self.pc.Index(index_name)
            
            # Initialize PineconeVectorStore
            vector_store = PineconeVectorStore(
                index=index,
                embedding=self.embeddings,
                text_key="text"
            )
            
            # Add documents if provided and index is empty
            if documents:
                index_stats = index.describe_index_stats()
                if index_stats['total_vector_count'] == 0:
                    logger.info(f"Adding {len(documents)} documents to empty index...")
                    vector_store.add_documents(documents)
                    logger.info(f"Added documents to index: {index_name}")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return None
    
    def _get_model_dimension(self) -> int:
        """Get the dimension for embedding model"""
        # Check if we're using HuggingFace fallback
        if hasattr(self.embeddings, 'model_name') and 'all-MiniLM-L6-v2' in str(self.embeddings.model_name):
            return 384  # HuggingFace sentence-transformers dimension
        
        # Test actual embedding dimension by creating a sample embedding
        try:
            test_embedding = self.embeddings.embed_query("test")
            actual_dimension = len(test_embedding)
            logger.info(f"Detected embedding dimension: {actual_dimension}")
            return actual_dimension
        except Exception as e:
            logger.warning(f"Could not detect embedding dimension: {e}")
        
        # Pinecone embedding model dimensions (fallback)
        model_dimensions = {
            "multilingual-e5-large": 1024,
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "llama-text-embed-v2": 4096,
            "text-embedding-gecko": 768,
            "text-embedding-gecko-multilingual": 768
        }
        
        return model_dimensions.get(self.embedding_model_name, 1024)
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)