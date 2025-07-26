from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

# Import services
from services.knowledge_base import KnowledgeBaseService
from services.web_search import WebSearchService
from services.math_solver import MathSolverService
from services.response_formatter import ResponseFormatter
from middleware.guardrails import input_guardrail, output_guardrail

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/math", tags=["Math Queries"])

# Service instances will be created when needed
knowledge_base_service = None
web_search_service = None
math_solver_service = None
response_formatter = None

# Helper function to get services
def get_services():
    global knowledge_base_service, web_search_service, math_solver_service, response_formatter
    
    if knowledge_base_service is None:
        knowledge_base_service = KnowledgeBaseService()
    if web_search_service is None:
        web_search_service = WebSearchService()
    if math_solver_service is None:
        math_solver_service = MathSolverService()
    if response_formatter is None:
        response_formatter = ResponseFormatter()
        
    return knowledge_base_service, web_search_service, math_solver_service, response_formatter

# Request model
class MathQuery(BaseModel):
    query: str = Field(..., description="The mathematical question to solve")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the question")

# Response model
class MathResponse(BaseModel):
    solution: str = Field(..., description="Step-by-step solution to the mathematical problem")
    source: str = Field(..., description="Source of the solution (knowledge_base, web_search, or generated)")
    confidence: float = Field(..., description="Confidence score of the solution")
    references: Optional[List[str]] = Field(default=None, description="References used for the solution")

@router.post("/solve", response_model=MathResponse)
async def solve_math_problem(
    request: Request,
    math_query: MathQuery = Body(...),
):
    """Solve a mathematical problem with step-by-step solution"""
    try:
        # Get service instances
        knowledge_base_service, web_search_service, math_solver_service, response_formatter = get_services()
        
        # Apply input guardrails
        validated_query = input_guardrail(math_query.query)
        
        # Step 1: Check knowledge base first
        kb_result = await knowledge_base_service.query(validated_query)
        
        if kb_result and kb_result.get("found", False):
            # Found in knowledge base
            solution = math_solver_service.format_solution(kb_result["solution"], validated_query)
            response = MathResponse(
                solution=solution,
                source="knowledge_base",
                confidence=kb_result.get("confidence", 0.9),
                references=kb_result.get("references")
            )
        else:
            # Not found in knowledge base, try web search
            web_result = await web_search_service.search(validated_query)
            
            if web_result and web_result.get("found", False):
                # Found via web search
                solution = math_solver_service.format_solution(web_result["solution"], validated_query)
                response = MathResponse(
                    solution=solution,
                    source="web_search",
                    confidence=web_result.get("confidence", 0.8),
                    references=web_result.get("references")
                )
            else:
                # Generate solution using LLM
                generated_solution = await math_solver_service.generate_solution(validated_query)
                response = MathResponse(
                    solution=generated_solution["solution"],
                    source="generated",
                    confidence=generated_solution.get("confidence", 0.7),
                    references=None
                )
        
        # Apply output guardrails
        response.solution = output_guardrail(response.solution)
        
        # Format the response for UI display
        response_dict = response.dict()
        formatted_response = response_formatter.format_api_response(response_dict)
        
        # Create new response with formatted data
        formatted_math_response = MathResponse(
            solution=formatted_response["solution"],
            source=formatted_response["source"],
            confidence=formatted_response["confidence"],
            references=formatted_response.get("references")
        )
        
        return formatted_math_response
    
    except Exception as e:
        logger.error(f"Error solving math problem: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to solve math problem: {str(e)}")