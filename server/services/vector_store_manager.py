"""
Vector Store Manager - Mock implementation without Pinecone dependencies
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Configure logging
logger = logging.getLogger(__name__)

# Mock classes to replace Pinecone dependencies
class MockEmbeddings:
    """Mock embeddings class that returns random vectors"""
    def __init__(self):
        self.dimension = 384
        logger.info("Using mock embeddings with dimension: 384")
    
    def embed_query(self, text):
        """Return a random embedding vector"""
        return np.random.rand(self.dimension)

class MockRetriever:
    """Mock retriever class"""
    def __init__(self, documents=None):
        self.documents = documents or []
    
    def get_relevant_documents(self, query):
        """Return empty list as we're not doing actual retrieval"""
        return []

class MockVectorStore:
    """Mock vector store class"""
    def __init__(self, documents=None):
        self.documents = documents or []
        self.embeddings = MockEmbeddings()
    
    def as_retriever(self, search_kwargs=None):
        """Return a mock retriever"""
        return MockRetriever(self.documents)
    
    def add_documents(self, documents):
        """Mock adding documents"""
        self.documents.extend(documents)
        logger.info(f"Mock added {len(documents)} documents")
    
    def similarity_search_with_score(self, query, k=5):
        """Mock similarity search that returns empty results"""
        return []

class VectorStoreManager:
    """Mock vector store manager that doesn't use Pinecone"""
    
    def __init__(self):
        logger.warning("Using mock VectorStoreManager without Pinecone")
        # Create a mock Pinecone client for compatibility
        self.pc = type('MockPinecone', (), {
            'Index': lambda _, name: type('MockIndex', (), {
                'describe_index_stats': lambda: {'total_vector_count': 0}
            })(),
            'list_indexes': lambda: type('MockIndexList', (), {'names': lambda: []})(),
        })()
        
        # Initialize mock embeddings
        self.embeddings = MockEmbeddings()
    
    def create_vector_store(self, index_name: str, documents: List[Document] = None) -> MockVectorStore:
        """Create a mock vector store"""
        logger.info(f"Creating mock vector store for index: {index_name}")
        return MockVectorStore(documents)
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)
            return dot_product / (norm_vec1 * norm_vec2)
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0