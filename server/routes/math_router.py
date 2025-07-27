from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

# Import services
from services.knowledge_base import KnowledgeBaseService
from services.web_search import WebSearchService
from services.math_solution_formatter import MathSolverService
from services.response_formatter import ResponseFormatter
from services.pdf_processor import PDFProcessor
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
pdf_processor = None

# Helper function to get services
def get_services():
    global knowledge_base_service, web_search_service, math_solver_service, response_formatter, pdf_processor
    
    if knowledge_base_service is None:
        knowledge_base_service = KnowledgeBaseService()
    if web_search_service is None:
        web_search_service = WebSearchService()
    if math_solver_service is None:
        math_solver_service = MathSolverService()
    if response_formatter is None:
        response_formatter = ResponseFormatter()
    if pdf_processor is None:
        pdf_processor = PDFProcessor()
        
    return knowledge_base_service, web_search_service, math_solver_service, response_formatter, pdf_processor

# Full search flow function
async def _full_search_flow(knowledge_base_service, web_search_service, math_solver_service, improved_solver, validated_query):
    """Execute the full search flow: Knowledge Base → JEE Bench → Web Search → AI Generated"""
    
    # Step 1: Check local knowledge base
    logger.info("Step 1: Searching in local knowledge base...")
    kb_result = await knowledge_base_service.query(validated_query)
    
    if kb_result and kb_result.get("found", False):
        logger.info("✅ Found in knowledge base")
        solution = math_solver_service.format_solution(kb_result["solution"], validated_query)
        return MathResponse(
            solution=f"**Source: Knowledge Base**\n\n{solution}",
            source="knowledge_base",
            confidence=kb_result.get("confidence", 0.85),
            references=[f"📚 {ref}" for ref in kb_result.get("references", [])]
        )
    
    # Step 2: Check JEE Bench dataset
    logger.info("Step 2: Searching in JEE Bench dataset...")
    jee_result = await knowledge_base_service.query_jee_bench(validated_query)
    
    if jee_result and jee_result.get("found", False):
        logger.info("✅ Found in JEE Bench dataset")
        solution = math_solver_service.format_solution(jee_result["solution"], validated_query)
        return MathResponse(
            solution=f"**Source: JEE Bench Dataset**\n\n{solution}",
            source="jee_bench",
            confidence=jee_result.get("confidence", 0.9),
            references=[f"🎯 JEE Bench - {jee_result.get('category', 'Mathematics')}"]
        )
    
    # Step 3: Try web search
    logger.info("Step 3: Searching on the web...")
    web_result = await web_search_service.search(validated_query)
    
    if web_result and web_result.get("found", False):
        logger.info("✅ Found via web search")
        solution = math_solver_service.format_solution(web_result["solution"], validated_query)
        
        # Create detailed source attribution for web search
        web_sources = []
        for ref in web_result.get("references", []):
            web_sources.append(f"🌐 {ref}")
        
        return MathResponse(
            solution=f"**Source: Web Search**\n\n{solution}",
            source="web_search",
            confidence=web_result.get("confidence", 0.8),
            references=web_sources
        )
    
    # Step 4: Generate comprehensive solution using AI
    logger.info("Step 4: Generating AI solution...")
    generated_solution = await improved_solver.generate_comprehensive_solution(validated_query)
    
    return MathResponse(
        solution=f"**Source: AI Generated Solution**\n\n{generated_solution['solution']}",
        source="generated",
        confidence=generated_solution.get("confidence", 0.85),
        references=generated_solution.get("references", ["🤖 AI Generated"])
    )

# Request models
class MathQuery(BaseModel):
    query: str = Field(..., description="The mathematical question to solve")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the question")

class AssignmentRequest(BaseModel):
    topic: str = Field(..., description="The mathematical topic for the assignment")
    difficulty: str = Field(default="Medium", description="Difficulty level (Easy, Medium, Hard)")
    num_problems: int = Field(default=5, description="Number of problems to include")

class RequirementsRequest(BaseModel):
    project_type: str = Field(..., description="Type of project (e.g., 'calculator app', 'data analysis tool')")
    subject: str = Field(..., description="Mathematical subject area")
    complexity: str = Field(default="Medium", description="Project complexity level")

# Response models
class MathResponse(BaseModel):
    solution: str = Field(..., description="Step-by-step solution to the mathematical problem")
    source: str = Field(..., description="Source of the solution (pdf_upload, jee_bench, knowledge_base, web_search, or generated)")
    confidence: float = Field(..., description="Confidence score of the solution")
    references: Optional[List[str]] = Field(default=None, description="References used for the solution")

