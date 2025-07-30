import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MathSolverService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.solutions_file = "data/generated_solutions.json"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize solutions storage
        if not os.path.exists(self.solutions_file):
            with open(self.solutions_file, "w") as f:
                json.dump([], f)
        
        # Initialize LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.google_api_key,
                temperature=0.2,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
            
            # Create solution generation prompt
            solution_template = """
            You are an expert mathematics professor. Your task is to provide a clear, step-by-step solution to the following mathematical problem. 
            Make sure your explanation is educational, precise, and easy to follow for students.
            
            PROBLEM: {problem}
            
            Please structure your solution as follows:
            1. First, identify what type of mathematical problem this is and what concepts are involved.
            2. Break down the solution into clear, numbered steps.
            3. Explain each step thoroughly, including the mathematical principles being applied.
            4. Show all work and calculations.
            5. Provide a final answer clearly marked.
            6. If applicable, verify the solution by checking or testing it.
            
            Your solution should be detailed enough that a student can learn from it, not just see the answer.
            """
            
            self.solution_prompt = PromptTemplate(
                template=solution_template,
                input_variables=["problem"]
            )
            
            # Create the chain using the new RunnableSequence approach
            self.solution_chain = self.solution_prompt | self.llm
        
        except Exception as e:
            logger.error(f"Error initializing MathSolverService: {e}")
            self.llm = None
            self.solution_chain = None
    
    async def generate_solution(self, problem: str) -> Dict[str, Any]:
        """Generate a step-by-step solution for a mathematical problem"""
        try:
            if not self.solution_chain:
                return {"solution": "Sorry, I'm unable to generate a solution at the moment. Please try again later.", "confidence": 0}
            
            # Generate solution using the new invoke method
            result = await self.solution_chain.ainvoke({"problem": problem})
            
            # Extract content from LangChain response
            if hasattr(result, 'content'):
                solution_content = result.content
            elif isinstance(result, str):
                solution_content = result
            else:
                solution_content = str(result)
            
            # Format the solution
            formatted_solution = f"Problem: {problem}\n\nSolution: {solution_content}"
            
            # Save the generated solution
            self._save_solution(problem, formatted_solution)
            
            return {
                "solution": formatted_solution,
                "confidence": 0.7  # Lower confidence for generated solutions
            }
        
        except Exception as e:
            logger.error(f"Error generating solution: {e}")
            return {"solution": "Sorry, I encountered an error while generating the solution. Please try a different question.", "confidence": 0}
    
    def format_solution(self, solution: str, problem: str) -> str:
        """Simple solution formatting - detailed formatting is handled by ResponseFormatter"""
        
        # Just return the solution with minimal formatting
        # The ResponseFormatter will handle all the complex formatting
        if solution.strip():
            return solution.strip()
        else:
            return f"Solution for: {problem}"
    

    
    def _save_solution(self, problem: str, solution: str) -> None:
        """Save generated solution for future reference"""
        try:
            with open(self.solutions_file, "r") as f:
                solutions = json.load(f)
            
            entry = {
                "problem": problem,
                "solution": solution,
                "timestamp": import_datetime().now().isoformat()
            }
            
            solutions.append(entry)
            
            with open(self.solutions_file, "w") as f:
                json.dump(solutions, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving solution: {e}")

# Helper function to import datetime (to avoid circular imports)
def import_datetime():
    from datetime import datetime
    return datetime

# Import regex for formatting
import re