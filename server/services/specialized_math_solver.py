#!/usr/bin/env python3
"""
Improved Math Solver Service that provides proper step-by-step solutions
"""

import os
import re
import logging
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from services.caching_service import cached

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedMathSolver:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    def is_simple_arithmetic(self, query: str) -> bool:
        """Check if query is simple arithmetic that should get direct calculation"""
        query_lower = query.lower().strip()
        
        # Patterns for simple arithmetic
        simple_patterns = [
            r'what\s+is\s+\d+\s*²',  # "what is 4²"
            r'what\s+is\s+\d+\s*\^\s*\d+',  # "what is 4^2"
            r'what\s+is\s+\d+\s*[\+\-\*\/]\s*\d+',  # "what is 2+3"
            r'^\d+\s*[\+\-\*\/\^²³]\s*\d+$',  # "4²", "2+3", "5*6"
            r'what\s+is\s+\d+\s*(squared|cubed)',  # "what is 4 squared"
            r'calculate\s+\d+\s*[\+\-\*\/\^²³](\s*\d+)?',  # "calculate 4²"
            r'solve\s+\d+\s*[\+\-\*\/\^²³](\s*\d+)?',  # "solve 4²"
        ]
        
        for pattern in simple_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def is_basic_geometry(self, query: str) -> bool:
        """Check if query is basic geometry that should get direct formula application"""
        query_lower = query.lower().strip()
        
        basic_geometry_patterns = [
            r'area\s+of\s+(circle|square|rectangle|triangle)\s+with\s+(radius|side|length|width|height)\s+\d+',
            r'volume\s+of\s+(sphere|cube|cylinder)\s+with\s+(radius|side|height)\s+\d+',
            r'perimeter\s+of\s+(square|rectangle|triangle)\s+with',
            r'circumference\s+of\s+circle\s+with\s+radius\s+\d+',
        ]
        
        for pattern in basic_geometry_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def is_simple_derivative(self, query: str) -> bool:
        """Check if query is a simple derivative that should get direct calculation"""
        query_lower = query.lower().strip()
        
        derivative_patterns = [
            r'derivative\s+of\s+[x\d\+\-\*\/\^]+$',  # "derivative of x^2"
            r'find\s+derivative\s+of\s+[x\d\+\-\*\/\^]+$',  # "find derivative of x^3"
            r'd/dx\s+[x\d\+\-\*\/\^]+$',  # "d/dx x^2"
        ]
        
        for pattern in derivative_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    @cached(prefix="arithmetic_solve", ttl=7200)  # Cache for 2 hours
    async def solve_simple_arithmetic(self, query: str) -> Dict[str, Any]:
        """Solve simple arithmetic problems with step-by-step solutions using caching and streaming"""
        # Import performance monitor
        from .performance_monitor import PerformanceMonitor
        performance_monitor = PerformanceMonitor()
        request_id = f"arithmetic_{hash(query)}"
        performance_monitor.start_request(request_id, "arithmetic_solve", query)
        
        try:
            prompt = f"""
            Solve this simple arithmetic problem step by step:
            
            Question: {query}
            
            Please provide:
            1. A clear step-by-step solution
            2. The final answer
            3. Show all calculations
            
            Format your response as a complete mathematical solution.
            """
            
            # Get streaming service for token-by-token generation
            from .streaming_service import StreamingService
            streaming_service = StreamingService()
            
            # Configure LLM for streaming
            streaming_llm = streaming_service.configure_llm_for_streaming(self.llm)
            
            # Generate solution with streaming
            performance_monitor.log_stage(request_id, "llm_generation_start")
            solution = await streaming_service.stream_llm_response(prompt=prompt, llm=streaming_llm)
            performance_monitor.log_stage(request_id, "llm_generation_complete")
            
            performance_monitor.end_request(request_id)
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.95,
                "source": "direct_calculation",
                "references": ["🧮 Direct Mathematical Calculation"]
            }
            
        except Exception as e:
            logger.error(f"Error solving simple arithmetic: {e}")
            performance_monitor.end_request(request_id, error=str(e))
            return {"found": False, "error": str(e)}
    
    async def solve_basic_geometry(self, query: str) -> Dict[str, Any]:
        """Solve basic geometry problems with formulas and step-by-step solutions"""
        request_id = f"geometry_{hash(query)}"
        self.performance_monitor.start_request(request_id, "solve_basic_geometry", query)
        
        try:
            prompt = f"""
            Solve this geometry problem step by step using the appropriate formula:
            
            Question: {query}
            
            Please provide:
            1. The relevant formula
            2. Step-by-step substitution
            3. All calculations shown
            4. Final answer with units
            
            Format your response as a complete mathematical solution.
            """
            
            # Get streaming service for token-by-token generation
            from .streaming_service import StreamingService
            streaming_service = StreamingService()
            
            # Configure LLM for streaming
            self.performance_monitor.log_stage(request_id, "configure_llm")
            streaming_llm = streaming_service.configure_llm_for_streaming(self.llm)
            
            # Generate solution with streaming
            self.performance_monitor.log_stage(request_id, "llm_generation_start")
            solution = await streaming_service.stream_llm_response(prompt=prompt, llm=streaming_llm)
            self.performance_monitor.log_stage(request_id, "llm_generation_complete")
            
            self.performance_monitor.end_request(request_id)
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.95,
                "source": "geometry_formula",
                "references": ["📐 Geometry Formula Application"]
            }
            
        except Exception as e:
            logger.error(f"Error solving basic geometry: {e}")
            self.performance_monitor.end_request(request_id, error=str(e))
            return {"found": False}
    
    async def solve_simple_derivative(self, query: str) -> Dict[str, Any]:
        """Solve simple derivative problems with step-by-step solutions"""
        request_id = f"derivative_{hash(query)}"
        self.performance_monitor.start_request(request_id, "solve_simple_derivative", query)
        
        try:
            prompt = f"""
            Find the derivative step by step:
            
            Question: {query}
            
            Please provide:
            1. The function to differentiate
            2. The differentiation rules used (power rule, sum rule, etc.)
            3. Step-by-step application of the rules
            4. Final simplified answer
            
            Format your response as a complete calculus solution.
            """
            
            # Get streaming service for token-by-token generation
            from .streaming_service import StreamingService
            streaming_service = StreamingService()
            
            # Configure LLM for streaming
            self.performance_monitor.log_stage(request_id, "configure_llm")
            streaming_llm = streaming_service.configure_llm_for_streaming(self.llm)
            
            # Generate solution with streaming
            self.performance_monitor.log_stage(request_id, "llm_generation_start")
            solution = await streaming_service.stream_llm_response(prompt=prompt, llm=streaming_llm)
            self.performance_monitor.log_stage(request_id, "llm_generation_complete")
            
            self.performance_monitor.end_request(request_id)
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.95,
                "source": "calculus_rules",
                "references": ["📊 Calculus Differentiation Rules"]
            }
            
        except Exception as e:
            logger.error(f"Error solving simple derivative: {e}")
            self.performance_monitor.end_request(request_id, error=str(e))
            return {"found": False}
    
    def should_use_jee_bench(self, query: str) -> bool:
        """Determine if query should use JEE Bench dataset"""
        query_lower = query.lower().strip()
        
        # Don't use JEE Bench for simple queries
        if (self.is_simple_arithmetic(query) or 
            self.is_basic_geometry(query) or 
            self.is_simple_derivative(query)):
            return False
        
        # Use JEE Bench for complex physics/chemistry/advanced math
        jee_indicators = [
            'photoelectric', 'planck', 'quantum', 'electromagnetic',
            'thermodynamics', 'equilibrium', 'kinetics', 'organic',
            'complex analysis', 'differential equations', 'matrices',
            'probability distribution', 'statistics', 'hypothesis testing',
            'jee', 'entrance exam', 'competitive exam'
        ]
        
        return any(indicator in query_lower for indicator in jee_indicators)
    
    async def generate_comprehensive_solution(self, query: str) -> Dict[str, Any]:
        """Generate a comprehensive solution for complex problems"""
        request_id = f"comprehensive_{hash(query)}"
        self.performance_monitor.start_request(request_id, "generate_comprehensive_solution", query)
        
        try:
            prompt = f"""
            Provide a comprehensive step-by-step solution for this mathematical problem:
            
            Question: {query}
            
            Please provide:
            1. Problem analysis and approach
            2. Relevant formulas or concepts
            3. Detailed step-by-step solution
            4. Clear explanations for each step
            5. Final answer with proper units/format
            6. Any important notes or alternative methods
            
            Format your response as a complete educational solution that a student can follow and understand.
            """
            
            # Get streaming service for token-by-token generation
            from .streaming_service import StreamingService
            streaming_service = StreamingService()
            
            # Configure LLM for streaming
            self.performance_monitor.log_stage(request_id, "configure_llm")
            streaming_llm = streaming_service.configure_llm_for_streaming(self.llm)
            
            # Generate solution with streaming
            self.performance_monitor.log_stage(request_id, "llm_generation_start")
            solution = await streaming_service.stream_llm_response(prompt=prompt, llm=streaming_llm)
            self.performance_monitor.log_stage(request_id, "llm_generation_complete")
            
            self.performance_monitor.end_request(request_id)
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.85,
                "source": "ai_comprehensive",
                "references": ["🤖 AI Generated Comprehensive Solution"]
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive solution: {e}")
            self.performance_monitor.end_request(request_id, error=str(e))
            return {"found": False}

