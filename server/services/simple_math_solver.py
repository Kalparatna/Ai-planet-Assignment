#!/usr/bin/env python3
"""
Simple Math Solver - Bypasses LangChain version conflicts
Uses direct Google Gemini API and MongoDB for ultra-fast responses
"""

import os
import re
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from .mongodb_service import mongodb_service
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMathSolver:
    """Simple math solver that bypasses LangChain conflicts"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        
        if self.google_api_key:
            try:
                genai.configure(api_key=self.google_api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Simple Math Solver initialized with Google Gemini")
            except Exception as e:
                logger.error(f"❌ Error initializing Gemini: {e}")
                self.model = None
        else:
            logger.warning("⚠️ GOOGLE_API_KEY not found - using basic patterns only")
    
    async def solve(self, query: str) -> Dict[str, Any]:
        """Main solve method - checks MongoDB first, then patterns, then AI"""
        try:
            logger.info(f"🔍 Solving: {query}")
            
            # 🚀 STEP 1: Check MongoDB for ultra-fast cached responses (0.01-0.1s)
            mongodb_result = await self._check_mongodb_cache(query)
            if mongodb_result:
                logger.info("⚡ Found in MongoDB cache - ULTRA FAST!")
                return mongodb_result
            
            # 🧮 STEP 2: Try basic pattern matching (0.1-0.5s)
            pattern_result = self._try_basic_patterns(query)
            if pattern_result:
                logger.info("⚡ Solved with basic patterns - FAST!")
                # Store in MongoDB for future ultra-fast access
                await mongodb_service.store_math_solution(
                    query, 
                    pattern_result["solution"], 
                    "pattern_matching", 
                    pattern_result["confidence"]
                )
                return pattern_result
            
            # 🤖 STEP 3: Use Google Gemini AI (2-8s)
            if self.model:
                ai_result = await self._try_gemini_ai(query)
                if ai_result:
                    logger.info("✅ Solved with Google Gemini AI")
                    # Store in MongoDB for future ultra-fast access
                    await mongodb_service.store_math_solution(
                        query, 
                        ai_result["solution"], 
                        "ai_generated", 
                        ai_result["confidence"]
                    )
                    return ai_result
            
            # ❌ STEP 4: No solution found
            logger.warning("❌ No solution found")
            return {
                "found": False,
                "error": "Unable to solve this problem",
                "suggestions": [
                    "Try rephrasing the question",
                    "Check if all necessary information is provided",
                    "Ensure the problem is mathematical in nature"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in solve method: {e}")
            return {
                "found": False,
                "error": f"Solver error: {str(e)}"
            }
    
    async def _check_mongodb_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Check MongoDB for cached solutions"""
        try:
            # Check math solutions cache
            result = await mongodb_service.get_math_solution(query)
            if result and result.get("found"):
                return {
                    "found": True,
                    "solution": result["solution"],
                    "confidence": result.get("confidence", 0.9),
                    "source": "MongoDB Cache",
                    "response_time": 0.01
                }
            
            # Check web search cache
            web_result = await mongodb_service.get_web_search_cache(query)
            if web_result and web_result.get("found"):
                return {
                    "found": True,
                    "solution": web_result["solution"],
                    "confidence": web_result.get("confidence", 0.8),
                    "source": "Web Search Cache",
                    "references": web_result.get("references", []),
                    "response_time": 0.05
                }
            
            # Check JEE bench data
            jee_result = await mongodb_service.get_jee_solution(query)
            if jee_result and jee_result.get("found"):
                return {
                    "found": True,
                    "solution": jee_result["solution"],
                    "confidence": jee_result.get("confidence", 0.9),
                    "source": "JEE Bench Data",
                    "response_time": 0.02
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking MongoDB cache: {e}")
            return None
    
    def _try_basic_patterns(self, query: str) -> Optional[Dict[str, Any]]:
        """Try basic pattern matching for common math problems"""
        try:
            query_lower = query.lower().strip()
            
            # Basic arithmetic patterns
            arithmetic_patterns = [
                (r'(\d+)\s*\+\s*(\d+)', lambda m: int(m.group(1)) + int(m.group(2))),
                (r'(\d+)\s*-\s*(\d+)', lambda m: int(m.group(1)) - int(m.group(2))),
                (r'(\d+)\s*\*\s*(\d+)', lambda m: int(m.group(1)) * int(m.group(2))),
                (r'(\d+)\s*/\s*(\d+)', lambda m: int(m.group(1)) / int(m.group(2)) if int(m.group(2)) != 0 else "undefined"),
                (r'(\d+)\s*\^\s*(\d+)', lambda m: int(m.group(1)) ** int(m.group(2))),
            ]
            
            for pattern, calc_func in arithmetic_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        result = calc_func(match)
                        return {
                            "found": True,
                            "solution": f"**Answer:** {result}\n\n**Calculation:** {query} = {result}",
                            "confidence": 0.95,
                            "source": "Basic Arithmetic"
                        }
                    except:
                        continue
            
            # Common formula patterns
            formula_patterns = {
                "area of circle": "**Formula:** A = πr²\n\n**Where:** A = area, r = radius, π ≈ 3.14159",
                "area of rectangle": "**Formula:** A = length × width\n\n**Where:** A = area",
                "area of triangle": "**Formula:** A = (1/2) × base × height\n\n**Where:** A = area",
                "volume of sphere": "**Formula:** V = (4/3)πr³\n\n**Where:** V = volume, r = radius",
                "volume of cube": "**Formula:** V = side³\n\n**Where:** V = volume",
                "circumference of circle": "**Formula:** C = 2πr\n\n**Where:** C = circumference, r = radius",
                "quadratic formula": "**Formula:** x = (-b ± √(b²-4ac)) / 2a\n\n**For equation:** ax² + bx + c = 0",
                "distance formula": "**Formula:** d = √[(x₂-x₁)² + (y₂-y₁)²]\n\n**Between points:** (x₁,y₁) and (x₂,y₂)",
                "slope formula": "**Formula:** m = (y₂-y₁)/(x₂-x₁)\n\n**Between points:** (x₁,y₁) and (x₂,y₂)",
                "pythagorean theorem": "**Formula:** a² + b² = c²\n\n**Where:** c = hypotenuse, a & b = other sides"
            }
            
            for pattern, solution in formula_patterns.items():
                if pattern in query_lower:
                    return {
                        "found": True,
                        "solution": solution,
                        "confidence": 0.9,
                        "source": "Formula Database"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in basic patterns: {e}")
            return None
    
    async def _try_gemini_ai(self, query: str) -> Optional[Dict[str, Any]]:
        """Use Google Gemini AI to solve the problem"""
        try:
            if not self.model:
                return None
            
            prompt = f"""
            You are a mathematical professor. Solve this math problem step by step:
            
            Problem: {query}
            
            Please provide:
            1. **Problem Analysis:** What type of problem this is
            2. **Step-by-Step Solution:** Clear, numbered steps
            3. **Final Answer:** Clearly marked final result
            4. **Explanation:** Brief explanation of concepts used
            
            Format your response clearly with markdown formatting.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    "found": True,
                    "solution": response.text,
                    "confidence": 0.85,
                    "source": "Google Gemini AI"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error with Gemini AI: {e}")
            return None

# Global instance
simple_math_solver = SimpleMathSolver()