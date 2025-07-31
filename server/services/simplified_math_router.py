#!/usr/bin/env python3
"""
SIMPLIFIED Math Routing Agent - User Requirements
Flow: Sample Data (MongoDB) → Web Search (5s timeout) → AI Generation
NO JEE BENCH DATA - Only sample data, web search, and AI generation
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional
from .mongodb_service import mongodb_service
from .web_search import WebSearchService
from .response_formatter import ResponseFormatter
from .gemini_service import gemini_service
from middleware.guardrails import input_guardrail, output_guardrail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedMathRouter:
    """Simplified Math Routing Agent - User Requirements"""
    
    def __init__(self):
        self.web_search = WebSearchService()
        self.formatter = ResponseFormatter()
        self.web_search_timeout = 5.0  # 5 second timeout for web search
        
    async def solve_math_problem(self, query: str) -> Dict[str, Any]:
        """
        PROPER Math Routing Flow as per Assignment Requirements:
        1. PDF Documents (if uploaded)
        2. Knowledge Base (existing mathematical knowledge)
        3. Web Search (5 second timeout)
        4. AI Generation (Fallback)
        """
        start_time = time.time()
        
        try:
            # Apply input guardrails
            validated_query = input_guardrail(query)
            logger.info(f"🎯 MATH ROUTING: {validated_query[:50]}...")
            
            # PHASE 1: Check PDF Documents First
            logger.info("📄 PHASE 1: Checking PDF Documents...")
            pdf_result = await self._check_pdf_documents(validated_query)
            if pdf_result and pdf_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found in PDF Documents! Response time: {response_time:.3f}s")
                return self._format_response(pdf_result, response_time, validated_query)
            
            # PHASE 2: Check Knowledge Base
            logger.info("📚 PHASE 2: Checking Knowledge Base...")
            kb_result = await self._check_knowledge_base(validated_query)
            if kb_result and kb_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found in Knowledge Base! Response time: {response_time:.3f}s")
                return self._format_response(kb_result, response_time, validated_query)
            
            # PHASE 3: Web Search with 5 Second Timeout
            logger.info("🌐 PHASE 3: Performing Web Search (5s timeout)...")
            web_result = await self._search_web_with_timeout(validated_query)
            if web_result and web_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found via Web Search! Response time: {response_time:.2f}s")
                return self._format_response(web_result, response_time, validated_query)
            
            # PHASE 4: AI Generation (Fallback)
            logger.info("🤖 PHASE 4: Generating AI Solution (Fallback)...")
            ai_result = await self._generate_ai_solution(validated_query)
            if ai_result and ai_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ AI Generated Solution! Response time: {response_time:.2f}s")
                return self._format_response(ai_result, response_time, validated_query)
            
            # No solution found
            response_time = time.time() - start_time
            logger.warning(f"❌ No solution found after {response_time:.2f}s")
            return self._format_response({
                "found": False,
                "solution": "I couldn't find a solution to this problem. Please try rephrasing your question or provide more details.",
                "confidence": 0.0,
                "source": "No Solution Found"
            }, response_time, validated_query)
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Error in math routing: {e}")
            return self._format_response({
                "found": False,
                "solution": f"An error occurred while solving the problem: {str(e)}",
                "confidence": 0.0,
                "source": "Error"
            }, response_time, validated_query)
    
    async def _check_pdf_documents(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 1: Check PDF Documents - Look in uploaded PDFs first"""
        try:
            logger.info("📄 Checking uploaded PDF documents...")
            
            # Import PDF processor
            from .pdf_processor import PDFProcessor
            pdf_processor = PDFProcessor()
            
            # Query PDF content
            pdf_result = await pdf_processor.query_pdf_content(query)
            if pdf_result and pdf_result.get("found"):
                logger.info("📄 Found in uploaded PDF documents!")
                return {
                    "found": True,
                    "solution": pdf_result.get("answer", ""),
                    "confidence": pdf_result.get("confidence", 0.9),
                    "source": "PDF Document",
                    "references": [f"📄 {source.get('filename', 'PDF Document')}" for source in pdf_result.get("sources", [])][:3]
                }
            
            logger.info("❌ Not found in PDF documents")
            return None
            
        except Exception as e:
            logger.error(f"PDF document check error: {e}")
            return None
    
    async def _check_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 2: Check Knowledge Base - Following Assignment Requirements"""
        try:
            logger.info("📚 Checking mathematical knowledge base...")
            
            # Use proper knowledge base service
            from .proper_knowledge_base import proper_knowledge_base
            
            # Search knowledge base with strict matching (no random answers)
            kb_result = await proper_knowledge_base.search_knowledge_base(query)
            if kb_result and kb_result.get("found"):
                logger.info("📚 Found relevant match in knowledge base!")
                return kb_result
            
            logger.info("❌ No relevant match found in knowledge base")
            return None
            
        except Exception as e:
            logger.error(f"Knowledge base check error: {e}")
            return None


    
    def _check_basic_patterns(self, query: str) -> Optional[Dict[str, Any]]:
        """Check basic mathematical patterns for instant responses"""
        try:
            query_lower = query.lower().strip()
            
            # Basic arithmetic patterns
            import re
            
            # Simple addition (e.g., "2+2", "5 + 3")
            if match := re.search(r'(\d+)\s*\+\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                result = a + b
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Solution:**\n{a} + {b} = {result}\n\n**Answer:** {result}",
                    "confidence": 0.99,
                    "source": "Basic Pattern (Addition)",
                    "references": ["🧮 Instant Calculation"]
                }
            
            # Simple subtraction
            if match := re.search(r'(\d+)\s*-\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                result = a - b
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Solution:**\n{a} - {b} = {result}\n\n**Answer:** {result}",
                    "confidence": 0.99,
                    "source": "Basic Pattern (Subtraction)",
                    "references": ["🧮 Instant Calculation"]
                }
            
            # Simple multiplication
            if match := re.search(r'(\d+)\s*[\*×]\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                result = a * b
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Solution:**\n{a} × {b} = {result}\n\n**Answer:** {result}",
                    "confidence": 0.99,
                    "source": "Basic Pattern (Multiplication)",
                    "references": ["🧮 Instant Calculation"]
                }
            
            # Simple division
            if match := re.search(r'(\d+)\s*[/÷]\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                if b != 0:
                    result = a / b
                    return {
                        "found": True,
                        "solution": f"**Problem:** {query}\n\n**Solution:**\n{a} ÷ {b} = {result}\n\n**Answer:** {result}",
                        "confidence": 0.99,
                        "source": "Basic Pattern (Division)",
                        "references": ["🧮 Instant Calculation"]
                    }
            
            # Common formulas
            formula_patterns = {
                "area of circle": {
                    "solution": "**Formula:** A = πr²\n\n**Where:**\n- A = Area\n- π ≈ 3.14159\n- r = radius\n\n**Example:** If radius = 5, then A = π(5)² = 25π ≈ 78.54 square units",
                    "confidence": 0.95
                },
                "area of rectangle": {
                    "solution": "**Formula:** A = length × width\n\n**Where:**\n- A = Area\n- length = length of rectangle\n- width = width of rectangle\n\n**Example:** If length = 8 and width = 5, then A = 8 × 5 = 40 square units",
                    "confidence": 0.95
                },
                "pythagorean theorem": {
                    "solution": "**Formula:** a² + b² = c²\n\n**Where:**\n- a, b = legs (shorter sides of right triangle)\n- c = hypotenuse (longest side)\n\n**Example:** If a = 3 and b = 4, then c = √(9+16) = √25 = 5",
                    "confidence": 0.95
                }
            }
            
            for pattern, data in formula_patterns.items():
                if pattern in query_lower:
                    return {
                        "found": True,
                        "solution": f"**Problem:** {query}\n\n**Solution:**\n{data['solution']}",
                        "confidence": data["confidence"],
                        "source": "Basic Pattern (Formula)",
                        "references": ["📐 Mathematical Formula"]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Pattern matching error: {e}")
            return None
    
    async def _search_web_with_timeout(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 2: Web Search with 5 Second Timeout"""
        try:
            logger.info(f"🌐 Starting web search with {self.web_search_timeout}s timeout...")
            
            # Use asyncio.wait_for for strict timeout
            try:
                result = await asyncio.wait_for(
                    self.web_search.search(query),
                    timeout=self.web_search_timeout
                )
                
                if result and result.get("found", False):
                    solution = result.get("solution", "")
                    if len(solution) > 50:  # Ensure substantial content
                        logger.info("✅ Web search successful!")
                        
                        # Store in MongoDB for future ultra-fast access
                        await mongodb_service.store_web_search_cache(
                            query,
                            solution,
                            result.get("references", []),
                            result.get("confidence", 0.8)
                        )
                        
                        return {
                            "found": True,
                            "solution": solution,
                            "confidence": result.get("confidence", 0.8),
                            "source": "Web Search",  # Clean source name for UI
                            "references": result.get("references", ["🌐 Web Search"])[:3]
                        }
                    else:
                        logger.warning("⚠️ Web search returned insufficient content")
                else:
                    logger.info("❌ Web search found no results")
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Web search timed out after {self.web_search_timeout}s - proceeding to AI generation")
                return None
            except Exception as search_error:
                logger.error(f"Web search failed: {search_error}")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Web search with timeout error: {e}")
            return None
    
    async def _generate_ai_solution(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 3: AI Generation using Google Gemini"""
        try:
            logger.info("🤖 Generating AI solution using Google Gemini...")
            
            # Check if Gemini service is available
            if not gemini_service.is_available():
                logger.warning("⚠️ Gemini service not available")
                return self._generate_fallback_solution(query)
            
            # Generate solution using Gemini
            result = await gemini_service.solve_math_problem(query)
            
            if result and result.get("found", False):
                solution = result.get("solution", "")
                if len(solution) > 100:  # Ensure substantial solution
                    logger.info("✅ Gemini AI generation successful")
                    
                    # Store successful solution in MongoDB for future ultra-fast access
                    await mongodb_service.store_math_solution(
                        query,
                        solution,
                        "ai_generated",
                        result.get("confidence", 0.8)
                    )
                    
                    return {
                        "found": True,
                        "solution": solution,
                        "confidence": result.get("confidence", 0.8),
                        "source": "AI Generated (Google Gemini)",
                        "references": ["🤖 Google Gemini AI"]
                    }
            
            logger.warning("❌ Gemini AI generation failed - using fallback")
            return self._generate_fallback_solution(query)
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self._generate_fallback_solution(query)
    
    def _generate_fallback_solution(self, query: str) -> Dict[str, Any]:
        """Generate a fallback solution when AI is not available"""
        try:
            solution = f"""**Problem:** {query}

**Solution Approach:**

I apologize, but I'm currently unable to provide a specific solution to this mathematical problem due to technical limitations.

**General Problem-Solving Steps:**

1. **Identify the Problem Type**
   - What kind of mathematical problem is this?
   - What information is given?
   - What needs to be found?

2. **Choose the Right Method**
   - Select appropriate formulas or techniques
   - Consider different approaches

3. **Solve Step by Step**
   - Apply the chosen method systematically
   - Show all calculations clearly
   - Verify each step

4. **Check Your Answer**
   - Does the solution make sense?
   - Are the units correct?
   - Try alternative methods if possible

**Suggestion:** Please try rephrasing your question or breaking it down into smaller parts for better assistance."""
            
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.5,
                "source": "Fallback Solution",
                "references": ["🔧 System Fallback"]
            }
            
        except Exception as e:
            logger.error(f"Fallback solution error: {e}")
            return {
                "found": False,
                "solution": "Unable to generate solution due to technical issues.",
                "confidence": 0.0,
                "source": "Error",
                "references": []
            }
    
    def _format_response(self, result: Dict[str, Any], response_time: float, query: str) -> Dict[str, Any]:
        """Format the final response"""
        try:
            # Apply output guardrails
            solution = result.get("solution", "")
            if solution:
                solution = output_guardrail(solution)
            
            formatted_result = {
                "found": result.get("found", False),
                "solution": solution,
                "source": result.get("source", "Unknown"),
                "confidence": result.get("confidence", 0.5),
                "references": result.get("references", []),
                "response_time": round(response_time, 3),
                "query": query,
                "timestamp": time.time(),
                "flow": "Simplified: Sample Data → Web Search (5s) → AI Generation"
            }
            
            # Use response formatter
            try:
                formatted_response = self.formatter.format_api_response(formatted_result)
                return formatted_response
            except Exception as format_error:
                logger.warning(f"Response formatting failed: {format_error}")
                return formatted_result
            
        except Exception as e:
            logger.error(f"Response formatting error: {e}")
            return result

# Global instance
simplified_math_router = SimplifiedMathRouter()