# Test the improved solver
async def test_improved_solver():
    """Test the improved math solver"""
    solver = ImprovedMathSolver()
    
    test_queries = [
        "what is 4²",
        "calculate 2 + 3 * 4",
        "area of circle with radius 7",
        "derivative of x^3 + 2x^2",
        "photoelectric effect problem",
        "solve quadratic equation x^2 - 5x + 6 = 0"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing: {query} ===")
        
        if solver.is_simple_arithmetic(query):
            print("→ Classified as: Simple Arithmetic")
            result = await solver.solve_simple_arithmetic(query)
        elif solver.is_basic_geometry(query):
            print("→ Classified as: Basic Geometry")
            result = await solver.solve_basic_geometry(query)
        elif solver.is_simple_derivative(query):
            print("→ Classified as: Simple Derivative")
            result = await solver.solve_simple_derivative(query)
        elif solver.should_use_jee_bench(query):
            print("→ Classified as: JEE Bench Candidate")
            result = {"found": False, "reason": "Would check JEE Bench"}
        else:
            print("→ Classified as: Comprehensive Solution")
            result = await solver.generate_comprehensive_solution(query)
        
        if result.get("found"):
            print(f"✅ Solution found (confidence: {result.get('confidence', 0):.2f})")
            print(f"Source: {result.get('source', 'unknown')}")
            print(f"Preview: {result.get('solution', '')[:100]}...")
        else:
            print(f"❌ No solution: {result.get('reason', 'Unknown')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_improved_solver())