class AssignmentResponse(BaseModel):
    success: bool = Field(..., description="Whether assignment generation was successful")
    assignment: Optional[str] = Field(default=None, description="Generated assignment content")
    topic: Optional[str] = Field(default=None, description="Assignment topic")
    difficulty: Optional[str] = Field(default=None, description="Assignment difficulty")
    sources_used: Optional[List[str]] = Field(default=None, description="Sources used for generation")
    error: Optional[str] = Field(default=None, description="Error message if generation failed")

class RequirementsResponse(BaseModel):
    success: bool = Field(..., description="Whether requirements generation was successful")
    requirements_document: Optional[str] = Field(default=None, description="Generated requirements document")
    project_type: Optional[str] = Field(default=None, description="Project type")
    subject: Optional[str] = Field(default=None, description="Subject area")
    sources_used: Optional[List[str]] = Field(default=None, description="Sources used for generation")
    error: Optional[str] = Field(default=None, description="Error message if generation failed")

@router.post("/solve", response_model=MathResponse)
async def solve_math_problem(
    request: Request,
    math_query: MathQuery = Body(...),
):
    """Solve a mathematical problem with step-by-step solution - PDF first, then web search"""
    try:
        # Get service instances
        knowledge_base_service, web_search_service, math_solver_service, response_formatter, pdf_processor = get_services()
        
        # Apply input guardrails
        validated_query = input_guardrail(math_query.query)
        
        # Import improved solver and feedback service
        from services.specialized_math_solver import ImprovedMathSolver
        from services.feedback_service import FeedbackService
        improved_solver = ImprovedMathSolver()
        feedback_service = FeedbackService()
        
        # Step 0: Check for improved solutions from HITL feedback (HIGHEST priority)
        logger.info("Step 0: Checking for HITL improved solutions...")
        improved_solution = await feedback_service.get_improved_solution_for_query(validated_query)
        
        if improved_solution:
            logger.info("✅ Found improved solution from Human-in-the-Loop feedback")
            return MathResponse(
                solution=f"**Source: Human-in-the-Loop Improved Solution**\n\n{improved_solution}",
                source="hitl_improved",
                confidence=0.98,  # High confidence for human-improved solutions
                references=["🧠 Human-in-the-Loop Learning", "👥 Community Feedback"]
            )
        
        # Step 1: Check uploaded PDF content FIRST (highest priority)
        pdf_result = await pdf_processor.query_pdf_content(validated_query)
        
        if pdf_result and pdf_result.get("found", False):
            # Found in uploaded PDFs
            solution = math_solver_service.format_solution(pdf_result["answer"], validated_query)
            
            # Create detailed source attribution for PDFs
            pdf_sources = []
            for source in pdf_result.get("sources", []):
                pdf_sources.append(f"📄 {source.get('filename', 'Unknown PDF')} (Chunk {source.get('chunk_index', 0) + 1})")
            
            response = MathResponse(
                solution=f"**Source: Uploaded PDF Document**\n\n{solution}",
                source="pdf_upload",
                confidence=pdf_result.get("confidence", 0.95),
                references=pdf_sources
            )
        else:
            # Step 2: Check if this is a simple problem that needs direct solution
            if improved_solver.is_simple_arithmetic(validated_query):
                logger.info("Solving as simple arithmetic")
                direct_result = await improved_solver.solve_simple_arithmetic(validated_query)
                if direct_result.get("found", False):
                    response = MathResponse(
                        solution=f"**Source: Direct Mathematical Calculation**\n\n{direct_result['solution']}",
                        source="direct_calculation",
                        confidence=direct_result.get("confidence", 0.95),
                        references=direct_result.get("references", ["🧮 Direct Calculation"])
                    )
                else:
                    # Fallback to full search flow
                    response = await _full_search_flow(knowledge_base_service, web_search_service, math_solver_service, improved_solver, validated_query)
            
            elif improved_solver.is_basic_geometry(validated_query):
                logger.info("Solving as basic geometry")
                direct_result = await improved_solver.solve_basic_geometry(validated_query)
                if direct_result.get("found", False):
                    response = MathResponse(
                        solution=f"**Source: Geometry Formula Application**\n\n{direct_result['solution']}",
                        source="geometry_formula",
                        confidence=direct_result.get("confidence", 0.95),
                        references=direct_result.get("references", ["📐 Geometry Formula"])
                    )
                else:
                    # Fallback to full search flow
                    response = await _full_search_flow(knowledge_base_service, web_search_service, math_solver_service, improved_solver, validated_query)
            
            elif improved_solver.is_simple_derivative(validated_query):
                logger.info("Solving as simple derivative")
                direct_result = await improved_solver.solve_simple_derivative(validated_query)
                if direct_result.get("found", False):
                    response = MathResponse(
                        solution=f"**Source: Calculus Rules Application**\n\n{direct_result['solution']}",
                        source="calculus_rules",
                        confidence=direct_result.get("confidence", 0.95),
                        references=direct_result.get("references", ["📊 Calculus Rules"])
                    )
                else:
                    # Fallback to full search flow
                    response = await _full_search_flow(knowledge_base_service, web_search_service, math_solver_service, improved_solver, validated_query)
            
            else:
                logger.info("Using full search flow")
                # For all other queries, use the complete search flow
                response = await _full_search_flow(knowledge_base_service, web_search_service, math_solver_service, improved_solver, validated_query)
        
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

