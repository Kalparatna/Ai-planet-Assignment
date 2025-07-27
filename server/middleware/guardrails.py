from typing import Dict, Any, List, Optional, Union
import re
import logging
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIGatewayGuardrails:
    """Enhanced AI Gateway with comprehensive guardrails for educational math content"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Banned topics and terms for educational math content
        self.banned_topics = [
            "weapons", "illegal activities", "adult content", "gambling", 
            "drugs", "violence", "hate speech", "discrimination", "politics",
            "religion", "personal information", "medical advice", "legal advice"
        ]
        
        # Math-specific allowed topics and keywords
        self.allowed_math_topics = [
            "algebra", "calculus", "geometry", "trigonometry", "statistics", 
            "probability", "number theory", "discrete mathematics", "linear algebra",
            "differential equations", "mathematical analysis", "topology", "combinatorics",
            "optimization", "numerical analysis", "set theory", "logic", "arithmetic",
            "area", "volume", "perimeter", "circumference", "radius", "diameter",
            "triangle", "circle", "square", "rectangle", "polygon", "angle",
            "sine", "cosine", "tangent", "logarithm", "exponential", "matrix",
            "vector", "polynomial", "quadratic", "cubic", "linear", "formula",
            "theorem", "proof", "graph", "plot", "coordinate", "axis", "physics",
            "chemistry", "engineering mathematics", "applied mathematics"
        ]
        
        # Privacy patterns to detect and redact
        self.privacy_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),  # SSN
            (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE_REDACTED]'),  # Phone
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email
            (r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', '[CARD_REDACTED]'),  # Credit card
        ]
        
        # Initialize guardrail logs
        self.guardrail_logs = []
    
    async def advanced_content_filter(self, text: str) -> Dict[str, Any]:
        """Use LLM to perform advanced content filtering"""
        try:
            prompt = f"""
            Analyze the following text for appropriateness in an educational mathematics context.
            
            Text: "{text}"
            
            Check for:
            1. Is this related to mathematics, physics, chemistry, or educational content?
            2. Does it contain any inappropriate, harmful, or non-educational content?
            3. Is it suitable for students of all ages?
            4. Does it request personal information or contain privacy concerns?
            
            Respond with JSON format:
            {{
                "is_appropriate": true/false,
                "is_educational": true/false,
                "concerns": ["list of any concerns"],
                "confidence": 0.0-1.0,
                "reason": "explanation"
            }}
            """
            
            response = await self.llm.ainvoke(prompt)
            result = json.loads(response.content)
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced content filter: {e}")
            return {
                "is_appropriate": True,
                "is_educational": True,
                "concerns": [],
                "confidence": 0.5,
                "reason": "Filter unavailable, allowing with caution"
            }
    
    def log_guardrail_action(self, action_type: str, content: str, result: str, reason: str):
        """Log guardrail actions for monitoring and improvement"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "result": result,
            "reason": reason
        }
        self.guardrail_logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.guardrail_logs) > 1000:
            self.guardrail_logs = self.guardrail_logs[-1000:]

# Create global instance
ai_gateway = AIGatewayGuardrails()

# Banned topics and terms for educational math content
BANNED_TOPICS = [
    "weapons", "illegal activities", "adult content", "gambling", 
    "drugs", "violence", "hate speech", "discrimination"
]

# Math-specific allowed topics and keywords
ALLOWED_MATH_TOPICS = [
    "algebra", "calculus", "geometry", "trigonometry", "statistics", 
    "probability", "number theory", "discrete mathematics", "linear algebra",
    "differential equations", "mathematical analysis", "topology", "combinatorics",
    "optimization", "numerical analysis", "set theory", "logic", "arithmetic",
    "area", "volume", "perimeter", "circumference", "radius", "diameter",
    "triangle", "circle", "square", "rectangle", "polygon", "angle",
    "sine", "cosine", "tangent", "logarithm", "exponential", "matrix",
    "vector", "polynomial", "quadratic", "cubic", "linear", "formula",
    "theorem", "proof", "graph", "plot", "coordinate", "axis"
]

def input_guardrail(query: str) -> str:
    """
    Apply input guardrails to ensure the query is appropriate and math-focused
    
    Args:
        query: The user's mathematical query
        
    Returns:
        Validated query or raises an exception if inappropriate
    """
    # Convert to lowercase for checking
    query_lower = query.lower()
    
    # Check for banned topics
    for topic in BANNED_TOPICS:
        if topic in query_lower:
            logger.warning(f"Blocked query containing banned topic: {topic}")
            raise ValueError(f"Your query contains inappropriate content. Please focus on mathematical topics only.")
    
    # Check if query is related to math
    is_math_related = False
    for topic in ALLOWED_MATH_TOPICS:
        if topic in query_lower:
            is_math_related = True
            break
    
    # Check for mathematical symbols and patterns
    math_patterns = [
        r'\d+', r'[+\-*/^=]', r'\bx\b', r'\by\b', r'\bz\b',
        r'\bequation\b', r'\bsolve\b', r'\bcalculate\b', r'\bprove\b',
        r'\bintegral\b', r'\bderivative\b', r'\blimit\b', r'\bsum\b',
        r'\bfactor\b', r'\bexpand\b', r'\bsimplify\b', r'\bfunction\b'
    ]
    
    for pattern in math_patterns:
        if re.search(pattern, query_lower):
            is_math_related = True
            break
    
    if not is_math_related:
        logger.warning(f"Blocked non-math query: {query}")
        raise ValueError("Your query doesn't appear to be related to mathematics. Please ask a math question.")
    
    # Sanitize the query (remove any potentially harmful characters)
    sanitized_query = re.sub(r'[\<\>\{\}\[\]\\\`\~]', '', query)
    
    return sanitized_query

def output_guardrail(solution: str) -> str:
    """
    Apply output guardrails to ensure the solution is appropriate and educational
    
    Args:
        solution: The generated mathematical solution
        
    Returns:
        Validated solution with any inappropriate content removed
    """
    # Check for banned topics in the solution
    solution_lower = solution.lower()
    
    for topic in BANNED_TOPICS:
        if topic in solution_lower:
            logger.warning(f"Detected banned topic in solution: {topic}")
            # Replace the banned topic with [redacted]
            solution = re.sub(re.compile(topic, re.IGNORECASE), "[redacted]", solution)
    
    # Ensure solution has step-by-step explanation
    if len(solution.split('\n')) < 3 and len(solution) < 100:
        logger.warning("Solution too short, adding disclaimer")
        solution += "\n\nNote: This is a simplified answer. For a more detailed explanation, please provide more context or ask for clarification."
    
    # Add educational disclaimer for complex topics
    complex_topics = ["calculus", "differential equations", "advanced statistics"]
    for topic in complex_topics:
        if topic in solution_lower:
            solution += "\n\nNote: This topic involves advanced mathematical concepts. Consider consulting additional educational resources for deeper understanding."
            break
    
    return solution