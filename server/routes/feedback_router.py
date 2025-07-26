from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

# Import services
from services.feedback_service import FeedbackService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
feedback_router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Initialize services
feedback_service = FeedbackService()

# Feedback request model
class FeedbackRequest(BaseModel):
    query_id: Optional[str] = Field(None, description="ID of the original query (auto-generated if not provided)")
    original_solution: str = Field(..., description="Original solution provided")
    feedback: str = Field(..., description="User feedback on the solution")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    corrections: Optional[str] = Field(None, description="User corrections or suggestions")

# Feedback response model
class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="Whether feedback was successfully processed")
    improved_solution: Optional[str] = Field(None, description="Improved solution based on feedback")
    message: str = Field(..., description="Response message")

@feedback_router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    feedback_data: FeedbackRequest = Body(...),
):
    """Submit feedback for a math solution to improve the system"""
    try:
        # Process the feedback
        result = await feedback_service.process_feedback(feedback_data)
        
        # Return response
        return FeedbackResponse(
            success=True,
            improved_solution=result.get("improved_solution"),
            message="Thank you for your feedback! We've used it to improve our system."
        )
    
    except Exception as e:
        logger.error(f"Error processing feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

@feedback_router.get("/stats")
async def get_feedback_stats():
    """Get statistics about feedback and system improvements"""
    try:
        stats = await feedback_service.get_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get feedback statistics: {str(e)}")