@router.post("/generate-assignment", response_model=AssignmentResponse)
async def generate_assignment(
    request: Request,
    assignment_request: AssignmentRequest = Body(...),
):
    """Generate a mathematical assignment with problems and requirements"""
    try:
        # Get service instances
        knowledge_base_service, _, _, _, _ = get_services()
        
        # Apply input guardrails
        validated_topic = input_guardrail(assignment_request.topic)
        
        # Generate assignment using knowledge base service
        result = await knowledge_base_service.generate_assignment(
            topic=validated_topic,
            difficulty=assignment_request.difficulty,
            num_problems=assignment_request.num_problems
        )
        
        if result.get("success", False):
            # Apply output guardrails
            assignment_content = output_guardrail(result["assignment"])
            
            return AssignmentResponse(
                success=True,
                assignment=assignment_content,
                topic=result["topic"],
                difficulty=result["difficulty"],
                sources_used=result.get("sources_used", [])
            )
        else:
            return AssignmentResponse(
                success=False,
                error=result.get("error", "Failed to generate assignment")
            )
    
    except Exception as e:
        logger.error(f"Error generating assignment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate assignment: {str(e)}")

@router.post("/generate-requirements", response_model=RequirementsResponse)
async def generate_requirements(
    request: Request,
    requirements_request: RequirementsRequest = Body(...),
):
    """Generate a requirements document for mathematical projects"""
    try:
        # Get service instances
        knowledge_base_service, _, _, _, _ = get_services()
        
        # Apply input guardrails
        validated_project_type = input_guardrail(requirements_request.project_type)
        validated_subject = input_guardrail(requirements_request.subject)
        
        # Generate requirements document using knowledge base service
        result = await knowledge_base_service.generate_requirements_document(
            project_type=validated_project_type,
            subject=validated_subject,
            complexity=requirements_request.complexity
        )
        
        if result.get("success", False):
            # Apply output guardrails
            requirements_content = output_guardrail(result["requirements_document"])
            
            return RequirementsResponse(
                success=True,
                requirements_document=requirements_content,
                project_type=result["project_type"],
                subject=result["subject"],
                sources_used=result.get("sources_used", [])
            )
        else:
            return RequirementsResponse(
                success=False,
                error=result.get("error", "Failed to generate requirements document")
            )
    
    except Exception as e:
        logger.error(f"Error generating requirements: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate requirements: {str(e)}")

@router.get("/jee-bench-status")
async def get_jee_bench_status():
    """Get status of JEE Bench dataset loading"""
    try:
        knowledge_base_service, _, _, _, _ = get_services()
        
        # Check if JEE Bench vector store is available
        if hasattr(knowledge_base_service, 'jee_vector_store') and knowledge_base_service.jee_vector_store:
            # Get index stats if possible
            try:
                if hasattr(knowledge_base_service, 'pc') and knowledge_base_service.pc:
                    index = knowledge_base_service.pc.Index(knowledge_base_service.jee_index_name)
                    stats = index.describe_index_stats()
                    return {
                        "status": "loaded",
                        "vector_count": stats.get('total_vector_count', 0),
                        "message": "JEE Bench dataset is loaded and ready"
                    }
            except Exception as e:
                logger.warning(f"Could not get index stats: {e}")
            
            return {
                "status": "loaded",
                "message": "JEE Bench dataset is loaded and ready"
            }
        else:
            return {
                "status": "not_loaded",
                "message": "JEE Bench dataset is not loaded or unavailable"
            }
    
    except Exception as e:
        logger.error(f"Error checking JEE Bench status: {e}")
        return {
            "status": "error",
            "message": f"Error checking JEE Bench status: {str(e)}"
        }