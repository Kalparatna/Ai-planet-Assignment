import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.retrievers.document_compressors import LLMChainExtractor

# Create a custom retriever class since ContextualCompressionRetriever is not available in this version
class CustomContextualRetriever:
    def __init__(self, base_compressor, base_retriever):
        self.base_compressor = base_compressor
        self.base_retriever = base_retriever
        
    def get_relevant_documents(self, query):
        # Get documents from base retriever
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
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.db_directory = "data/vectordb"
        self.math_data_file = "data/math_problems.json"
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs(self.db_directory, exist_ok=True)
        
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        
        # Initialize vector store
        self._initialize_vector_store()
        
        # Initialize LLM for contextual compression
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Create compressor for better retrieval
        self.compressor = LLMChainExtractor.from_llm(self.llm)
    
    def _initialize_vector_store(self):
        """Initialize the vector store with math problems and solutions"""
        try:
            # Check if vector store already exists
            if os.path.exists(os.path.join(self.db_directory, "chroma.sqlite3")):
                self.vector_store = Chroma(persist_directory=self.db_directory, embedding_function=self.embeddings)
                logger.info("Loaded existing vector store")
                return
            
            # Create sample math problems if file doesn't exist
            if not os.path.exists(self.math_data_file):
                self._create_sample_math_data()
            
            # Load math problems
            with open(self.math_data_file, "r") as f:
                math_data = json.load(f)
            
            # Prepare documents for vector store
            documents = []
            for item in math_data:
                # Create a document with the problem and solution
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
            
            # Create and persist the vector store
            self.vector_store = Chroma.from_documents(
                documents=split_documents,
                embedding=self.embeddings,
                persist_directory=self.db_directory
            )
            self.vector_store.persist()
            logger.info(f"Created vector store with {len(split_documents)} documents")
        
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            # Create an empty vector store as fallback
            self.vector_store = Chroma(persist_directory=self.db_directory, embedding_function=self.embeddings)
    
    def _create_sample_math_data(self):
        """Create sample math problems and solutions for the knowledge base"""
        sample_data = [
            {
                "id": "algebra-1",
                "problem": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
                "solution": "To solve the quadratic equation x^2 - 5x + 6 = 0, we can use the factoring method.\n\nStep 1: Identify the coefficients.\na = 1, b = -5, c = 6\n\nStep 2: Find two numbers that multiply to give 'c' (which is 6) and add up to 'b' (which is -5).\nThe numbers -2 and -3 multiply to give 6 and add up to -5.\n\nStep 3: Rewrite the middle term using these numbers.\nx^2 - 5x + 6 = x^2 - 2x - 3x + 6 = x(x - 2) - 3(x - 2) = (x - 2)(x - 3)\n\nStep 4: Set each factor equal to zero and solve.\nx - 2 = 0 → x = 2\nx - 3 = 0 → x = 3\n\nTherefore, the solutions to the equation x^2 - 5x + 6 = 0 are x = 2 and x = 3.",
                "category": "Algebra",
                "difficulty": "Easy",
                "tags": ["quadratic equation", "factoring", "algebra"]
            },
            {
                "id": "calculus-1",
                "problem": "Find the derivative of f(x) = x^3 - 4x^2 + 7x - 9",
                "solution": "To find the derivative of f(x) = x^3 - 4x^2 + 7x - 9, we'll use the power rule and the sum rule of differentiation.\n\nThe power rule states that if f(x) = x^n, then f'(x) = n·x^(n-1).\nThe sum rule states that the derivative of a sum is the sum of the derivatives.\n\nLet's differentiate each term:\n\nFor x^3: f'(x) = 3x^2\nFor -4x^2: f'(x) = -4 · 2x = -8x\nFor 7x: f'(x) = 7\nFor -9: f'(x) = 0 (the derivative of a constant is zero)\n\nCombining all terms:\nf'(x) = 3x^2 - 8x + 7\n\nTherefore, the derivative of f(x) = x^3 - 4x^2 + 7x - 9 is f'(x) = 3x^2 - 8x + 7.",
                "category": "Calculus",
                "difficulty": "Medium",
                "tags": ["calculus", "derivative", "polynomial"]
            },
            {
                "id": "geometry-1",
                "problem": "Find the area of a circle with radius 5 cm.",
                "solution": "To find the area of a circle, we use the formula: A = πr², where r is the radius.\n\nGiven information:\n- Radius (r) = 5 cm\n\nStep 1: Substitute the radius into the formula.\nA = π × 5²\nA = π × 25\n\nStep 2: Calculate the result.\nA = 25π cm²\n\nIf we use π ≈ 3.14159, then:\nA ≈ 25 × 3.14159\nA ≈ 78.54 cm²\n\nTherefore, the area of the circle with radius 5 cm is 25π cm² or approximately 78.54 cm².",
                "category": "Geometry",
                "difficulty": "Easy",
                "tags": ["geometry", "circle", "area"]
            },
            {
                "id": "trigonometry-1",
                "problem": "Prove the identity: sin²θ + cos²θ = 1",
                "solution": "To prove the identity sin²θ + cos²θ = 1, we'll use the definitions of sine and cosine in terms of a right triangle.\n\nIn a right triangle with hypotenuse of length 1 (unit circle):\n- sin θ is the length of the opposite side\n- cos θ is the length of the adjacent side\n\nBy the Pythagorean theorem, in a right triangle:\n(opposite)² + (adjacent)² = (hypotenuse)²\n\nSubstituting our definitions:\n(sin θ)² + (cos θ)² = 1²\nsin²θ + cos²θ = 1\n\nThis proves the identity sin²θ + cos²θ = 1, which is one of the fundamental Pythagorean identities in trigonometry.",
                "category": "Trigonometry",
                "difficulty": "Medium",
                "tags": ["trigonometry", "identity", "pythagorean identity"]
            },
            {
                "id": "statistics-1",
                "problem": "Calculate the mean, median, and mode of the following data set: 4, 7, 2, 8, 4, 9, 4, 6, 3",
                "solution": "Let's calculate the mean, median, and mode for the data set: 4, 7, 2, 8, 4, 9, 4, 6, 3\n\nStep 1: Calculate the mean (average).\nMean = (sum of all values) ÷ (number of values)\nMean = (4 + 7 + 2 + 8 + 4 + 9 + 4 + 6 + 3) ÷ 9\nMean = 47 ÷ 9\nMean ≈ 5.22\n\nStep 2: Calculate the median (middle value when arranged in order).\nFirst, arrange the data in ascending order: 2, 3, 4, 4, 4, 6, 7, 8, 9\nSince there are 9 values (odd number), the median is the 5th value.\nMedian = 4\n\nStep 3: Calculate the mode (most frequently occurring value).\nCounting the frequency of each value:\n2 appears 1 time\n3 appears 1 time\n4 appears 3 times\n6 appears 1 time\n7 appears 1 time\n8 appears 1 time\n9 appears 1 time\n\nThe value 4 appears most frequently (3 times), so:\nMode = 4\n\nTherefore:\n- Mean ≈ 5.22\n- Median = 4\n- Mode = 4",
                "category": "Statistics",
                "difficulty": "Easy",
                "tags": ["statistics", "mean", "median", "mode"]
            }
        ]
        
        # Save sample data
        with open(self.math_data_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        logger.info("Created sample math data")
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Query the knowledge base for a mathematical problem"""
        try:
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
            query_embedding = self.embeddings.embed_query(query)
            best_doc = None
            best_score = -1
            
            for doc in docs:
                doc_embedding = self.embeddings.embed_query(doc.page_content)
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_doc = doc
            
            # Check if similarity is high enough
            if best_score < 0.75:  # Threshold for considering it a match
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
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)
    
    async def add_to_knowledge_base(self, problem: str, solution: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a new problem and solution to the knowledge base"""
        try:
            if metadata is None:
                metadata = {}
            
            # Create document
            content = f"Problem: {problem}\nSolution: {solution}"
            document = Document(page_content=content, metadata=metadata)
            
            # Add to vector store
            self.vector_store.add_documents([document])
            self.vector_store.persist()
            
            # Also add to the JSON file for backup
            if os.path.exists(self.math_data_file):
                with open(self.math_data_file, "r") as f:
                    math_data = json.load(f)
                
                # Generate ID
                category = metadata.get("category", "general").lower()
                new_id = f"{category}-{len(math_data) + 1}"
                
                # Create entry
                entry = {
                    "id": new_id,
                    "problem": problem,
                    "solution": solution,
                    "category": metadata.get("category", "General"),
                    "difficulty": metadata.get("difficulty", "Medium"),
                    "tags": metadata.get("tags", []).split(",") if isinstance(metadata.get("tags", ""), str) else metadata.get("tags", [])
                }
                
                math_data.append(entry)
                
                with open(self.math_data_file, "w") as f:
                    json.dump(math_data, f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {e}")
            return False