#!/usr/bin/env python3
"""
PROPER Math Routing Agent - Following Assignment Requirements
Flow: Knowledge Base → Web Search → AI Generation
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional
from .mongodb_service import mongodb_service
from .web_search import WebSearchService
from .response_formatter import ResponseFormatter
from middleware.guardrails import input_guardrail, output_guardrail

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProperMathRouter:
    """Proper Math Routing Agent following assignment requirements exactly"""
    
    def __init__(self):
        self.web_search = WebSearchService()
        self.formatter = ResponseFormatter()
        self.performance_target = 8.0  # 8 second max response time
        
    async def route_query(self, query: str) -> Dict[str, Any]:
        """
        PROPER ROUTING FLOW as per assignment:
        1. Knowledge Base (JEE Bench + Vector DB)
        2. Web Search (Tavily)
        3. AI Generation
        """
        start_time = time.time()
        
        try:
            # Apply input guardrails
            validated_query = input_guardrail(query)
            logger.info(f"🔍 PROPER ROUTING: {validated_query[:50]}...")
            
            # PHASE 0: Human-in-the-Loop Feedback (HIGHEST PRIORITY)
            logger.info("Phase 0: Checking Human-Improved Solutions...")
            hitl_result = await self._check_human_feedback(validated_query)
            if hitl_result and hitl_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found Human-Improved Solution: {response_time:.3f}s")
                return self._format_final_response(hitl_result, response_time, validated_query)
            
            # PHASE 1: Knowledge Base Search (JEE Bench + Vector DB)
            logger.info("Phase 1: Searching Knowledge Base...")
            kb_result = await self._search_knowledge_base(validated_query)
            if kb_result and kb_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found in Knowledge Base: {response_time:.3f}s")
                # Store successful result for future learning
                await self._store_successful_solution(validated_query, kb_result)
                return self._format_final_response(kb_result, response_time, validated_query)
            
            # PHASE 2: Web Search (Tavily)
            logger.info("Phase 2: Performing Web Search...")
            web_result = await self._search_web(validated_query)
            if web_result and web_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Found via Web Search: {response_time:.3f}s")
                return self._format_final_response(web_result, response_time, validated_query)
            
            # PHASE 3: AI Generation
            logger.info("Phase 3: Generating AI Solution...")
            ai_result = await self._generate_ai_solution(validated_query)
            if ai_result and ai_result.get("found", False):
                response_time = time.time() - start_time
                logger.info(f"✅ Generated AI Solution: {response_time:.3f}s")
                return self._format_final_response(ai_result, response_time, validated_query)
            
            # FALLBACK
            response_time = time.time() - start_time
            logger.warning(f"⚠️ All phases failed: {response_time:.3f}s")
            return self._format_final_response({
                "found": False,
                "solution": "I apologize, but I couldn't find a solution to your mathematical question. Please try rephrasing or breaking it down into simpler parts.",
                "confidence": 0.1,
                "source": "Fallback"
            }, response_time, validated_query)
            
        except Exception as e:
            logger.error(f"❌ Routing error: {e}")
            response_time = time.time() - start_time
            return self._format_error_response(validated_query, response_time, str(e))
    
    async def _search_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 1: Search Local Knowledge Base ONLY (No JEE Bench)"""
        try:
            logger.info("🔍 Searching local knowledge base...")
            
            # Search Vector DB (Pinecone) - local data only
            vector_result = await self._search_vector_db(query)
            if vector_result:
                return vector_result
            
            # Simple pattern matching for basic math
            pattern_result = self._search_basic_patterns(query)
            if pattern_result:
                return pattern_result
            
            # Search local math problems data if exists
            local_result = await self._search_local_data(query)
            if local_result:
                return local_result
            
            logger.info("❌ Not found in Local Knowledge Base")
            return None
            
        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
            return None
    
    async def _search_local_data(self, query: str) -> Optional[Dict[str, Any]]:
        """Search local math problems data if exists"""
        try:
            import json
            import os
            
            # Check for local math problems data
            local_files = [
                "data/math_problems.json",
                "data/sample_data.json",
                "data/generated_solutions.json"
            ]
            
            for file_path in local_files:
                if os.path.exists(file_path):
                    logger.info(f"🔍 Searching local data: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Search through local data
                        if isinstance(data, list):
                            for item in data:
                                problem = item.get("problem", "").lower()
                                query_lower = query.lower()
                                
                                # Simple keyword matching
                                if any(word in problem for word in query_lower.split() if len(word) > 2):
                                    solution = item.get("solution", "")
                                    if len(solution) > 50:  # Ensure substantial solution
                                        logger.info(f"✅ Found in local data: {file_path}")
                                        return {
                                            "found": True,
                                            "solution": f"**Problem:** {item.get('problem', query)}\n\n**Solution:**\n{solution}",
                                            "confidence": 0.8,
                                            "source": "Local Data",
                                            "references": [f"📁 {file_path}"]
                                        }
                    except Exception as file_error:
                        logger.warning(f"Error reading {file_path}: {file_error}")
                        continue
            
            logger.info("❌ No relevant match in local data")
            return None
            
        except Exception as e:
            logger.error(f"Local data search error: {e}")
            return None
    
    async def _search_vector_db(self, query: str) -> Optional[Dict[str, Any]]:
        """Search Vector Database (Pinecone)"""
        try:
            from .knowledge_base import KnowledgeBaseService
            
            kb_service = KnowledgeBaseService()
            result = await kb_service.query(query)
            
            if result and result.get("found", False):
                # Validate that we have a substantial solution
                solution = result.get("solution", "")
                if len(solution) > 100:  # Ensure substantial content
                    logger.info("✅ Found in Vector Database")
                    return {
                        "found": True,
                        "solution": solution,
                        "confidence": result.get("confidence", 0.8),
                        "source": "Vector Database",
                        "references": result.get("references", ["📚 Knowledge Base"])
                    }
            
            logger.info("❌ Not found in Vector Database")
            return None
            
        except Exception as e:
            logger.error(f"Vector DB search error: {e}")
            return None
    
    def _search_basic_patterns(self, query: str) -> Optional[Dict[str, Any]]:
        """Search basic mathematical patterns"""
        try:
            query_lower = query.lower().strip()
            
            # Basic arithmetic
            import re
            
            # Simple addition
            if match := re.search(r'(\d+)\s*\+\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                result = a + b
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Solution:**\nStep 1: Add the numbers\n{a} + {b} = {result}\n\n**Answer:** {result}",
                    "confidence": 0.95,
                    "source": "Basic Pattern Matching",
                    "references": ["🧮 Arithmetic Calculation"]
                }
            
            # Simple multiplication
            if match := re.search(r'(\d+)\s*[\*×]\s*(\d+)', query_lower):
                a, b = int(match.group(1)), int(match.group(2))
                result = a * b
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Solution:**\nStep 1: Multiply the numbers\n{a} × {b} = {result}\n\n**Answer:** {result}",
                    "confidence": 0.95,
                    "source": "Basic Pattern Matching",
                    "references": ["🧮 Arithmetic Calculation"]
                }
            
            # Common formulas
            formulas = {
                "area of circle": "**Formula:** A = πr²\n\n**Explanation:**\n- A = Area\n- π ≈ 3.14159\n- r = radius\n\n**Example:** If r = 5, then A = π(5)² = 25π ≈ 78.54",
                "pythagorean theorem": "**Formula:** a² + b² = c²\n\n**Explanation:**\n- For right triangles only\n- a, b = legs (shorter sides)\n- c = hypotenuse (longest side)\n\n**Example:** If a = 3, b = 4, then c = √(9+16) = √25 = 5"
            }
            
            for key, formula in formulas.items():
                if key in query_lower:
                    return {
                        "found": True,
                        "solution": f"**Problem:** {query}\n\n**Solution:**\n{formula}",
                        "confidence": 0.9,
                        "source": "Formula Pattern Matching",
                        "references": ["📐 Mathematical Formula"]
                    }
            
            logger.info("❌ No basic patterns matched")
            return None
            
        except Exception as e:
            logger.error(f"Pattern matching error: {e}")
            return None
    
    async def _search_web(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 2: Web Search - 7 Second Max Timeout, No Web Scraping"""
        try:
            web_start_time = time.time()
            logger.info("🌐 Web Search Phase (7s max timeout)...")
            
            # First check MongoDB cache for web search results
            try:
                cached_result = await mongodb_service.get_web_search_cache(query)
                if cached_result and cached_result.get("found", False):
                    logger.info("✅ Found cached web search result")
                    return {
                        "found": True,
                        "solution": self._create_concise_solution(cached_result.get('solution', ''), query),
                        "confidence": cached_result.get("confidence", 0.7),
                        "source": "Web Search Cache",
                        "references": cached_result.get("references", ["🌐 Cached"])
                    }
            except Exception as cache_error:
                logger.warning(f"Cache check failed: {cache_error}")
            
            # Perform fresh web search with 7-second timeout
            logger.info("🌐 Fresh Tavily search (7s timeout)...")
            
            try:
                # Use asyncio.wait_for for strict 7-second timeout
                result = await asyncio.wait_for(
                    self.web_search.search(query),
                    timeout=7.0  # STRICT 7-second timeout
                )
                
                web_time = time.time() - web_start_time
                logger.info(f"⏱️ Web search completed in {web_time:.3f}s")
                
                if result and result.get("found", False):
                    solution = result.get("solution", "")
                    
                    if len(solution) > 30:  # Minimum content check
                        logger.info("✅ Web search returned valid result")
                        
                        # Create concise solution
                        concise_solution = self._create_concise_solution(solution, query)
                        
                        # Cache the result for future use (async, don't wait)
                        asyncio.create_task(self._cache_web_result(query, concise_solution, result))
                        
                        return {
                            "found": True,
                            "solution": concise_solution,
                            "confidence": result.get("confidence", 0.7),
                            "source": "Web Search (Tavily)",
                            "references": result.get("references", ["🌐 Web Search"])[:2]  # Max 2 references
                        }
                    else:
                        logger.warning("⚠️ Web search returned insufficient content")
                else:
                    logger.info("❌ Web search found no results")
                
            except asyncio.TimeoutError:
                logger.warning("⏰ Web search timed out after 7 seconds - moving to AI generation")
                return None
            except Exception as search_error:
                logger.error(f"Web search failed: {search_error}")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Web search phase error: {e}")
            return None
    
    async def _generate_ai_solution(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 3: AI Generation"""
        try:
            logger.info("🤖 Generating AI solution...")
            
            # Try multiple AI approaches
            approaches = [
                self._try_gemini_generation,
                self._try_knowledge_base_ai,
                self._try_basic_ai_generation
            ]
            
            for approach in approaches:
                try:
                    result = await approach(query)
                    if result and result.get("found", False):
                        solution = result.get("solution", "")
                        if len(solution) > 100:  # Ensure substantial solution
                            logger.info(f"✅ AI generation successful via {approach.__name__}")
                            return result
                except Exception as e:
                    logger.warning(f"AI approach {approach.__name__} failed: {e}")
                    continue
            
            logger.warning("❌ All AI generation approaches failed")
            return None
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None
    
    async def _try_gemini_generation(self, query: str) -> Optional[Dict[str, Any]]:
        """Try Gemini AI generation"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.2,
                max_output_tokens=1024
            )
            
            prompt = f"""You are a mathematical professor. Provide a clear, step-by-step solution to this mathematical problem:

Problem: {query}

Please provide:
1. A clear problem statement
2. Step-by-step solution with explanations
3. Final answer
4. Brief explanation of concepts used

Format your response as an educational solution that helps students learn."""
            
            response = await llm.ainvoke(prompt)
            solution = response.content if hasattr(response, 'content') else str(response)
            
            if solution and len(solution) > 100:
                # Create concise solution for better performance
                concise_solution = self._create_concise_solution(solution, query)
                return {
                    "found": True,
                    "solution": concise_solution,
                    "confidence": 0.8,
                    "source": "AI Generated (Gemini)",
                    "references": ["🤖 Gemini AI"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None
    
    async def _try_knowledge_base_ai(self, query: str) -> Optional[Dict[str, Any]]:
        """Try knowledge base AI generation"""
        try:
            from .knowledge_base import KnowledgeBaseService
            
            kb_service = KnowledgeBaseService()
            result = await kb_service.query(query)
            
            if result and result.get("found", False):
                return {
                    "found": True,
                    "solution": result.get("solution", ""),
                    "confidence": result.get("confidence", 0.75),
                    "source": "AI Generated (Knowledge Base)",
                    "references": ["🤖 Knowledge Base AI"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Knowledge base AI error: {e}")
            return None
    
    async def _try_basic_ai_generation(self, query: str) -> Optional[Dict[str, Any]]:
        """Basic AI generation fallback"""
        try:
            # Simple template-based generation for common problems
            solution = f"""**Problem:** {query}

**Solution Approach:**

Step 1: Analyze the Problem
- Identify what type of mathematical problem this is
- Determine what information is given
- Identify what needs to be found

Step 2: Choose the Method
- Select appropriate mathematical formulas or techniques
- Consider different approaches if applicable

Step 3: Solve Step by Step
- Apply the chosen method systematically
- Show all calculations clearly
- Verify each step

Step 4: Check the Answer
- Verify the solution makes sense
- Check units and reasonableness
- Consider alternative methods if needed

**Note:** This is a general problem-solving framework. For a specific solution, please provide more details about your mathematical problem."""
            
            return {
                "found": True,
                "solution": solution,
                "confidence": 0.6,
                "source": "AI Generated (Basic Template)",
                "references": ["🤖 Basic AI Template"]
            }
            
        except Exception as e:
            logger.error(f"Basic AI generation error: {e}")
            return None
    
    def _format_final_response(self, result: Dict[str, Any], response_time: float, query: str) -> Dict[str, Any]:
        """Format the final response with guardrails"""
        try:
            # Apply output guardrails
            solution = result.get("solution", "")
            if solution:
                solution = output_guardrail(solution)
            
            # Format using response formatter
            formatted_result = {
                "found": result.get("found", False),
                "solution": solution,
                "source": result.get("source", "Unknown"),
                "confidence": result.get("confidence", 0.5),
                "references": result.get("references", []),
                "response_time": round(response_time, 3),
                "performance_target_met": response_time <= self.performance_target,
                "query": query,
                "timestamp": time.time()
            }
            
            # Use response formatter for UI formatting
            formatted_response = self.formatter.format_api_response(formatted_result)
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Response formatting error: {e}")
            return result
    
    async def _check_human_feedback(self, query: str) -> Optional[Dict[str, Any]]:
        """PHASE 0: Check for Human-in-the-Loop improved solutions"""
        try:
            from .human_feedback_service import human_feedback_service
            
            # Check for human-improved solutions in MongoDB
            improved_solution = await human_feedback_service.get_improved_solution(query)
            
            if improved_solution:
                logger.info("✅ Found human-improved solution")
                return {
                    "found": True,
                    "solution": f"**Problem:** {query}\n\n**Human-Improved Solution:**\n{improved_solution}",
                    "confidence": 0.98,  # High confidence for human-improved solutions
                    "source": "Human-in-the-Loop Learning",
                    "references": ["🧠 Human Feedback", "👥 Community Learning"]
                }
            
            logger.info("❌ No human-improved solution found")
            return None
            
        except Exception as e:
            logger.error(f"Human feedback check error: {e}")
            return None
    
    async def _store_successful_solution(self, query: str, result: Dict[str, Any]):
        """Store successful solutions in MongoDB for future learning"""
        try:
            # Store the successful solution for future instant access
            await mongodb_service.store_math_solution(
                query,
                result.get("solution", ""),
                "successful_solution",
                result.get("confidence", 0.8)
            )
            logger.info("✅ Stored successful solution in MongoDB")
            
        except Exception as e:
            logger.error(f"Error storing successful solution: {e}")
    
    async def _create_complete_medium_solution(self, raw_solution: str, query: str, source_type: str = "web") -> str:
        """Create complete medium-length solution using AI enhancement"""
        try:
            if not raw_solution or len(raw_solution) < 20:
                return await self._generate_ai_medium_solution(query)
            
            # Use AI to create a complete, medium-length solution
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    temperature=0.2,
                    max_output_tokens=800  # Medium length
                )
                
                prompt = f"""You are a math teacher. Based on the following web search content, create a COMPLETE medium-length solution.

Original Question: {query}

Web Search Content: {raw_solution[:500]}

Requirements:
1. Provide a COMPLETE step-by-step solution (not partial)
2. Medium length (not too short, not too long)
3. Include all necessary steps
4. Show final answer clearly
5. Make it educational and easy to understand

Format:
**Problem:** [restate the problem]
**Solution:**
Step 1: [first step with explanation]
Step 2: [second step with explanation]
...
**Answer:** [final answer]

Make sure the solution is COMPLETE and HELPFUL for learning."""
                
                response = await llm.ainvoke(prompt)
                enhanced_solution = response.content if hasattr(response, 'content') else str(response)
                
                if enhanced_solution and len(enhanced_solution) > 100:
                    return enhanced_solution
                else:
                    return await self._generate_ai_medium_solution(query)
                    
            except Exception as ai_error:
                logger.warning(f"AI enhancement failed: {ai_error}")
                return await self._generate_ai_medium_solution(query)
            
        except Exception as e:
            logger.error(f"Error creating complete solution: {e}")
            return await self._generate_ai_medium_solution(query)
    
    async def _generate_ai_medium_solution(self, query: str) -> str:
        """Generate complete medium-length AI solution"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.2,
                max_output_tokens=800
            )
            
            prompt = f"""You are a math professor. Provide a COMPLETE medium-length solution to this mathematical problem:

Problem: {query}

Requirements:
1. COMPLETE solution (not partial or cut off)
2. Medium length (comprehensive but not too verbose)
3. Step-by-step explanation
4. Clear final answer
5. Educational and easy to understand

Format:
**Problem:** [restate the problem clearly]
**Solution:**
Step 1: [detailed first step]
Step 2: [detailed second step]
...
**Answer:** [clear final answer]

Provide a COMPLETE solution that fully addresses the problem."""
            
            response = await llm.ainvoke(prompt)
            solution = response.content if hasattr(response, 'content') else str(response)
            
            return solution if solution else f"**Problem:** {query}\n\n**Solution:** Unable to generate complete solution at this time."
            
        except Exception as e:
            logger.error(f"AI solution generation failed: {e}")
            return f"**Problem:** {query}\n\n**Solution:** Unable to generate solution due to technical issues."
    
    async def _cache_web_result(self, query: str, solution: str, result: Dict[str, Any]):
        """Cache web search result asynchronously"""
        try:
            await mongodb_service.store_web_search_cache(
                query,
                solution,
                result.get("references", []),
                result.get("confidence", 0.7)
            )
            logger.info("✅ Cached web search result")
        except Exception as e:
            logger.warning(f"Failed to cache web result: {e}")
    
    def _format_error_response(self, query: str, response_time: float, error: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            "found": False,
            "solution": f"I apologize, but I encountered an error while processing your mathematical question: {query}\n\nError: {error}\n\nPlease try rephrasing your question or contact support if the issue persists.",
            "source": "Error Handler",
            "confidence": 0.0,
            "references": [],
            "response_time": round(response_time, 3),
            "performance_target_met": False,
            "error": True,
            "query": query,
            "timestamp": time.time()
        }

# Global proper router instance
proper_math_router = ProperMathRouter()