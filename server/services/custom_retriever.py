"""
Custom Retriever - Handles document retrieval with compression
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

class CustomContextualRetriever:
    """Custom retriever class for document compression and retrieval"""
    
    def __init__(self, base_compressor, base_retriever):
        self.base_compressor = base_compressor
        self.base_retriever = base_retriever
        
    def get_relevant_documents(self, query):
        """Get relevant documents with optional compression"""
        # Use the new invoke method instead of deprecated get_relevant_documents
        try:
            docs = self.base_retriever.invoke(query)
        except AttributeError:
            # Fallback to old method if invoke is not available
            docs = self.base_retriever.get_relevant_documents(query)
        
        # Apply compression if available
        if self.base_compressor:
            try:
                compressed_docs = self.base_compressor.compress_documents(docs, query)
                return compressed_docs
            except Exception as e:
                logger.warning(f"Error in document compression: {e}")
                return docs
        return docs