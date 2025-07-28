"""
Knowledge Base Service - Main service for mathematical knowledge retrieval
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_google_genai import ChatGoogleGenerativeAI

# Import our modular components
from .vector_store_manager import VectorStoreManager
from .jee_bench_loader import JEEBenchLoader
from .query_processor import QueryProcessor
from .content_generator import ContentGenerator
from .custom_retriever import CustomContextualRetriever
from .sample_data_generator import SampleDataGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Main service for mathematical knowledge base operations"""
    
    def __init__(self):
        self.math_data_file = "data/math_problems.json"
        self.jee_bench_file = "data/jee_bench_data.json"
        
        # Pinecone configuration
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "math-routing-agent")
        self.jee_index_name = "jee-bench-problems"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize components
        self.vector_manager = VectorStoreManager()
        self.jee_loader = JEEBenchLoader(self.jee_bench_file)
        self.query_processor = QueryProcessor()
        self.content_generator = ContentGenerator()
        self.sample_generator = SampleDataGenerator()
        
        # Initialize vector stores
        self._initialize_vector_store()
        self._initialize_jee_bench()
        
        # Initialize LLM for contextual compression
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create compressor for better retrieval
        self.compressor = LLMChainExtractor.from_llm(self.llm)
        
        # Expose Pinecone client for external access (needed by math_router.py)
        self.pc = self.vector_manager.pc
    
    def _initialize_vector_store(self):
        """Initialize the main knowledge base vector store"""
        try:
            # Create sample data if file doesn't exist
            if not os.path.exists(self.math_data_file):
                self.sample_generator.create_sample_math_data(self.math_data_file)
            
            # Load math problems
            with open(self.math_data_file, "r") as f:
                math_data = json.load(f)
            
            # Prepare documents for vector store
            documents = []
            for item in math_data:
                content = f"Problem: {item['problem']}\nSolution: {item['solution']}"
                metadata = {
                    "problem_id": item.get("id", ""),
                    "category": item.get("category", ""),
                    "difficulty": item.get("difficulty", ""),
                    "tags": ",".join(item.get("tags", []))
                }
                documents.append(Document(page_content=content, metadata=metadata))
            
            # Split documents if needed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            split_documents = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = self.vector_manager.create_vector_store(
                self.index_name, 
                split_documents
            )
            
            if self.vector_store:
                logger.info(f"Initialized knowledge base vector store with {len(split_documents)} documents")
            else:
                logger.error("Failed to initialize knowledge base vector store")
        
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = None
    
    def _initialize_jee_bench(self):
        """Initialize JEE Bench dataset vector store"""
        try:
            # Check if we need to load JEE Bench data
            existing_store = self.vector_manager.create_vector_store(self.jee_index_name)
            
            if existing_store:
                # Check if index is empty
                index = self.vector_manager.pc.Index(self.jee_index_name)
                index_stats = index.describe_index_stats()
                
                if index_stats['total_vector_count'] == 0:
                    logger.info("JEE Bench index is empty, loading from Hugging Face...")
                    documents = self.jee_loader.load_jee_bench_data()
                    
                    if documents:
                        # Add documents in batches
                        batch_size = 50
                        for i in range(0, len(documents), batch_size):
                            batch = documents[i:i + batch_size]
                            try:
                                existing_store.add_documents(batch)
                                logger.info(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                            except Exception as e:
                                logger.error(f"Error adding batch: {e}")
                                continue
                else:
                    logger.info(f"JEE Bench index already has {index_stats['total_vector_count']} vectors")
                
                self.jee_vector_store = existing_store
            else:
                logger.error("Failed to create JEE Bench vector store")
                self.jee_vector_store = None
                
        except Exception as e:
            logger.error(f"Error initializing JEE Bench: {e}")
            self.jee_vector_store = None
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Query the knowledge base for a mathematical problem"""
        try:
            if not self.vector_store:
                return {"found": False}
            
            # Create retriever with compression for better results
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            compression_retriever = CustomContextualRetriever(
                base_compressor=self.compressor,
                base_retriever=retriever
            )
            
            # Retrieve relevant documents
            docs = compression_retriever.get_relevant_documents(query)
            
            if not docs:
                return {"found": False}
            
            # Calculate similarity score
            query_embedding = self.vector_manager.embeddings.embed_query(query)
            best_doc = None
            best_score = -1
            
            for doc in docs:
                doc_embedding = self.vector_manager.embeddings.embed_query(doc.page_content)
                similarity = self.vector_manager.cosine_similarity(query_embedding, doc_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_doc = doc
            
            # Check if similarity is high enough
            if best_score < 0.75:
                return {"found": False}
            
            # Extract problem and solution
            content = best_doc.page_content
            parts = content.split("Solution:", 1)
            
            if len(parts) < 2:
                return {"found": False}
            
            problem = parts[0].replace("Problem:", "").strip()
            solution = parts[1].strip()
            
            return {
                "found": True,
                "problem": problem,
                "solution": solution,
                "confidence": best_score,
                "metadata": best_doc.metadata,
                "references": [f"Knowledge Base: {best_doc.metadata.get('category', 'Mathematics')}"]
            }
        
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {"found": False}
    
    async def query_jee_bench(self, query: str) -> Dict[str, Any]:
        """Query the JEE Bench dataset"""
        try:
            if not self.jee_vector_store:
                return {"found": False}
            
            # Classify query and get appropriate threshold
            query_type = self.query_processor.classify_query(query)
            threshold = self.query_processor.get_adaptive_threshold(query_type)
            
            # Expand query for better matching
            expanded_queries = self.query_processor.expand_query(query)
            
            best_result = None
            best_score = 0
            
            # Try each expanded query
            for expanded_query in expanded_queries:
                try:
                    # Search with higher k for better results
                    results = self.jee_vector_store.similarity_search_with_score(
                        expanded_query, k=10
                    )
                    
                    for doc, score in results:
                        # Check relevance
                        if self.query_processor.is_query_relevant_to_problem(query, doc.page_content):
                            if score > best_score and score >= threshold:
                                best_score = score
                                best_result = doc
                
                except Exception as e:
                    logger.warning(f"Error searching with query '{expanded_query}': {e}")
                    continue
            
            if best_result and best_score >= threshold:
                # Extract problem and solution
                content = best_result.page_content
                parts = content.split("Solution:", 1)
                
                if len(parts) >= 2:
                    problem = parts[0].replace("Problem:", "").strip()
                    solution = parts[1].strip()
                    
                    return {
                        "found": True,
                        "problem": problem,
                        "solution": solution,
                        "confidence": best_score,
                        "metadata": best_result.metadata,
                        "references": [f"JEE Bench: {best_result.metadata.get('category', 'Mathematics')}"]
                    }
            
            return {"found": False}
            
        except Exception as e:
            logger.error(f"Error querying JEE Bench: {e}")
            return {"found": False}
    
    async def generate_assignment(self, topic: str, difficulty: str = "Medium", num_problems: int = 5) -> Dict[str, Any]:
        """Generate assignment using content generator"""
        return await self.content_generator.generate_assignment(topic, difficulty, num_problems)
    
    async def generate_requirements_document(self, project_type: str, subject: str, complexity: str = "Medium") -> Dict[str, Any]:
        """Generate requirements document using content generator"""
        return await self.content_generator.generate_requirements_document(project_type, subject, complexity)