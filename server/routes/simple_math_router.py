#!/usr/bin/env python3
"""
Simple Math Router - Bypasses LangChain conflicts
Ultra-fast math problem solving with MongoDB caching
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging
import time
from services.simple_math_solver import simple_math_solver
from services.mongodb_service import mongodb_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

class MathQuery(BaseModel):
    query: str = Field(..., description="Mathematical problem to solve")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class MathResponse(BaseModel):
    found: bool
    solution: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None
    response_time: Optional[float] = None
    error: Optional[str] = None
    suggestions: Optional[list] = None
    references: Optional[list] = None

@router.post("/solve", response_model=MathResponse)
async def solve_math_problem(request: MathQuery) -> MathResponse:
    """
    Solve mathematical problems with ultra-fast MongoDB caching
    
    **Performance Targets:**
    - 80% of queries: < 0.5 seconds (MongoDB cache hits)
    - 95% of queries: < 8 seconds (including AI generation)
    - Average response: 1-4 seconds
    """
    start_time = time.time()
    request_id = f"math_{hash(request.query)}"
    
    try:
        logger.info(f"🔍 Processing math query: {request.query[:50]}...")
        
        # Validate input
        if not request.query or len(request.query.strip()) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Query must be at least 2 characters long"
            )
        
        if len(request.query) > 1000:
            raise HTTPException(
                status_code=400, 
                detail="Query too long (max 1000 characters)"
            )
        
        # Solve the problem
        result = await simple_math_solver.solve(request.query.strip())
        
        # Calculate response time
        response_time = time.time() - start_time
        result["response_time"] = round(response_time, 3)
        
        # Log performance
        await mongodb_service.log_performance(
            request.query,
            response_time,
            result.get("source", "unknown"),
            result.get("found", False)
        )
        
        # Log result
        if result.get("found"):
            logger.info(f"✅ Solved in {response_time:.3f}s - Source: {result.get('source')}")
        else:
            logger.warning(f"❌ Not solved in {response_time:.3f}s")
        
        return MathResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        response_time = time.time() - start_time
        error_msg = f"Internal server error: {str(e)}"
        
        logger.error(f"❌ Error processing query: {error_msg}")
        
        # Log error performance
        await mongodb_service.log_performance(
            request.query,
            response_time,
            "error",
            False
        )
        
        return MathResponse(
            found=False,
            error=error_msg,
            response_time=round(response_time, 3)
        )

@router.get("/performance-stats")
async def get_performance_stats():
    """Get performance statistics from MongoDB"""
    try:
        stats = await mongodb_service.get_performance_stats()
        return {
            "status": "success",
            "mongodb_enabled": True,
            "performance_stats": stats.get("performance_stats", []),
            "message": "Ultra-fast responses enabled with MongoDB caching"
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return {
            "status": "error",
            "mongodb_enabled": False,
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongodb_connected = mongodb_service.db is not None
        
        # Test Gemini availability
        gemini_available = simple_math_solver.model is not None
        
        return {
            "status": "healthy",
            "mongodb_connected": mongodb_connected,
            "gemini_available": gemini_available,
            "services": {
                "simple_math_solver": "active",
                "mongodb_service": "active" if mongodb_connected else "inactive",
                "gemini_ai": "active" if gemini_available else "inactive"
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/test")
async def test_solver(request: MathQuery):
    """Test endpoint for debugging"""
    try:
        start_time = time.time()
        
        # Test basic functionality
        test_results = {
            "input_query": request.query,
            "mongodb_available": mongodb_service.db is not None,
            "gemini_available": simple_math_solver.model is not None,
        }
        
        # Try to solve
        result = await simple_math_solver.solve(request.query)
        test_results["solve_result"] = result
        test_results["response_time"] = round(time.time() - start_time, 3)
        
        return test_results
        
    except Exception as e:
        return {
            "error": str(e),
            "input_query": request.query
        }