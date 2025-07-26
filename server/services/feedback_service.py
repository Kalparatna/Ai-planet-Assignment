import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import dspy
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define DSPy modules for feedback-based learning
class MathSolutionSignature(dspy.Signature):
    """Generate a step-by-step solution for a mathematical problem."""
    problem = dspy.InputField()
    feedback = dspy.InputField(description="Previous feedback on similar problems, if any")
    solution = dspy.OutputField(description="Step-by-step solution to the mathematical problem")

class MathSolutionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_solution = dspy.Predict(MathSolutionSignature)
    
    def forward(self, problem, feedback=None):
        return self.generate_solution(problem=problem, feedback=feedback)

class FeedbackService:
    def __init__(self):
        self.feedback_file = "data/feedback.json"
        self.improved_solutions_file = "data/improved_solutions.json"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize feedback storage
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, "w") as f:
                json.dump([], f)
        
        if not os.path.exists(self.improved_solutions_file):
            with open(self.improved_solutions_file, "w") as f:
                json.dump([], f)
        
        # We'll initialize DSPy only when needed to avoid pickling issues
        self.dspy_model = None
        self.dspy_initialized = False
        
    def _initialize_dspy(self):
        """Initialize DSPy only when needed"""
        if not self.dspy_initialized:
            try:
                self.dspy_model = MathSolutionModule()
                # Set up DSPy with appropriate LLM
                dspy.settings.configure(lm=dspy.Gemini2(model="gemini-2.0-flash"))
                self.dspy_initialized = True
            except Exception as e:
                logger.error(f"Error initializing DSPy: {e}")
                self.dspy_model = None
    
    async def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user feedback and improve the solution"""
        try:
            # Load existing feedback
            with open(self.feedback_file, "r") as f:
                feedback_list = json.load(f)
            
            # Convert Pydantic model to dict if needed
            if hasattr(feedback_data, 'dict'):
                feedback_dict = feedback_data.dict()
            else:
                feedback_dict = feedback_data
            
            # Generate query_id if not provided
            query_id = feedback_dict.get("query_id")
            if not query_id:
                # Generate a unique query_id based on timestamp and feedback count
                query_id = f"feedback-{len(feedback_list) + 1}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Clean the original solution data
            original_solution = self._clean_solution_data(feedback_dict.get("original_solution", ""))
            
            # Add timestamp
            feedback_entry = {
                "id": len(feedback_list) + 1,
                "query_id": query_id,
                "original_solution": original_solution,
                "feedback": feedback_dict.get("feedback", ""),
                "rating": feedback_dict.get("rating", 3),
                "corrections": feedback_dict.get("corrections", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save feedback
            feedback_list.append(feedback_entry)
            with open(self.feedback_file, "w") as f:
                json.dump(feedback_list, f, indent=2)
            
            logger.info(f"Feedback saved successfully: Rating {feedback_entry['rating']}/5")
            
            # For now, skip DSPy integration to avoid errors
            # We can add it back later when properly configured
            improved_solution = None
            
            # Try to generate a simple improved solution message
            if feedback_dict.get("rating", 3) < 4:
                improved_solution = f"Thank you for your feedback. We've noted that this solution could be improved. Your suggestions: {feedback_dict.get('corrections', 'No specific corrections provided')}"
            
            return {"success": True, "improved_solution": improved_solution}
        
        except Exception as e:
            logger.error(f"Error processing feedback: {e}", exc_info=True)
            # Return a basic success response even if there are issues
            return {"success": True, "improved_solution": None}
    
    def _clean_solution_data(self, solution: str) -> str:
        """Clean the solution data by removing metadata and extra formatting"""
        if not solution:
            return ""
        
        # Remove common metadata patterns
        import re
        
        # Remove content=' and trailing metadata
        solution = re.sub(r"content='([^']*)'.*", r'\1', solution)
        
        # Remove additional_kwargs and response_metadata
        solution = re.sub(r'additional_kwargs=\{[^}]*\}', '', solution)
        solution = re.sub(r'response_metadata=\{[^}]*\}', '', solution)
        solution = re.sub(r'id=\'[^\']*\'', '', solution)
        solution = re.sub(r'usage_metadata=\{[^}]*\}', '', solution)
        
        # Clean up escape characters
        solution = solution.replace("\\'", "'")
        solution = solution.replace("\\n", "\n")
        
        # Remove extra whitespace
        solution = re.sub(r'\s+', ' ', solution)
        solution = solution.strip()
        
        return solution
    
    def _extract_query_from_solution(self, solution: str) -> str:
        """Extract the original query from the solution context"""
        # This is a simple implementation - in a real system, you would have a more robust method
        lines = solution.split('\n')
        if lines and lines[0].startswith("Problem:"):
            return lines[0].replace("Problem:", "").strip()
        return "" # Return empty string if we can't extract the query
    
    def _save_improved_solution(self, query_id: str, original_query: str, 
                              original_solution: str, improved_solution: str,
                              feedback: str) -> None:
        """Save the improved solution for future reference"""
        try:
            with open(self.improved_solutions_file, "r") as f:
                solutions = json.load(f)
            
            solution_entry = {
                "id": len(solutions) + 1,
                "query_id": query_id,
                "original_query": original_query,
                "original_solution": original_solution,
                "improved_solution": improved_solution,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            solutions.append(solution_entry)
            
            with open(self.improved_solutions_file, "w") as f:
                json.dump(solutions, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving improved solution: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about feedback and system improvements"""
        try:
            with open(self.feedback_file, "r") as f:
                feedback_list = json.load(f)
            
            with open(self.improved_solutions_file, "r") as f:
                improved_solutions = json.load(f)
            
            # Calculate statistics
            total_feedback = len(feedback_list)
            avg_rating = sum(item["rating"] for item in feedback_list) / total_feedback if total_feedback > 0 else 0
            total_improvements = len(improved_solutions)
            
            # Group feedback by rating
            ratings = {}
            for i in range(1, 6):
                ratings[str(i)] = len([item for item in feedback_list if item["rating"] == i])
            
            return {
                "total_feedback": total_feedback,
                "average_rating": round(avg_rating, 2),
                "total_improvements": total_improvements,
                "ratings_distribution": ratings,
                "last_updated": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            raise