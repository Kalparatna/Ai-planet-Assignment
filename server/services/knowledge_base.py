"""
Knowledge Base Service - Main service for mathematical knowledge retrieval
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
# from langchain.retrievers.document_compressors import LLMChainExtractor  # Commented out due to version conflicts
# from langchain_google_genai import ChatGoogleGenerativeAI  # Commented out due to version conflicts
from services.caching_service import cached

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .pinecone_vector_store import PineconeVectorStoreManager as VectorStoreManager
    logger.info("Using real Pinecone vector store")
except Exception as e:
    logger.warning(f"Pinecone not available, using mock: {e}")
    from .vector_store_manager import VectorStoreManager

from .jee_bench_loader import JEEBenchLoader
from .query_processor import QueryProcessor
from .content_generator import ContentGenerator
from .custom_retriever import CustomContextualRetriever
from .sample_data_generator import SampleDataGenerator
from .mongodb_service import mongodb_service

class KnowledgeBaseService:
    """Main service for mathematical knowledge base operations"""
    
    def __init__(self):
        self.math_data_file = "data/math_problems.json"
        self.jee_bench_file = "data/jee_bench_data.json"
        
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "math-routing-agent")
        self.jee_index_name = "jee-bench-problems"
        
        os.makedirs("data", exist_ok=True)
        
        self.vector_manager = VectorStoreManager()
        self.jee_loader = JEEBenchLoader(self.jee_bench_file)
        self.query_processor = QueryProcessor()
        self.content_generator = ContentGenerator()
        self.sample_generator = SampleDataGenerator()
        
        self._initialize_vector_store()
        # JEE bench initialization REMOVED per user requirements
        # self._initialize_jee_bench()
        
        # LLM initialization commented out due to version conflicts
        # try:
        #     self.llm = ChatGoogleGenerativeAI(
        #         model="gemini-2.5-flash", 
        #         google_api_key=os.getenv("GOOGLE_API_KEY")
        #     )
        # except Exception as e:
        #     logger.error(f"Error initializing LLM: {e}")
        self.llm = None
        
        # self.compressor = LLMChainExtractor.from_llm(self.llm)  # Commented out due to version conflicts
        self.compressor = None
        self.pc = self.vector_manager.pc
    
    def _initialize_vector_store(self):
        """Initialize the main knowledge base vector store with adaptive chunking"""
        try:
            # Import adaptive chunking service
            from .adaptive_chunking import AdaptiveChunkingService
            self.chunking_service = AdaptiveChunkingService()
            
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
            
            # Use adaptive chunking to split documents
            split_documents = self.chunking_service.chunk_documents(documents, "math_problem")
            
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
        """Initialize JEE Bench dataset vector store with adaptive chunking"""
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
                        # Use adaptive chunking to split documents
                        documents = self.chunking_service.chunk_documents(documents, "math_problem")
                        
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
    
    @cached(prefix="kb_query", ttl=3600)  # Cache for 1 hour
    async def query(self, query: str) -> Dict[str, Any]:
        """Query the knowledge base for a mathematical problem with MongoDB first, then vector store"""
        try:
            # Import performance monitor
            from .performance_monitor import PerformanceMonitor
            performance_monitor = PerformanceMonitor()
            request_id = f"kb_query_{hash(query)}"
            performance_monitor.start_request(request_id, "knowledge_base_query", query)
            
            # 🚀 ULTRA-FAST: Check MongoDB first (0.01-0.1 seconds)
            performance_monitor.log_stage(request_id, "mongodb_check_start")
            mongodb_result = await mongodb_service.get_math_solution(query)
            if mongodb_result and mongodb_result.get("found"):
                performance_monitor.log_stage(request_id, "mongodb_check_complete")
                performance_monitor.end_request(request_id, source="MongoDB")
                return {
                    "found": True,
                    "problem": query,
                    "solution": mongodb_result["solution"],
                    "confidence": mongodb_result.get("confidence", 0.9),
                    "references": ["MongoDB Cache - Ultra Fast Response"],
                    "source": "MongoDB"
                }
            performance_monitor.log_stage(request_id, "mongodb_check_complete")
            
            # Fallback to vector store if not in MongoDB
            if not self.vector_store:
                performance_monitor.end_request(request_id)
                return {"found": False}
            
            # Create retriever with compression for better results
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            compression_retriever = CustomContextualRetriever(
                base_compressor=self.compressor,
                base_retriever=retriever
            )
            
            # Retrieve relevant documents
            performance_monitor.log_stage(request_id, "retrieval_start")
            docs = compression_retriever.get_relevant_documents(query)
            performance_monitor.log_stage(request_id, "retrieval_complete")
            
            if not docs:
                performance_monitor.end_request(request_id)
                return {"found": False}
            
            # Calculate similarity score
            performance_monitor.log_stage(request_id, "similarity_calculation_start")
            query_embedding = self.vector_manager.embeddings.embed_query(query)
            best_doc = None
            best_score = -1
            
            for doc in docs:
                doc_embedding = self.vector_manager.embeddings.embed_query(doc.page_content)
                similarity = self.vector_manager.cosine_similarity(query_embedding, doc_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_doc = doc
            performance_monitor.log_stage(request_id, "similarity_calculation_complete")
            
            # Check if similarity is high enough
            if best_score < 0.75:
                performance_monitor.end_request(request_id)
                return {"found": False}
            
            # Extract problem and solution
            content = best_doc.page_content
            parts = content.split("Solution:", 1)
            
            if len(parts) < 2:
                performance_monitor.end_request(request_id)
                return {"found": False}
            
            problem = parts[0].replace("Problem:", "").strip()
            solution = parts[1].strip()
            
            performance_monitor.end_request(request_id)
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
            performance_monitor.end_request(request_id, error=str(e))
            return {"found": False}
    
    @cached(prefix="jee_query", ttl=3600)  # Cache for 1 hour
    async def query_jee_bench(self, query: str) -> Dict[str, Any]:
        """Query the JEE Bench dataset with caching and performance monitoring"""
        try:
            # Import performance monitor
            from .performance_monitor import PerformanceMonitor
            performance_monitor = PerformanceMonitor()
            request_id = f"jee_query_{hash(query)}"
            performance_monitor.start_request(request_id, "jee_bench_query", query)
            
            if not self.jee_vector_store:
                performance_monitor.end_request(request_id)
                return {"found": False}
            
            # Classify query and get appropriate threshold
            performance_monitor.log_stage(request_id, "query_classification_start")
            query_type = self.query_processor.classify_query(query)
            threshold = self.query_processor.get_adaptive_threshold(query_type)
            performance_monitor.log_stage(request_id, "query_classification_complete")
            
            # Expand query for better matching
            performance_monitor.log_stage(request_id, "query_expansion_start")
            expanded_queries = self.query_processor.expand_query(query)
            performance_monitor.log_stage(request_id, "query_expansion_complete")
            
            best_result = None
            best_score = 0
            
            # Try each expanded query
            performance_monitor.log_stage(request_id, "retrieval_start")
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
            performance_monitor.log_stage(request_id, "retrieval_complete")
            
            if best_result and best_score >= threshold:
                # Extract problem and solution
                content = best_result.page_content
                parts = content.split("Solution:", 1)
                
                if len(parts) >= 2:
                    problem = parts[0].replace("Problem:", "").strip()
                    solution = parts[1].strip()
                    
                    performance_monitor.end_request(request_id)
                    return {
                        "found": True,
                        "problem": problem,
                        "solution": solution,
                        "confidence": best_score,
                        "metadata": best_result.metadata,
                        "references": [f"JEE Bench: {best_result.metadata.get('category', 'Mathematics')}"]
                    }
            
            performance_monitor.end_request(request_id)
            return {"found": False}
            
        except Exception as e:
            logger.error(f"Error querying JEE Bench: {e}")
            performance_monitor.end_request(request_id, error=str(e))
            return {"found": False}
    
    async def generate_assignment(self, topic: str, difficulty: str = "Medium", num_problems: int = 5) -> Dict[str, Any]:
        """Generate assignment using content generator"""
        return await self.content_generator.generate_assignment(topic, difficulty, num_problems)
    
    async def generate_requirements_document(self, project_type: str, subject: str, complexity: str = "Medium") -> Dict[str, Any]:
        """Generate requirements document using content generator"""
        return await self.content_generator.generate_requirements_document(project_type, subject, complexity)