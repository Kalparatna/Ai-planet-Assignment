"""
Content Generator - Handles generation of assignments and requirements documents
"""

import os
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates educational content like assignments and requirements"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    async def generate_assignment(self, topic: str, difficulty: str = "Medium", num_problems: int = 5) -> Dict[str, Any]:
        """Generate assignment requirements based on topic and difficulty"""
        try:
            # Create assignment generation prompt
            assignment_prompt = f"""
            Create a comprehensive mathematical assignment on the topic: {topic}
            
            Requirements:
            - Difficulty Level: {difficulty}
            - Number of Problems: {num_problems}
            - Include a mix of problem types (conceptual, computational, application)
            - Provide clear problem statements
            - Include a grading rubric
            - Suggest time allocation
            
            Please structure the assignment as follows:
            1. Assignment Title
            2. Learning Objectives
            3. Problems (with clear numbering and instructions)
            4. Grading Rubric
            5. Estimated Time: X hours
            6. Additional Resources (if applicable)
            
            Make sure the problems are educational, progressive in difficulty, and cover different aspects of {topic}.
            """
            
            # Generate assignment using LLM
            response = await self.llm.ainvoke(assignment_prompt)
            assignment_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "success": True,
                "assignment": assignment_content,
                "topic": topic,
                "difficulty": difficulty,
                "num_problems": num_problems,
                "generated_at": "2024-01-15T10:30:00Z"  # You might want to use actual timestamp
            }
            
        except Exception as e:
            logger.error(f"Error generating assignment: {e}")
            return {
                "success": False,
                "error": f"Failed to generate assignment: {str(e)}"
            }
    
    async def generate_requirements_document(self, project_type: str, subject: str, complexity: str = "Medium") -> Dict[str, Any]:
        """Generate requirements document for mathematical projects"""
        try:
            # Create requirements generation prompt
            requirements_prompt = f"""
            Create a detailed requirements document for a {project_type} project in {subject}.
            
            Project Details:
            - Type: {project_type}
            - Subject: {subject}
            - Complexity: {complexity}
            
            Please include the following sections:
            1. Project Overview
            2. Functional Requirements
            3. Technical Requirements
            4. Mathematical Components Required
            5. User Interface Requirements (if applicable)
            6. Performance Requirements
            7. Testing Requirements
            8. Deliverables
            9. Timeline Estimation
            10. Success Criteria
            
            Make sure the requirements are:
            - Specific and measurable
            - Technically feasible
            - Appropriate for the complexity level
            - Include relevant mathematical concepts from {subject}
            - Consider real-world applications
            """
            
            # Generate requirements using LLM
            response = await self.llm.ainvoke(requirements_prompt)
            requirements_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "success": True,
                "requirements": requirements_content,
                "project_type": project_type,
                "subject": subject,
                "complexity": complexity,
                "generated_at": "2024-01-15T10:30:00Z"  # You might want to use actual timestamp
            }
            
        except Exception as e:
            logger.error(f"Error generating requirements document: {e}")
            return {
                "success": False,
                "error": f"Failed to generate requirements document: {str(e)}"
            }