from typing import Dict, Any, List, Optional, Union
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Banned topics and terms for educational math content
BANNED_TOPICS = [
    "weapons", "illegal activities", "adult content", "gambling", 
    "drugs", "violence", "hate speech", "discrimination"
]

# Math-specific allowed topics
ALLOWED_MATH_TOPICS = [
    "algebra", "calculus", "geometry", "trigonometry", "statistics", 
    "probability", "number theory", "discrete mathematics", "linear algebra",
    "differential equations", "mathematical analysis", "topology", "combinatorics",
    "optimization", "numerical analysis", "set theory", "logic", "arithmetic"
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