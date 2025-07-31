#!/usr/bin/env python3
"""
Web Search Service - ENHANCED
Complete medium-length solutions with proper source attribution
"""

import os
import asyncio
import logging
import re
from typing import Dict, Any, List
from dotenv import load_dotenv
from .connection_manager import connection_manager
from .mongodb_service import mongodb_service

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchService:
    """Enhanced Web Search - Complete solutions with clean source attribution"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
    async def search(self, query: str, timeout: float = 6.5) -> Dict[str, Any]:
        """
        Enhanced search with complete medium-length solutions
        Args:
            query: The search query
            timeout: Maximum time in seconds to wait for response (default: 6.5)
        Returns:
            Dict containing search results or fallback response
        """
        try:
            if not self.tavily_api_key:
                logger.warning("❌ Tavily API key not found")
                return await self._generate_ai_fallback_solution(query)
            
            logger.info(f"🌐 Web search: {query[:50]}...")
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": f"complete step by step mathematical solution: {query}",
                "search_depth": "basic",
                "include_domains": [
                    "mathsisfun.com",
                    "khanacademy.org",
                    "chegg.com",
                    "symbolab.com",
                    "mathway.com",
                    "wolframalpha.com"
                ],
                "max_results": 3,
                "include_answer": True,
                "include_raw_content": True
            }
            try:
                result = await asyncio.wait_for(
                    connection_manager.post_json(
                        "https://api.tavily.com/search",
                        payload
                    ),
                    timeout=timeout
                )

                if result and "results" in result and result["results"]:
                    # Process results for complete medium-length solution
                    combined_content = ""
                    source_names = []

                    for i, item in enumerate(result["results"][:3]):  # Max 3 sources
                        item_content = item.get("content", "")
                        if item_content and len(item_content) > 50:
                            combined_content += item_content + " "
                            # Extract clean source name from URL
                            source_name = self._extract_source_name(item.get("url", ""))
                            source_names.append(source_name)

                    if combined_content:
                        # Create complete medium-length solution
                        complete_solution = self._create_complete_solution(combined_content, query)

                        # 🚀 Store in MongoDB for ultra-fast future access
                        await mongodb_service.store_web_search_cache(
                            query, 
                            complete_solution, 
                            source_names[:3], 
                            0.8
                        )

                        return {
                            "found": True,
                            "solution": complete_solution,
                            "confidence": 0.8,
                            "references": source_names[:3]  # Clean source names only
                        }

            except Exception as e:
                logger.info("❌ No valid results from web search, generating AI solution")
                return await self._generate_ai_fallback_solution(query)

            
        except asyncio.TimeoutError:
            logger.warning("⏰ Web search timed out, generating AI solution")
            return await self._generate_ai_fallback_solution(query)
        except Exception as e:
            logger.error(f"❌ Web search error: {e}, generating AI solution")
            return await self._generate_ai_fallback_solution(query)
    
    def _create_complete_solution(self, content: str, query: str) -> str:
        """Create complete medium-length solution from web content"""
        try:
            # Clean and normalize content
            clean_content = re.sub(r'\s+', ' ', content).strip()
            
            # Remove web garbage and navigation elements
            garbage_patterns = [
                r'cookie\s+policy.*?(?=\.|$)',
                r'privacy.*?(?=\.|$)',
                r'advertisement.*?(?=\.|$)',
                r'subscribe.*?(?=\.|$)',
                r'login.*?(?=\.|$)',
                r'menu.*?(?=\.|$)',
                r'navigation.*?(?=\.|$)',
                r'footer.*?(?=\.|$)',
                r'header.*?(?=\.|$)',
                r'sidebar.*?(?=\.|$)'
            ]
            
            for pattern in garbage_patterns:
                clean_content = re.sub(pattern, '', clean_content, flags=re.IGNORECASE)
            
            # Extract mathematical content with better filtering
            math_content = []
            sentences = clean_content.split('.')
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15:
                    # Check for mathematical indicators
                    math_indicators = [
                        '=', 'formula', 'step', 'solve', 'answer', 'calculate', 
                        'solution', 'method', 'approach', 'theorem', 'rule',
                        '+', '-', '×', '÷', '²', '³', '√', 'x', 'y', 'z'
                    ]
                    
                    if any(indicator in sentence.lower() for indicator in math_indicators):
                        math_content.append(sentence)
            
            # Build complete medium-length solution
            if math_content:
                # Take more sentences for complete solution (5-8 sentences)
                selected_content = math_content[:8]
                solution_text = '. '.join(selected_content)
                
                # Ensure medium length (300-800 characters)
                if len(solution_text) < 300 and len(clean_content) > 300:
                    # Add more context if solution is too short
                    additional_sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
                    for sentence in additional_sentences:
                        if sentence not in solution_text:
                            solution_text += '. ' + sentence
                            if len(solution_text) >= 300:
                                break
                
                # Trim if too long (keep under 800 characters)
                if len(solution_text) > 800:
                    solution_text = solution_text[:797] + "..."
                
                return solution_text
            else:
                # Fallback: use first meaningful part of content
                meaningful_content = clean_content[:600] + "..." if len(clean_content) > 600 else clean_content
                return meaningful_content
            
        except Exception as e:
            logger.error(f"Error creating complete solution: {e}")
            return content[:400] + "..." if len(content) > 400 else content
    
    def _extract_source_name(self, url: str) -> str:
        """Extract clean source name from URL"""
        try:
            if not url:
                return "Web Source"
            
            # Extract domain name
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                
                # Clean up common domain patterns
                domain_mappings = {
                    'mathsisfun.com': 'Math is Fun',
                    'khanacademy.org': 'Khan Academy',
                    'chegg.com': 'Chegg',
                    'symbolab.com': 'Symbolab',
                    'mathway.com': 'Mathway',
                    'wolframalpha.com': 'Wolfram Alpha',
                    'stackoverflow.com': 'Stack Overflow',
                    'math.stackexchange.com': 'Math Stack Exchange',
                    'brilliant.org': 'Brilliant',
                    'coursera.org': 'Coursera'
                }
                
                return domain_mappings.get(domain, domain.replace('.com', '').replace('.org', '').title())
            
            return "Web Source"
            
        except Exception as e:
            logger.error(f"Error extracting source name: {e}")
            return "Web Source"
    
    async def _generate_ai_fallback_solution(self, query: str) -> Dict[str, Any]:
        """Generate AI solution when web search fails or times out"""
        try:
            logger.info("🤖 Generating AI fallback solution...")
            
            # Import the AI solver
            from .specialized_math_solver import ImprovedMathSolver
            improved_solver = ImprovedMathSolver()
            
            # Generate comprehensive solution
            ai_result = await improved_solver.generate_comprehensive_solution(query)
            
            return {
                "found": True,
                "solution": ai_result.get("solution", "Unable to generate solution"),
                "confidence": ai_result.get("confidence", 0.75),
                "references": ["AI Generated Solution"]
            }
            
        except Exception as e:
            logger.error(f"Error generating AI fallback solution: {e}")
            return {
                "found": False,
                "solution": "Unable to find or generate solution",
                "confidence": 0.0,
                "references": []
            }

# Global web search service instance
web_search_service = WebSearchService()