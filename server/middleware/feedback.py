from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Feedback request model
class FeedbackRequest(BaseModel):
    query_id: str = Field(..., description="ID of the original query")
    original_solution: str = Field(..., description="Original solution provided")
    feedback: str = Field(..., description="User feedback on the solution")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    corrections: Optional[str] = Field(None, description="User corrections or suggestions")

# Feedback response model
class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="Whether feedback was successfully processed")
    improved_solution: Optional[str] = Field(None, description="Improved solution based on feedback")
    message: str = Field(..., description="Response message")

# Service instance will be created when needed
feedback_service = None

# Helper function to get service
def get_feedback_service():
    global feedback_service
    
    if feedback_service is None:
        from services.feedback_service import FeedbackService
        feedback_service = FeedbackService()
        
    return feedback_service

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    feedback_data: FeedbackRequest = Body(...),
):
    """Submit feedback for a math solution to improve the system"""
    try:
        # Get service instance
        feedback_service = get_feedback_service()
        
        # Process the feedback
        result = await feedback_service.process_feedback(feedback_data)
        
        # Return response
        return FeedbackResponse(
            success=True,
            improved_solution=result.get("improved_solution"),
            message="Thank you for your feedback! We've used it to improve our system."
        )
    
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")