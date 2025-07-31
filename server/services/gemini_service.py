#!/usr/bin/env python3
"""
Google Gemini Service - Using correct Google Gemini API
Based on the sample code provided by the user
"""

import os
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """Service for Google Gemini API using the correct approach"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        
        if self.google_api_key:
            try:
                # Configure Gemini API
                genai.configure(api_key=self.google_api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Google Gemini model initialized successfully")
            except Exception as e:
                logger.error(f"❌ Error initializing Gemini model: {e}")
                self.model = None
        else:
            logger.warning("⚠️ GOOGLE_API_KEY not found - Gemini service disabled")
            self.model = None
    
    async def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Google Gemini API - concise responses"""
        try:
            if not self.model:
                return None
            
            # Add instruction for concise responses
            concise_prompt = f"""
            {prompt}
            
            Instructions: Be concise and direct. Avoid unnecessary explanations. Focus on essential information only.
            """
            
            response = self.model.generate_content(concise_prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            return None
    
    async def solve_math_problem(self, query: str) -> Dict[str, Any]:
        """Solve math problem using Gemini"""
        try:
            if not self.model:
                return {
                    "found": False,
                    "error": "Gemini model not available"
                }
            
            # Create a concise math prompt for focused solutions
            prompt = f"""
            Solve this math problem with simple, clear steps. Be concise and direct.

            Problem: {query}

            Instructions:
            - Show only essential steps
            - No lengthy explanations
            - Use simple language
            - Focus on the solution process
            - End with the final answer

            Format:
            Step 1: [action]
            Step 2: [action]
            ...
            Answer: [final result]
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    "found": True,
                    "solution": response.text,
                    "confidence": 0.9,
                    "source": "Google Gemini AI"
                }
            else:
                return {
                    "found": False,
                    "error": "No response from Gemini"
                }
                
        except Exception as e:
            logger.error(f"Error solving math problem with Gemini: {e}")
            return {
                "found": False,
                "error": f"Gemini error: {str(e)}"
            }
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.model is not None

# Global Gemini service instance
gemini_service = GeminiService()