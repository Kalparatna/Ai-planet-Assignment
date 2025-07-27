from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

# Import services
from services.pdf_processor import PDFProcessor
from middleware.guardrails import input_guardrail, output_guardrail

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/pdf", tags=["PDF Processing"])

# Service instance
pdf_processor = None

# Helper function to get PDF processor service
def get_pdf_processor():
    global pdf_processor
    if pdf_processor is None:
        pdf_processor = PDFProcessor()
    return pdf_processor

# Request models
class PDFQueryRequest(BaseModel):
    query: str = Field(..., description="Question to ask about the PDF content")
    file_id: Optional[str] = Field(None, description="Specific PDF file ID to query (optional)")

# Response models
class PDFUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message")
    file_id: Optional[str] = Field(None, description="Unique identifier for the uploaded PDF")
    filename: Optional[str] = Field(None, description="Original filename")
    pages: Optional[int] = Field(None, description="Number of pages in the PDF")
    chunks: Optional[int] = Field(None, description="Number of text chunks created")
    text_preview: Optional[str] = Field(None, description="Preview of extracted text")
    error: Optional[str] = Field(None, description="Error message if upload failed")

class PDFQueryResponse(BaseModel):
    found: bool = Field(..., description="Whether relevant content was found")
    answer: Optional[str] = Field(None, description="Answer based on PDF content")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source information")
    confidence: Optional[float] = Field(None, description="Confidence score")
    source_type: Optional[str] = Field(None, description="Type of source")
    error: Optional[str] = Field(None, description="Error message if query failed")

class PDFListResponse(BaseModel):
    pdfs: List[Dict[str, Any]] = Field(..., description="List of uploaded PDFs")

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(..., description="PDF file to upload"),
):
    """Upload and process a PDF file for mathematical content extraction"""
    try:
        # Get PDF processor service
        processor = get_pdf_processor()
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check file size (limit to 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
        
        # Reset file pointer
        await file.seek(0)
        
        # Process the PDF
        result = await processor.process_pdf_upload(file)
        
        return PDFUploadResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

@router.post("/query", response_model=PDFQueryResponse)
async def query_pdf_content(
    request: Request,
    query_request: PDFQueryRequest,
):
    """Query mathematical content from uploaded PDFs"""
    try:
        # Get PDF processor service
        processor = get_pdf_processor()
        
        # Apply input guardrails
        validated_query = input_guardrail(query_request.query)
        
        # Query PDF content
        result = await processor.query_pdf_content(
            query=validated_query,
            file_id=query_request.file_id
        )
        
        # Apply output guardrails if answer found
        if result.get("found") and result.get("answer"):
            result["answer"] = output_guardrail(result["answer"])
        
        return PDFQueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Error querying PDF content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to query PDF content: {str(e)}")

@router.get("/list", response_model=PDFListResponse)
async def list_uploaded_pdfs(request: Request):
    """Get list of all uploaded PDFs"""
    try:
        # Get PDF processor service
        processor = get_pdf_processor()
        
        # Get list of uploaded PDFs
        pdfs = processor.get_uploaded_pdfs()
        
        return PDFListResponse(pdfs=pdfs)
    
    except Exception as e:
        logger.error(f"Error listing PDFs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list PDFs: {str(e)}")

@router.delete("/{file_id}")
async def delete_pdf(
    request: Request,
    file_id: str,
):
    """Delete an uploaded PDF and its associated data"""
    try:
        # Get PDF processor service
        processor = get_pdf_processor()
        
        # Delete the PDF
        result = await processor.delete_pdf(file_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "PDF not found"))
        
        return {"message": result.get("message")}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")

@router.get("/health")
async def pdf_health_check():
    """Health check for PDF processing service"""
    try:
        processor = get_pdf_processor()
        
        status = {
            "service": "PDF Processor",
            "status": "healthy",
            "vector_store": "available" if processor.pdf_vector_store else "unavailable",
            "embeddings": "available" if processor.embeddings else "unavailable",
            "llm": "available" if processor.llm else "unavailable"
        }
        
        return status
    
    except Exception as e:
        logger.error(f"PDF health check failed: {e}")
        return {
            "service": "PDF Processor",
            "status": "unhealthy",
            "error": str(e)
        }