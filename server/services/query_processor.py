"""
Query Processor - Handles query classification, expansion, and relevance checking
"""

import re
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

class QueryProcessor:
    """Processes and analyzes queries for better search results"""
    
    def classify_query(self, query: str) -> str:
        """Classify query type for adaptive threshold"""
        query_lower = query.lower()
        
        # Check for specific scientific terms
        specific_terms = ['planck', 'photoelectric', 'electromagnetic', 'quantum', 'derivative', 'integral', 'momentum', 'energy']
        if any(term in query_lower for term in specific_terms):
            return 'specific_term'
        
        # Check for mathematical concepts
        math_concepts = ['equation', 'function', 'calculus', 'algebra', 'geometry', 'probability', 'solve', 'find']
        if any(concept in query_lower for concept in math_concepts):
            return 'mathematical_concept'
        
        # Check for general subjects
        if query_lower in ['physics', 'chemistry', 'mathematics', 'math']:
            return 'general_subject'
        
        return 'default'
    
    def get_adaptive_threshold(self, query_type: str) -> float:
        """Get adaptive threshold based on query type"""
        thresholds = {
            'specific_term': 0.35,      # For specific scientific terms
            'general_subject': 0.25,    # For general subjects  
            'mathematical_concept': 0.30, # For math concepts
            'default': 0.25
        }
        return thresholds.get(query_type, 0.25)
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms for better matching"""
        query_lower = query.lower()
        expanded_queries = [query]
        
        # Subject-specific keywords
        subject_keywords = {
            'physics': ['force', 'energy', 'momentum', 'electric', 'magnetic'],
            'chemistry': ['reaction', 'bond', 'molecule', 'acid', 'base'],
            'mathematics': ['equation', 'function', 'derivative', 'integral', 'algebra']
        }
        
        # Add subject-specific expansions
        for subject, keywords in subject_keywords.items():
            if subject in query_lower:
                expanded_queries.extend([f"{query} {kw}" for kw in keywords[:2]])
                break
        
        # Add common mathematical terms
        if any(term in query_lower for term in ['solve', 'find', 'calculate']):
            expanded_queries.append(f"{query} problem")
        
        return expanded_queries[:4]  # Limit to 4 variations
    
    def is_query_relevant_to_problem(self, query: str, problem: str) -> bool:
        """Check if the retrieved problem is actually relevant to the query"""
        query_lower = query.lower()
        problem_lower = problem.lower()
        
        # Extract key terms from query (remove common words)
        stop_words = {'what', 'is', 'the', 'find', 'solve', 'calculate', 'determine', 'of', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with'}
        query_terms = set(query_lower.split()) - stop_words
        problem_terms = set(problem_lower.split())
        
        # Calculate overlap ratio
        if len(query_terms) == 0:
            return True  # If no meaningful terms, accept the match
        
        overlap = len(query_terms.intersection(problem_terms))
        overlap_ratio = overlap / len(query_terms)
        
        # Require at least 50% overlap for relevance
        return overlap_ratio >= 0.5