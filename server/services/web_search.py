import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.search_history_file = "data/search_history.json"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize search history
        if not os.path.exists(self.search_history_file):
            with open(self.search_history_file, "w") as f:
                json.dump([], f)
        
        # Initialize Gemini for content formatting
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self.google_api_key,
                temperature=0.2,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
            logger.info("Gemini initialized for web search content formatting")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.llm = None
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search the web for mathematical problems and solutions"""
        try:
            # First try Tavily API for specialized search
            tavily_result = await self._search_tavily(query)
            
            if tavily_result and tavily_result.get("found", False):
                return tavily_result
            
            # If Tavily fails or doesn't find good results, try direct web scraping
            scrape_result = await self._scrape_math_sites(query)
            
            if scrape_result and scrape_result.get("found", False):
                return scrape_result
            
            # If all else fails, return not found
            return {"found": False}
        
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {"found": False}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _search_tavily(self, query: str) -> Dict[str, Any]:
        """Search using Tavily API for specialized search"""
        try:
            if not self.tavily_api_key:
                logger.warning("Tavily API key not found")
                return {"found": False}
            
            # Enhance query for mathematical context
            enhanced_query = f"mathematical problem solution step by step: {query}"
            
            # Call Tavily API with correct format
            payload = {
                "api_key": self.tavily_api_key,
                "query": enhanced_query,
                "search_depth": "advanced",
                "include_domains": [
                    "khanacademy.org", "mathsisfun.com", "purplemath.com", 
                    "mathworld.wolfram.com", "brilliant.org", "mathway.com",
                    "symbolab.com", "socratic.org", "chegg.com", "mathsgenie.co.uk"
                ],
                "max_results": 5,
                "include_answer": True,
                "include_raw_content": True
            }
            
            response = requests.post(
                "https://api.tavily.com/search",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Tavily API error: {response.status_code} - {response.text}")
                return {"found": False}
            
            result = response.json()
            
            # Process and extract solution
            if result and "results" in result and len(result["results"]) > 0:
                # Extract content from results
                content = ""
                references = []
                
                for item in result["results"]:
                    content += item.get("content", "") + "\n\n"
                    references.append(item.get("url", ""))
                
                # Extract mathematical solution
                solution = await self._extract_math_solution(content, query)
                
                if solution:
                    # Save search history
                    self._save_search_history(query, solution, references)
                    
                    return {
                        "found": True,
                        "solution": solution,
                        "confidence": 0.85,
                        "references": references
                    }
            
            return {"found": False}
        
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            return {"found": False}
    
    async def _scrape_math_sites(self, query: str) -> Dict[str, Any]:
        """Scrape popular math websites for solutions"""
        try:
            # List of math websites to scrape
            math_sites = [
                f"https://www.mathway.com/Algebra?problem={query}",
                f"https://www.wolframalpha.com/input?i={query}",
                f"https://www.symbolab.com/solver?or=goog&query={query}"
            ]
            
            for site in math_sites:
                try:
                    response = requests.get(
                        site,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Parse HTML
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        # Extract content based on the site
                        content = ""
                        if "mathway.com" in site:
                            # Extract from Mathway
                            steps_div = soup.find("div", {"class": "steps"})
                            if steps_div:
                                content = steps_div.get_text()
                        
                        elif "wolframalpha.com" in site:
                            # Extract from WolframAlpha
                            result_divs = soup.find_all("div", {"class": "_9JgWwX8"})
                            for div in result_divs:
                                content += div.get_text() + "\n"
                        
                        elif "symbolab.com" in site:
                            # Extract from Symbolab
                            steps_div = soup.find("div", {"class": "solution-step"})
                            if steps_div:
                                content = steps_div.get_text()
                        
                        # Extract solution
                        solution = await self._extract_math_solution(content, query)
                        
                        if solution:
                            # Save search history
                            self._save_search_history(query, solution, [site])
                            
                            return {
                                "found": True,
                                "solution": solution,
                                "confidence": 0.75,
                                "references": [site]
                            }
                
                except Exception as e:
                    logger.error(f"Error scraping {site}: {e}")
                    continue
            
            return {"found": False}
        
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            return {"found": False}
    
    async def _extract_math_solution(self, content: str, query: str) -> Optional[str]:
        """Extract and format a mathematical solution from web content using Gemini"""
        if not content:
            return None
        
        # Clean up the content
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Check if content is substantial enough
        if len(content) < 50:
            return None
        
        # Use Gemini to format the web search content into a proper mathematical solution
        if self.llm:
            try:
                prompt = f"""
                You are a mathematical professor. I found some content from web search about a mathematical problem, but it's messy and unstructured. Please format it into a clean, step-by-step mathematical solution.

                Original Question: {query}

                Web Search Content:
                {content}

                Please provide a clean, educational solution with:
                1. Clear problem statement
                2. Step-by-step solution with proper mathematical notation
                3. Final answer
                4. Brief explanation of the mathematical concepts used

                Format it as a proper mathematical solution that a student can easily understand. Remove any unnecessary content, advertisements, or irrelevant information. Focus only on the mathematical solution.

                Do not include any references to websites or sources in the solution itself - just provide the clean mathematical content.
                """
                
                response = await self.llm.ainvoke(prompt)
                
                # Extract content from response
                if hasattr(response, 'content'):
                    formatted_solution = response.content
                else:
                    formatted_solution = str(response)
                
                # Clean up the formatted solution
                formatted_solution = formatted_solution.strip()
                
                # Ensure it starts with "Problem:" if not already
                if not formatted_solution.startswith("Problem:"):
                    formatted_solution = f"Problem: {query}\n\n{formatted_solution}"
                
                return formatted_solution
                
            except Exception as e:
                logger.error(f"Error formatting solution with Gemini: {e}")
                # Fall back to basic formatting if Gemini fails
                return self._basic_format_solution(content, query)
        else:
            # Fall back to basic formatting if Gemini is not available
            return self._basic_format_solution(content, query)
    
    def _basic_format_solution(self, content: str, query: str) -> str:
        """Basic formatting fallback when Gemini is not available"""
        solution = f"Problem: {query}\n\n"
        
        # Look for step indicators
        steps = re.findall(r'(Step \d+[:.\s].*?)(?=Step \d+|$)', content, re.IGNORECASE | re.DOTALL)
        
        if steps:
            solution += "Solution:\n\n"
            for i, step in enumerate(steps, 1):
                solution += f"Step {i}: {step.strip()}\n\n"
        else:
            # If no explicit steps, try to break into logical parts
            sentences = re.split(r'(?<=[.!?])\s+', content)
            
            if len(sentences) > 3:
                solution += "Solution:\n\n"
                solution += "Step 1: Understanding the problem\n"
                solution += sentences[0] + "\n\n"
                
                solution += "Step 2: Solution approach\n"
                solution += " ".join(sentences[1:3]) + "\n\n"
                
                solution += "Step 3: Solving\n"
                solution += " ".join(sentences[3:min(len(sentences), 6)]) + "\n\n"
                
                if len(sentences) > 6:
                    solution += "Step 4: Final answer\n"
                    solution += " ".join(sentences[6:]) + "\n\n"
            else:
                # Not enough content to structure, just use as is
                solution += "Solution:\n" + content[:500] + "...\n\n"
        
        return solution
    
    def _save_search_history(self, query: str, solution: str, references: List[str]) -> None:
        """Save search history for future reference"""
        try:
            with open(self.search_history_file, "r") as f:
                history = json.load(f)
            
            entry = {
                "query": query,
                "solution": solution,
                "references": references,
                "timestamp": import_datetime().now().isoformat()
            }
            
            history.append(entry)
            
            with open(self.search_history_file, "w") as f:
                json.dump(history, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving search history: {e}")

# Helper function to import datetime (to avoid circular imports)
def import_datetime():
    from datetime import datetime
    return datetime