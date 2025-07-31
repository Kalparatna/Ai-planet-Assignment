import os
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import PyPDF2
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import numpy as np
# from langchain_google_genai import ChatGoogleGenerativeAI  # Commented out due to version conflicts
import aiofiles
from fastapi import UploadFile
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service for processing PDF files and extracting mathematical content"""
    
    def __init__(self):
        self.upload_dir = "data/uploads"
        self.processed_pdfs_file = "data/processed_pdfs.json"
        self.pdf_index_name = "math-pdf-documents"
        
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.processed_pdfs_file):
            with open(self.processed_pdfs_file, "w") as f:
                json.dump([], f)
        
        self.pinecone_api_key = None
        class MockEmbeddings:
            def __init__(self):
                self.dimension = 384
                logger.info(f"Using mock embeddings with dimension: {self.dimension}")
                
            def embed_documents(self, texts):
                return [np.random.rand(self.dimension).tolist() for _ in texts]
                
            def embed_query(self, text):
                return np.random.rand(self.dimension).tolist()
        
        self.embeddings = MockEmbeddings()
        logger.info("Using mock embeddings for PDF processing")
        
        class MockVectorStore:
            def __init__(self):
                self.documents = []
                logger.info("Using mock vector store for PDFs")
                
            def add_documents(self, documents):
                self.documents.extend(documents)
                return len(documents)
                
            def similarity_search(self, query, k=4):
                return self.documents[:min(k, len(self.documents))]
        
        self.vector_store = MockVectorStore()
        self.pdf_vector_store = self.vector_store
        logger.info("Initialized mock vector store for PDFs")
        
        # Use the working Gemini service instead of problematic LangChain
        from .gemini_service import gemini_service
        self.llm = gemini_service
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _initialize_pdf_vector_store(self):
        """Initialize mock vector store for PDF documents"""
        try:
            # We're using the mock vector store already initialized in __init__
            logger.info(f"Using mock vector store for PDF index: {self.pdf_index_name}")
            # The self.pdf_vector_store is already set in __init__
            logger.info("PDF mock vector store initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing PDF vector store: {e}")
            self.pdf_vector_store = None
    
    async def process_pdf_upload(self, file: UploadFile) -> Dict[str, Any]:
        """Process uploaded PDF file and extract content"""
        try:
            # Validate file
            if not file.filename.lower().endswith('.pdf'):
                return {
                    "success": False,
                    "error": "Only PDF files are supported",
                    "file_id": None
                }
            
            # Generate file ID
            file_content = await file.read()
            file_hash = hashlib.md5(file_content).hexdigest()
            file_id = f"pdf_{file_hash}_{int(datetime.now().timestamp())}"
            
            # Check if already processed
            if self._is_pdf_already_processed(file_hash):
                existing_pdf = self._get_processed_pdf_info(file_hash)
                return {
                    "success": True,
                    "message": "PDF already processed",
                    "file_id": existing_pdf.get("file_id"),
                    "filename": existing_pdf.get("filename"),
                    "pages": existing_pdf.get("pages"),
                    "chunks": existing_pdf.get("chunks")
                }
            
            # Save uploaded file temporarily
            temp_path = os.path.join(self.upload_dir, f"{file_id}.pdf")
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(file_content)
            
            # Extract text from PDF
            extracted_text = self._extract_text_from_pdf(temp_path)
            
            if not extracted_text.strip():
                os.remove(temp_path)
                return {
                    "success": False,
                    "error": "No text could be extracted from the PDF",
                    "file_id": None
                }
            
            # Process and chunk the text
            chunks = self._process_and_chunk_text(extracted_text, file_id, file.filename)
            
            # Store in vector database
            if self.pdf_vector_store and chunks:
                await self._store_chunks_in_vector_db(chunks)
            
            # Save processing info
            pdf_info = {
                "file_id": file_id,
                "filename": file.filename,
                "file_hash": file_hash,
                "upload_time": datetime.now().isoformat(),
                "file_path": temp_path,
                "pages": len(extracted_text.split('\f')),  # Rough page count
                "chunks": len(chunks),
                "text_length": len(extracted_text)
            }
            
            self._save_processed_pdf_info(pdf_info)
            
            return {
                "success": True,
                "message": "PDF processed successfully",
                "file_id": file_id,
                "filename": file.filename,
                "pages": pdf_info["pages"],
                "chunks": len(chunks),
                "text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF upload: {e}")
            return {
                "success": False,
                "error": f"Failed to process PDF: {str(e)}",
                "file_id": None
            }
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        # Try PyMuPDF first (better for complex layouts)
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text() + "\n\n"
            doc.close()
            
            if text.strip():
                return text
                
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
                    
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
        
        return text
    
    def _process_and_chunk_text(self, text: str, file_id: str, filename: str) -> List[Document]:
        """Process and chunk the extracted text"""
        try:
            # Clean the text
            cleaned_text = self._clean_extracted_text(text)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create Document objects
            documents = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Only add non-empty chunks
                    metadata = {
                        "file_id": file_id,
                        "filename": filename,
                        "chunk_index": i,
                        "source": "pdf_upload",
                        "upload_time": datetime.now().isoformat()
                    }
                    documents.append(Document(page_content=chunk, metadata=metadata))
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing and chunking text: {e}")
            return []
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text for better processing"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page breaks
        text = text.replace('\f', '\n')
        
        # Fix common OCR issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add space between number and letter
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Add space between letter and number
        
        # Clean up multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    async def _store_chunks_in_vector_db(self, chunks: List[Document]):
        """Store document chunks in vector database"""
        try:
            if self.pdf_vector_store:
                self.pdf_vector_store.add_documents(chunks)
                logger.info(f"Stored {len(chunks)} chunks in PDF vector database")
            else:
                logger.warning("PDF vector store not available, chunks not stored")
                
        except Exception as e:
            logger.error(f"Error storing chunks in vector database: {e}")
    
    async def query_pdf_content(self, query: str, file_id: Optional[str] = None) -> Dict[str, Any]:
        """Query content from uploaded PDFs"""
        try:
            if not self.pdf_vector_store:
                return {
                    "found": False,
                    "error": "PDF vector store not available"
                }
            
            # Create retriever
            retriever = self.pdf_vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
            
            # Add file_id filter if specified
            if file_id:
                retriever = self.pdf_vector_store.as_retriever(
                    search_kwargs={
                        "k": 5,
                        "filter": {"file_id": file_id}
                    }
                )
            
            # Retrieve relevant documents
            docs = retriever.get_relevant_documents(query)
            
            if not docs:
                return {"found": False}
            
            # Combine relevant chunks
            combined_content = ""
            sources = []
            
            for doc in docs:
                combined_content += doc.page_content + "\n\n"
                sources.append({
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "file_id": doc.metadata.get("file_id", "Unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                })
            
            # Generate answer using LLM if available
            if self.llm:
                answer = await self._generate_answer_from_pdf_content(query, combined_content)
            else:
                answer = f"Based on the uploaded PDF content:\n\n{combined_content[:1000]}..."
            
            return {
                "found": True,
                "answer": answer,
                "sources": sources,
                "confidence": 0.9,
                "source_type": "pdf_upload"
            }
            
        except Exception as e:
            logger.error(f"Error querying PDF content: {e}")
            return {
                "found": False,
                "error": f"Failed to query PDF content: {str(e)}"
            }
    
    async def _generate_answer_from_pdf_content(self, query: str, content: str) -> str:
        """Generate answer from PDF content using Gemini"""
        try:
            if not self.llm or not self.llm.is_available():
                return f"Based on the PDF content: {content[:500]}..."
            
            prompt = f"""
            Based on the following content from uploaded PDF documents, please answer the question step by step.
            
            Question: {query}
            
            PDF Content:
            {content}
            
            Please provide a clear, step-by-step mathematical solution if the question is mathematical in nature.
            If the content doesn't contain enough information to answer the question, please state that clearly.
            """
            
            response = await self.llm.generate_content(prompt)
            
            if response:
                return response
            else:
                return f"Based on the PDF content: {content[:500]}..."
                
        except Exception as e:
            logger.error(f"Error generating answer from PDF content: {e}")
            return f"Based on the PDF content: {content[:500]}..."
    
    def _is_pdf_already_processed(self, file_hash: str) -> bool:
        """Check if PDF with this hash has already been processed"""
        try:
            with open(self.processed_pdfs_file, 'r') as f:
                processed_pdfs = json.load(f)
            
            return any(pdf.get("file_hash") == file_hash for pdf in processed_pdfs)
            
        except Exception as e:
            logger.error(f"Error checking processed PDFs: {e}")
            return False
    
    def _get_processed_pdf_info(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get info about already processed PDF"""
        try:
            with open(self.processed_pdfs_file, 'r') as f:
                processed_pdfs = json.load(f)
            
            for pdf in processed_pdfs:
                if pdf.get("file_hash") == file_hash:
                    return pdf
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting processed PDF info: {e}")
            return None
    
    def _save_processed_pdf_info(self, pdf_info: Dict[str, Any]):
        """Save information about processed PDF"""
        try:
            with open(self.processed_pdfs_file, 'r') as f:
                processed_pdfs = json.load(f)
            
            processed_pdfs.append(pdf_info)
            
            with open(self.processed_pdfs_file, 'w') as f:
                json.dump(processed_pdfs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving processed PDF info: {e}")
    
    def get_uploaded_pdfs(self) -> List[Dict[str, Any]]:
        """Get list of all uploaded PDFs"""
        try:
            with open(self.processed_pdfs_file, 'r') as f:
                processed_pdfs = json.load(f)
            
            # Return summary info (without file paths for security)
            return [
                {
                    "file_id": pdf.get("file_id"),
                    "filename": pdf.get("filename"),
                    "upload_time": pdf.get("upload_time"),
                    "pages": pdf.get("pages"),
                    "chunks": pdf.get("chunks")
                }
                for pdf in processed_pdfs
            ]
            
        except Exception as e:
            logger.error(f"Error getting uploaded PDFs: {e}")
            return []
    
    async def delete_pdf(self, file_id: str) -> Dict[str, Any]:
        """Delete uploaded PDF and its data"""
        try:
            # Load processed PDFs
            with open(self.processed_pdfs_file, 'r') as f:
                processed_pdfs = json.load(f)
            
            # Find and remove the PDF
            pdf_to_remove = None
            updated_pdfs = []
            
            for pdf in processed_pdfs:
                if pdf.get("file_id") == file_id:
                    pdf_to_remove = pdf
                else:
                    updated_pdfs.append(pdf)
            
            if not pdf_to_remove:
                return {
                    "success": False,
                    "error": "PDF not found"
                }
            
            # Remove file from disk
            file_path = pdf_to_remove.get("file_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Update processed PDFs list
            with open(self.processed_pdfs_file, 'w') as f:
                json.dump(updated_pdfs, f, indent=2)
            
            # TODO: Remove from vector database (requires implementing delete by metadata)
            
            return {
                "success": True,
                "message": f"PDF {pdf_to_remove.get('filename')} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting PDF: {e}")
            return {
                "success": False,
                "error": f"Failed to delete PDF: {str(e)}"
            }