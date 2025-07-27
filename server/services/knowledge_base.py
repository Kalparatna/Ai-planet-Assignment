import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeEmbeddings
from langchain_core.documents import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from datasets import load_dataset

# Create a custom retriever class since ContextualCompressionRetriever is not available in this version
class CustomContextualRetriever:
    def __init__(self, base_compressor, base_retriever):
        self.base_compressor = base_compressor
        self.base_retriever = base_retriever
        
    def get_relevant_documents(self, query):
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
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.math_data_file = "data/math_problems.json"
        self.jee_bench_file = "data/jee_bench_data.json"
        
        # Pinecone configuration
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "math-routing-agent")
        self.jee_index_name = "jee-bench-problems"
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.cloud = os.getenv("PINECONE_CLOUD", "aws")
        self.embedding_model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize embedding model with fallback
        try:
            # Try Pinecone's native embedding model first
            self.embeddings = PineconeEmbeddings(
                api_key=self.pinecone_api_key,
                model=self.embedding_model_name  # Uses "llama-text-embed-v2" from .env
            )
            logger.info(f"Using Pinecone embeddings with model: {self.embedding_model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Pinecone embeddings: {e}")
            # Fallback to HuggingFace embeddings
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Using HuggingFace embeddings as fallback")
        
        # Initialize vector stores
        self._initialize_vector_store()
        self._initialize_jee_bench()
        
        # Initialize LLM for contextual compression
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Create compressor for better retrieval
        self.compressor = LLMChainExtractor.from_llm(self.llm)
    
    def _initialize_vector_store(self):
        """Initialize the Pinecone vector store with math problems and solutions"""
        try:
            # Check if Pinecone index exists, create if not
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                # Get the dimension for the Pinecone embedding model
                model_dimension = self._get_model_dimension(self.embedding_model_name)
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=model_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.environment
                    )
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Get the index
            index = self.pc.Index(self.index_name)
            
            # Initialize PineconeVectorStore
            self.vector_store = PineconeVectorStore(
                index=index,
                embedding=self.embeddings,
                text_key="text"
            )
            
            # Check if index is empty and populate with sample data
            index_stats = index.describe_index_stats()
            if index_stats['total_vector_count'] == 0:
                logger.info("Index is empty, populating with sample data...")
                
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
                
                # Add documents to Pinecone
                self.vector_store.add_documents(split_documents)
                logger.info(f"Added {len(split_documents)} documents to Pinecone index")
            else:
                logger.info(f"Loaded existing Pinecone index with {index_stats['total_vector_count']} vectors")
        
        except Exception as e:
            logger.error(f"Error initializing Pinecone vector store: {e}")
            # Fallback to local embeddings if Pinecone fails
            logger.warning("Falling back to in-memory vector store")
            self.vector_store = None
    
    def _initialize_jee_bench(self):
        """Initialize JEE Bench dataset from Hugging Face"""
        try:
            # Check if JEE Bench index exists, create if not
            if self.jee_index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating JEE Bench Pinecone index: {self.jee_index_name}")
                model_dimension = self._get_model_dimension(self.embedding_model_name)
                
                self.pc.create_index(
                    name=self.jee_index_name,
                    dimension=model_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.environment
                    )
                )
                logger.info(f"Created JEE Bench Pinecone index: {self.jee_index_name}")
            
            # Get the index
            jee_index = self.pc.Index(self.jee_index_name)
            
            # Initialize PineconeVectorStore for JEE Bench
            self.jee_vector_store = PineconeVectorStore(
                index=jee_index,
                embedding=self.embeddings,
                text_key="text"
            )
            
            # Check if index is empty and populate with JEE Bench data
            index_stats = jee_index.describe_index_stats()
            if index_stats['total_vector_count'] == 0:
                logger.info("JEE Bench index is empty, loading from Hugging Face...")
                self._load_jee_bench_data()
            else:
                logger.info(f"Loaded existing JEE Bench index with {index_stats['total_vector_count']} vectors")
                
        except Exception as e:
            logger.error(f"Error initializing JEE Bench: {e}")
            self.jee_vector_store = None
    
    def _load_jee_bench_data(self):
        """Load JEE Bench dataset from Hugging Face - FIXED VERSION"""
        try:
            logger.info("Loading JEE Bench dataset from Hugging Face...")
            
            # Load dataset from Hugging Face
            dataset = load_dataset("daman1209arora/jeebench")
            
            # Process the dataset
            documents = []
            jee_data = []
            total_processed = 0
            
            # Subject mapping
            subject_mapping = {
                'phy': 'Physics',
                'chem': 'Chemistry', 
                'math': 'Mathematics',
                'maths': 'Mathematics'
            }
            
            for split_name, split_data in dataset.items():
                logger.info(f"Processing {split_name} split with {len(split_data)} examples")
                
                for idx, example in enumerate(split_data):
                    try:
                        # Extract fields from the actual dataset structure
                        question = example.get('question', '').strip()
                        gold_answer = example.get('gold', '').strip()
                        subject_code = example.get('subject', 'math').strip()
                        question_type = example.get('type', 'MCQ').strip()
                        description = example.get('description', '').strip()
                        
                        # Map subject code to full name
                        subject = subject_mapping.get(subject_code, 'Mathematics')
                        
                        # Only process if we have a question
                        if question and len(question) > 20:
                            # Create a solution based on the gold answer
                            if gold_answer:
                                if question_type == 'MCQ':
                                    solution = f"The correct answer is option ({gold_answer}). This is a multiple choice question from {description}."
                                elif question_type == 'MCQ(multiple)':
                                    solution = f"The correct answers are options ({gold_answer}). This is a multiple choice question with multiple correct answers from {description}."
                                else:
                                    solution = f"Answer: {gold_answer}. From {description}."
                            else:
                                solution = f"This is a {question_type} question from {description}. Please solve step by step."
                            
                            # Create document content
                            content = f"Problem: {question}\nSolution: {solution}"
                            
                            # Create metadata
                            metadata = {
                                "problem_id": f"jee-{split_name}-{idx}",
                                "category": subject,
                                "topic": f"{subject} - JEE Level",
                                "difficulty": "JEE Level",
                                "source": "JEE Bench Dataset",
                                "split": split_name,
                                "question_type": question_type,
                                "gold_answer": gold_answer
                            }
                            
                            documents.append(Document(page_content=content, metadata=metadata))
                            
                            # Also save to local file for backup
                            jee_data.append({
                                "id": f"jee-{split_name}-{idx}",
                                "problem": question,
                                "solution": solution,
                                "category": subject,
                                "topic": f"{subject} - JEE Level",
                                "difficulty": "JEE Level",
                                "source": "JEE Bench Dataset",
                                "split": split_name,
                                "question_type": question_type,
                                "gold_answer": gold_answer
                            })
                            
                            total_processed += 1
                            
                            # Log progress every 100 items
                            if total_processed % 100 == 0:
                                logger.info(f"Processed {total_processed} valid examples...")
                    
                    except Exception as e:
                        logger.warning(f"Error processing example {idx} in {split_name}: {e}")
                        continue
            
            logger.info(f"Total valid examples processed: {total_processed}")
            
            if total_processed == 0:
                logger.error("No valid examples found in dataset!")
                return
            
            # Split documents if needed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
            split_documents = text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(split_documents)} document chunks")
            
            # Add documents to Pinecone in batches
            if self.jee_vector_store and split_documents:
                batch_size = 50  # Smaller batch size for reliability
                total_batches = (len(split_documents) + batch_size - 1) // batch_size
                
                for i in range(0, len(split_documents), batch_size):
                    batch = split_documents[i:i + batch_size]
                    try:
                        self.jee_vector_store.add_documents(batch)
                        batch_num = i // batch_size + 1
                        logger.info(f"Added batch {batch_num}/{total_batches} ({len(batch)} documents)")
                    except Exception as e:
                        logger.error(f"Error adding batch {batch_num}: {e}")
                        continue
            
            # Save to local file
            with open(self.jee_bench_file, "w", encoding='utf-8') as f:
                json.dump(jee_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully loaded {len(split_documents)} JEE Bench problems to vector store")
            logger.info(f"Saved {len(jee_data)} problems to local file: {self.jee_bench_file}")
            
        except Exception as e:
            logger.error(f"Error loading JEE Bench data: {e}")
            # Create empty file if loading fails
            with open(self.jee_bench_file, "w") as f:
                json.dump([], f)
    
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
    
    def _get_model_dimension(self, model_name: str) -> int:
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
            "llama-text-embed-v2": 4096,  # Your model from .env
            "text-embedding-gecko": 768,
            "text-embedding-gecko-multilingual": 768
        }
        
        return model_dimensions.get(model_name, 1024)  # Default to 1024 for most Pinecone models
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)
    
    def _classify_query(self, query: str) -> str:
        """Classify query type for adaptive threshold"""
        query_lower = query.lower()
        
        # Check for specific scientific terms
        specific_terms = ['planck', 'photoelectric', 'electromagnetic', 'quantum', 'derivative', 'integral', 'momentum', 'energy']
        if any(term in query_lower for term in specific_terms):
            return 'specific_term'
        
        # Check for mathematical concepts
        math_concepts = ['equation', 'function', 'calculus', 'algebra', 'geometry', 'probability', 'solve', 'find']
        if any(concept in query_lower for concept in math_concepts):
            return 'mathematical_concept'
        
        # Check for general subjects
        if query_lower in ['physics', 'chemistry', 'mathematics', 'math']:
            return 'general_subject'
        
        return 'default'
    
    def _get_adaptive_threshold(self, query_type: str) -> float:
        """Get adaptive threshold based on query type"""
        thresholds = {
            'specific_term': 0.35,      # For specific scientific terms
            'general_subject': 0.25,    # For general subjects  
            'mathematical_concept': 0.30, # For math concepts
            'default': 0.25
        }
        return thresholds.get(query_type, 0.25)
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with related terms for better matching"""
        query_lower = query.lower()
        expanded_queries = [query]
        
        # Subject-specific keywords
        subject_keywords = {
            'physics': ['force', 'energy', 'momentum', 'electric', 'magnetic'],
            'chemistry': ['reaction', 'bond', 'molecule', 'acid', 'base'],
            'mathematics': ['equation', 'function', 'derivative', 'integral', 'algebra']
        }
        
        # Add subject-specific expansions
        for subject, keywords in subject_keywords.items():
            if subject in query_lower:
                expanded_queries.extend([f"{query} {kw}" for kw in keywords[:2]])
                break
        
        # Add common mathematical terms
        if any(term in query_lower for term in ['solve', 'find', 'calculate']):
            expanded_queries.append(f"{query} problem")
        
        return expanded_queries[:4]  # Limit to 4 variations
    
    def _is_query_relevant_to_problem(self, query: str, problem: str) -> bool:
        """Check if the retrieved problem is actually relevant to the query"""
        query_lower = query.lower()
        problem_lower = problem.lower()
        
        # Extract key terms from query
        query_terms = set(query_lower.split())
        
        # Remove common words
        stop_words = {'what', 'is', 'the', 'find', 'solve', 'calculate', 'determine', 'of', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with'}
        query_terms = query_terms - stop_words
        
        # Check for mathematical operations/concepts
        math_operations = {
            'square': ['²', 'square', 'squared'],
            'cube': ['³', 'cube', 'cubed'], 
            'derivative': ['derivative', 'differentiate', 'diff'],
            'integral': ['integral', 'integrate', 'integration'],
            'equation': ['equation', 'solve', '='],
            'area': ['area', 'surface'],
            'volume': ['volume', 'capacity'],
            'probability': ['probability', 'chance', 'odds']
        }
        
        # Simple queries that should get direct answers, not JEE problems
        simple_patterns = [
            r'\d+\s*[\+\-\*\/\^²³]\s*\d+',  # Simple arithmetic like "4²", "2+3"
            r'what\s+is\s+\d+',  # "what is 4²"
            r'area\s+of\s+(circle|square|triangle)\s+with',  # Basic geometry
            r'derivative\s+of\s+[x\d\+\-\*\/\^]+',  # Simple derivatives
        ]
        
        import re
        for pattern in simple_patterns:
            if re.search(pattern, query_lower):
                # This is a simple query - only match if problem is very similar
                return len(query_terms.intersection(set(problem_lower.split()))) >= len(query_terms) * 0.7
        
        # For complex queries, check if key terms appear in problem
        if len(query_terms) <= 2:
            # Short queries need high overlap
            return len(query_terms.intersection(set(problem_lower.split()))) >= len(query_terms) * 0.8
        else:
            # Longer queries need moderate overlap
            return len(query_terms.intersection(set(problem_lower.split()))) >= len(query_terms) * 0.5

    async def query_jee_bench(self, query: str) -> Dict[str, Any]:
        """Query the JEE Bench dataset with improved relevance checking"""
        try:
            if not self.jee_vector_store:
                return {"found": False}
            
            # Classify query and get appropriate threshold
            query_type = self._classify_query(query)
            threshold = self._get_adaptive_threshold(query_type)
            
            # For simple arithmetic queries, use higher threshold
            import re
            if re.search(r'\d+\s*[\+\-\*\/\^²³]\s*\d+', query.lower()) or 'what is' in query.lower():
                threshold = 0.6  # Much higher threshold for simple queries
            
            # Expand query for better matching
            expanded_queries = self._expand_query(query)
            
            best_result = None
            best_score = -1
            
            # Try each expanded query
            for exp_query in expanded_queries:
                try:
                    retriever = self.jee_vector_store.as_retriever(search_kwargs={"k": 5})
                    
                    # Skip compression to avoid API quota issues
                    try:
                        docs = retriever.invoke(exp_query)
                    except AttributeError:
                        docs = retriever.get_relevant_documents(exp_query)
                    
                    if docs:
                        # Calculate similarity for all docs
                        query_embedding = self.embeddings.embed_query(exp_query)
                        
                        for doc in docs:
                            doc_embedding = self.embeddings.embed_query(doc.page_content)
                            similarity = self._cosine_similarity(query_embedding, doc_embedding)
                            
                            # Check relevance before considering this result
                            problem_text = doc.page_content.split("Solution:", 1)[0].replace("Problem:", "").strip()
                            
                            if similarity > best_score and self._is_query_relevant_to_problem(query, problem_text):
                                best_score = similarity
                                best_result = {
                                    "doc": doc,
                                    "similarity": similarity,
                                    "query_used": exp_query
                                }
                
                except Exception as e:
                    logger.warning(f"Error with expanded query '{exp_query}': {e}")
                    continue
            
            # Check if we found something above threshold AND relevant
            if best_result and best_score >= threshold:
                doc = best_result["doc"]
                
                # Extract problem and solution
                content = doc.page_content
                parts = content.split("Solution:", 1)
                
                if len(parts) >= 2:
                    problem = parts[0].replace("Problem:", "").strip()
                    solution = parts[1].strip()
                    
                    # Additional relevance check - make sure this is actually helpful
                    if len(solution) > 20 and not solution.startswith("Answer:"):  # Avoid short/unhelpful answers
                        return {
                            "found": True,
                            "problem": problem,
                            "solution": solution,
                            "confidence": best_score,
                            "metadata": doc.metadata,
                            "category": doc.metadata.get("category", "Mathematics"),
                            "topic": doc.metadata.get("topic", "General"),
                            "query_type": query_type,
                            "threshold_used": threshold,
                            "references": [f"JEE Bench Dataset: {doc.metadata.get('category', 'Mathematics')} - {doc.metadata.get('topic', 'General')}"]
                        }
            
            return {"found": False, "reason": f"No relevant match found (best score: {best_score:.3f}, threshold: {threshold:.3f})"}
        
        except Exception as e:
            logger.error(f"Error querying JEE Bench: {e}")
            return {"found": False}
    
    async def generate_assignment(self, topic: str, difficulty: str = "Medium", num_problems: int = 5) -> Dict[str, Any]:
        """Generate assignment requirements based on topic and difficulty"""
        try:
            # Search for related problems in all sources
            search_queries = [
                f"{topic} problems",
                f"{topic} exercises",
                f"{topic} practice questions"
            ]
            
            all_problems = []
            sources_used = []
            
            # Search in JEE Bench first
            if self.jee_vector_store:
                for query in search_queries:
                    jee_retriever = self.jee_vector_store.as_retriever(search_kwargs={"k": 10})
                    try:
                        jee_docs = jee_retriever.invoke(query)
                    except AttributeError:
                        jee_docs = jee_retriever.get_relevant_documents(query)
                    
                    for doc in jee_docs:
                        if doc.metadata.get("topic", "").lower() in topic.lower() or topic.lower() in doc.page_content.lower():
                            all_problems.append({
                                "content": doc.page_content,
                                "source": "JEE Bench Dataset",
                                "category": doc.metadata.get("category", "Mathematics"),
                                "topic": doc.metadata.get("topic", "General"),
                                "difficulty": doc.metadata.get("difficulty", "JEE Level")
                            })
                            if "JEE Bench Dataset" not in sources_used:
                                sources_used.append("JEE Bench Dataset")
            
            # Search in knowledge base
            if self.vector_store:
                for query in search_queries:
                    kb_retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
                    try:
                        kb_docs = kb_retriever.invoke(query)
                    except AttributeError:
                        kb_docs = kb_retriever.get_relevant_documents(query)
                    
                    for doc in kb_docs:
                        if topic.lower() in doc.page_content.lower():
                            all_problems.append({
                                "content": doc.page_content,
                                "source": "Knowledge Base",
                                "category": doc.metadata.get("category", "Mathematics"),
                                "difficulty": doc.metadata.get("difficulty", "Medium")
                            })
                            if "Knowledge Base" not in sources_used:
                                sources_used.append("Knowledge Base")
            
            # Generate assignment using LLM
            assignment_prompt = f"""
            Create a comprehensive assignment for the topic: {topic}
            Difficulty Level: {difficulty}
            Number of Problems: {num_problems}
            
            Based on the following reference problems:
            {chr(10).join([f"- {prob['content'][:200]}..." for prob in all_problems[:10]])}
            
            Please create:
            1. Assignment Title
            2. Learning Objectives (3-5 objectives)
            3. Prerequisites
            4. {num_problems} practice problems with varying difficulty
            5. Grading rubric
            6. Estimated completion time
            7. Additional resources for study
            
            Format the response in a clear, structured manner suitable for students.
            """
            
            response = await self.llm.ainvoke(assignment_prompt)
            assignment_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "success": True,
                "assignment": assignment_content,
                "topic": topic,
                "difficulty": difficulty,
                "num_problems": num_problems,
                "sources_used": sources_used,
                "reference_problems_count": len(all_problems)
            }
            
        except Exception as e:
            logger.error(f"Error generating assignment: {e}")
            return {
                "success": False,
                "error": f"Failed to generate assignment: {str(e)}"
            }
    
    async def generate_requirements_document(self, project_type: str, subject: str, complexity: str = "Medium") -> Dict[str, Any]:
        """Generate requirements document for mathematical projects"""
        try:
            # Search for related content
            search_query = f"{subject} {project_type} requirements"
            
            reference_content = []
            sources_used = []
            
            # Search all available sources
            for vector_store, source_name in [(self.jee_vector_store, "JEE Bench"), (self.vector_store, "Knowledge Base")]:
                if vector_store:
                    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
                    docs = retriever.get_relevant_documents(search_query)
                    
                    for doc in docs:
                        reference_content.append(doc.page_content[:300])
                        if source_name not in sources_used:
                            sources_used.append(source_name)
            
            # Generate requirements document using LLM
            requirements_prompt = f"""
            Create a detailed requirements document for a {project_type} project in {subject}.
            Complexity Level: {complexity}
            
            Reference Content:
            {chr(10).join(reference_content[:5])}
            
            Please create a comprehensive requirements document including:
            
            1. PROJECT OVERVIEW
               - Project title and description
               - Objectives and goals
               - Scope and limitations
            
            2. FUNCTIONAL REQUIREMENTS
               - Core features and capabilities
               - User interactions and workflows
               - Input/output specifications
            
            3. TECHNICAL REQUIREMENTS
               - Mathematical concepts to be implemented
               - Algorithms and methods required
               - Performance requirements
               - Platform and technology constraints
            
            4. DELIVERABLES
               - Expected outputs and artifacts
               - Documentation requirements
               - Testing and validation criteria
            
            5. TIMELINE AND MILESTONES
               - Project phases
               - Key milestones and deadlines
               - Dependencies and critical path
            
            6. RESOURCES AND CONSTRAINTS
               - Required skills and knowledge
               - Tools and software needed
               - Budget and resource constraints
            
            7. EVALUATION CRITERIA
               - Success metrics
               - Quality standards
               - Acceptance criteria
            
            Format this as a professional requirements document suitable for academic or professional use.
            """
            
            response = await self.llm.ainvoke(requirements_prompt)
            requirements_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "success": True,
                "requirements_document": requirements_content,
                "project_type": project_type,
                "subject": subject,
                "complexity": complexity,
                "sources_used": sources_used,
                "generated_at": "2025-01-26"
            }
            
        except Exception as e:
            logger.error(f"Error generating requirements document: {e}")
            return {
                "success": False,
                "error": f"Failed to generate requirements document: {str(e)}"
            }
    
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