"""Streaming Service - Handles streaming responses from LLMs"""

import os
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional, Callable
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenStreamingHandler(AsyncCallbackHandler):
    """Callback handler for streaming tokens from LLM"""
    
    def __init__(self):
        self.tokens = []
        self.token_queue = asyncio.Queue()
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Process new token from LLM"""
        self.tokens.append(token)
        await self.token_queue.put(token)
    
    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Signal end of LLM generation"""
        await self.token_queue.put(None)  # Signal end of stream
    
    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM errors"""
        logger.error(f"LLM error: {error}")
        await self.token_queue.put(f"\nError: {str(error)}")
        await self.token_queue.put(None)  # Signal end of stream
    
    def get_tokens(self) -> List[str]:
        """Get all tokens received so far"""
        return self.tokens
    
    async def get_token_stream(self) -> AsyncGenerator[str, None]:
        """Get tokens as an async generator"""
        while True:
            token = await self.token_queue.get()
            if token is None:  # End of stream
                break
            yield token

class StreamingService:
    """Service for streaming responses from LLMs"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
    
    def get_streaming_llm(self, streaming_handler: TokenStreamingHandler) -> ChatGoogleGenerativeAI:
        """Get LLM configured for streaming"""
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.google_api_key,
            streaming=True,
            callbacks=[streaming_handler]
        )
    
    def configure_llm_for_streaming(self, llm: ChatGoogleGenerativeAI) -> ChatGoogleGenerativeAI:
        """Configure an existing LLM for streaming"""
        streaming_handler = TokenStreamingHandler()
        
        # Create a new LLM instance with streaming enabled
        streaming_llm = ChatGoogleGenerativeAI(
            model=llm.model_name,
            google_api_key=self.google_api_key,
            streaming=True,
            callbacks=[streaming_handler]
        )
        
        return streaming_llm
    
    async def stream_llm_response(self, llm=None, prompt: str = None) -> AsyncGenerator[str, None]:
        """Stream response from LLM token by token"""
        streaming_handler = TokenStreamingHandler()
        
        # If no LLM is provided, create one
        if llm is None:
            llm = self.get_streaming_llm(streaming_handler)
        elif not hasattr(llm, 'callbacks') or not any(isinstance(cb, TokenStreamingHandler) for cb in llm.callbacks):
            # If LLM doesn't have a streaming handler, add one
            llm.callbacks = llm.callbacks + [streaming_handler] if hasattr(llm, 'callbacks') else [streaming_handler]
        
        # Start LLM generation in background task
        generation_task = asyncio.create_task(llm.ainvoke(prompt))
        
        # Stream tokens as they arrive
        async for token in streaming_handler.get_token_stream():
            yield token
        
        # Ensure generation task completes
        try:
            await generation_task
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            yield f"\nError: {str(e)}"
    
    async def stream_solution(self, query: str, solution_generator: Callable) -> AsyncGenerator[str, None]:
        """Stream solution generation with progress updates"""
        # Send initial progress updates
        yield "Initializing search...\n"
        await asyncio.sleep(0.1)
        yield "Searching knowledge base...\n"
        await asyncio.sleep(0.1)
        yield "Checking web sources...\n"
        await asyncio.sleep(0.1)
        yield "Generating solution...\n\n"
        
        # Start solution generation in background task
        try:
            # Check if solution_generator is already awaitable or needs to be called with query
            if asyncio.iscoroutine(solution_generator):
                solution_task = solution_generator
            else:
                solution_task = asyncio.create_task(solution_generator(query))
            
            # Wait for solution generation to complete
            solution = await solution_task
            
            # Stream the solution content
            if isinstance(solution, dict) and "solution" in solution:
                solution_text = solution["solution"]
                
                # Stream solution in chunks for smoother experience
                chunk_size = 20  # characters per chunk
                for i in range(0, len(solution_text), chunk_size):
                    yield solution_text[i:i+chunk_size]
                    await asyncio.sleep(0.01)  # Small delay between chunks
            else:
                yield str(solution)
                
        except Exception as e:
            logger.error(f"Error in solution generation: {e}")
            yield f"\nError generating solution: {str(e)}"
    
    async def stream_math_solution(self, query: str, math_solver) -> AsyncGenerator[str, None]:
        """Stream a math solution with step-by-step updates"""
        # Import performance monitor
        from .performance_monitor import PerformanceMonitor
        performance_monitor = PerformanceMonitor()
        request_id = f"stream_math_{hash(query)}"
        performance_monitor.start_request(request_id, "stream_math_solution", query)
        
        # Send initial progress updates
        yield "Processing your math problem...\n"
        await asyncio.sleep(0.1)
        
        try:
            # Determine problem type
            performance_monitor.log_stage(request_id, "problem_classification")
            if math_solver.is_simple_arithmetic(query):
                yield "Identified as arithmetic problem...\n"
                solution_generator = lambda q: math_solver.solve_simple_arithmetic(q)
            elif math_solver.is_basic_geometry(query):
                yield "Identified as geometry problem...\n"
                solution_generator = lambda q: math_solver.solve_basic_geometry(q)
            elif math_solver.is_simple_derivative(query):
                yield "Identified as calculus problem...\n"
                solution_generator = lambda q: math_solver.solve_simple_derivative(q)
            else:
                yield "Analyzing problem structure...\n"
                yield "Searching for similar problems...\n"
                solution_generator = lambda q: math_solver.generate_comprehensive_solution(q)
            
            await asyncio.sleep(0.1)
            yield "Generating step-by-step solution...\n\n"
            
            # Generate and stream the solution
            performance_monitor.log_stage(request_id, "solution_generation_start")
            solution_result = await solution_generator(query)
            performance_monitor.log_stage(request_id, "solution_generation_complete")
            
            if isinstance(solution_result, dict) and "solution" in solution_result:
                solution_text = solution_result["solution"]
                
                # Stream solution in chunks for smoother experience
                chunk_size = 20  # characters per chunk
                for i in range(0, len(solution_text), chunk_size):
                    yield solution_text[i:i+chunk_size]
                    await asyncio.sleep(0.01)  # Small delay between chunks
            else:
                yield str(solution_result)
                
            performance_monitor.end_request(request_id, True, solution_result.get("source", "unknown"), solution_result.get("confidence", 0.0))
            
        except Exception as e:
            logger.error(f"Error in math solution streaming: {e}")
            yield f"\nError generating solution: {str(e)}"
            performance_monitor.end_request(request_id, False, "error", 0.0)