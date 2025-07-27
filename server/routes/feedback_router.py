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

@feedback_router.get("/learning-insights")
async def get_learning_insights():
    """Get insights from Human-in-the-Loop learning patterns"""
    try:
        insights = await feedback_service.get_learning_insights()
        return insights
    
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get learning insights: {str(e)}")

@feedback_router.get("/quality-control")
async def get_quality_control_issues():
    """Get pending quality control issues for human review"""
    try:
        issues = await feedback_service.get_quality_control_issues()
        return issues
    
    except Exception as e:
        logger.error(f"Error getting quality control issues: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get quality control issues: {str(e)}")

@feedback_router.post("/quality-control/{issue_id}/resolve")
async def resolve_quality_issue(
    issue_id: int,
    resolution_data: Dict[str, str] = Body(...)
):
    """Resolve a quality control issue"""
    try:
        resolution = resolution_data.get("resolution", "")
        reviewer = resolution_data.get("reviewer", "anonymous")
        
        result = await feedback_service.resolve_quality_issue(issue_id, resolution, reviewer)
        return result
    
    except Exception as e:
        logger.error(f"Error resolving quality issue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to resolve quality issue: {str(e)}")

@feedback_router.get("/improved-solution")
async def get_improved_solution(query: str):
    """Get improved solution for a query if available from HITL learning"""
    try:
        improved_solution = await feedback_service.get_improved_solution_for_query(query)
        
        if improved_solution:
            return {
                "found": True,
                "improved_solution": improved_solution,
                "source": "human_feedback_learning"
            }
        else:
            return {
                "found": False,
                "message": "No improved solution available for this query"
            }
    
    except Exception as e:
        logger.error(f"Error getting improved solution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get improved solution: {str(e)}")