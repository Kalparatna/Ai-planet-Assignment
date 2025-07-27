import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import dspy
from pydantic import BaseModel
import hashlib
import re
from langchain_google_genai import ChatGoogleGenerativeAI

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
        self.learning_patterns_file = "data/learning_patterns.json"
        self.quality_control_file = "data/quality_control.json"
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize all storage files
        for file_path in [self.feedback_file, self.improved_solutions_file, 
                         self.learning_patterns_file, self.quality_control_file]:
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    json.dump([], f)
        
        # Initialize LLM for solution improvement (fallback from DSPy)
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.3
            )
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            self.llm = None
        
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
        """Process user feedback and implement Human-in-the-Loop learning"""
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
                query_id = f"feedback-{len(feedback_list) + 1}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Clean the original solution data
            original_solution = self._clean_solution_data(feedback_dict.get("original_solution", ""))
            original_query = self._extract_query_from_solution(original_solution)
            
            # Create comprehensive feedback entry
            feedback_entry = {
                "id": len(feedback_list) + 1,
                "query_id": query_id,
                "original_query": original_query,
                "original_solution": original_solution,
                "feedback": feedback_dict.get("feedback", ""),
                "rating": feedback_dict.get("rating", 3),
                "corrections": feedback_dict.get("corrections", ""),
                "timestamp": datetime.now().isoformat(),
                "processed": False,
                "improvement_generated": False
            }
            
            # Save feedback
            feedback_list.append(feedback_entry)
            with open(self.feedback_file, "w") as f:
                json.dump(feedback_list, f, indent=2)
            
            logger.info(f"Feedback saved successfully: Rating {feedback_entry['rating']}/5")
            
            # HITL Processing: Generate improved solution if rating is low
            improved_solution = None
            if feedback_dict.get("rating", 3) < 4:
                improved_solution = await self._generate_improved_solution(
                    original_query, original_solution, 
                    feedback_dict.get("feedback", ""), 
                    feedback_dict.get("corrections", "")
                )
                
                if improved_solution:
                    # Save the improved solution
                    self._save_improved_solution(
                        query_id, original_query, original_solution, 
                        improved_solution, feedback_dict.get("feedback", "")
                    )
                    
                    # Update feedback entry
                    feedback_entry["improvement_generated"] = True
                    feedback_list[-1] = feedback_entry
                    with open(self.feedback_file, "w") as f:
                        json.dump(feedback_list, f, indent=2)
            
            # Update learning patterns
            await self._update_learning_patterns(feedback_entry)
            
            # Quality control check
            await self._quality_control_check(feedback_entry)
            
            # Mark as processed
            feedback_entry["processed"] = True
            feedback_list[-1] = feedback_entry
            with open(self.feedback_file, "w") as f:
                json.dump(feedback_list, f, indent=2)
            
            return {
                "success": True, 
                "improved_solution": improved_solution,
                "learning_applied": True,
                "quality_checked": True
            }
        
        except Exception as e:
            logger.error(f"Error processing feedback: {e}", exc_info=True)
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
    
    async def _generate_improved_solution(self, query: str, original_solution: str, 
                                        feedback: str, corrections: str) -> Optional[str]:
        """Generate an improved solution based on user feedback"""
        try:
            if not self.llm:
                return None
            
            # Create improvement prompt
            improvement_prompt = f"""
            You are a mathematics professor tasked with improving a solution based on student feedback.
            
            Original Problem: {query}
            
            Original Solution: {original_solution}
            
            Student Feedback: {feedback}
            
            Student Corrections/Suggestions: {corrections}
            
            Please provide an improved step-by-step solution that addresses the feedback and incorporates the corrections.
            Make sure the solution is:
            1. Mathematically accurate
            2. Clear and easy to follow
            3. Addresses the specific issues mentioned in the feedback
            4. Incorporates valid corrections provided by the student
            
            Improved Solution:
            """
            
            response = await self.llm.ainvoke(improvement_prompt)
            improved_solution = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Generated improved solution based on feedback")
            return improved_solution
            
        except Exception as e:
            logger.error(f"Error generating improved solution: {e}")
            return None
    
    async def _update_learning_patterns(self, feedback_entry: Dict[str, Any]) -> None:
        """Update learning patterns based on feedback to improve future responses"""
        try:
            with open(self.learning_patterns_file, "r") as f:
                patterns = json.load(f)
            
            # Extract learning insights from feedback
            query_type = self._classify_problem_type(feedback_entry.get("original_query", ""))
            rating = feedback_entry.get("rating", 3)
            feedback_text = feedback_entry.get("feedback", "")
            corrections = feedback_entry.get("corrections", "")
            
            # Create learning pattern entry
            pattern_entry = {
                "id": len(patterns) + 1,
                "query_type": query_type,
                "rating": rating,
                "feedback_summary": self._extract_feedback_insights(feedback_text),
                "common_issues": self._identify_common_issues(feedback_text, corrections),
                "improvement_areas": self._identify_improvement_areas(corrections),
                "timestamp": datetime.now().isoformat(),
                "query_hash": hashlib.md5(feedback_entry.get("original_query", "").encode()).hexdigest()[:8]
            }
            
            patterns.append(pattern_entry)
            
            # Keep only last 1000 patterns to prevent file from growing too large
            if len(patterns) > 1000:
                patterns = patterns[-1000:]
            
            with open(self.learning_patterns_file, "w") as f:
                json.dump(patterns, f, indent=2)
            
            logger.info(f"Updated learning patterns for {query_type} problems")
            
        except Exception as e:
            logger.error(f"Error updating learning patterns: {e}")
    
    async def _quality_control_check(self, feedback_entry: Dict[str, Any]) -> None:
        """Perform quality control checks and flag issues for human review"""
        try:
            with open(self.quality_control_file, "r") as f:
                quality_issues = json.load(f)
            
            rating = feedback_entry.get("rating", 3)
            feedback_text = feedback_entry.get("feedback", "").lower()
            
            # Define quality control triggers
            needs_review = False
            issue_type = []
            
            # Low rating trigger
            if rating <= 2:
                needs_review = True
                issue_type.append("low_rating")
            
            # Negative feedback keywords
            negative_keywords = ["wrong", "incorrect", "error", "mistake", "bad", "terrible", "useless"]
            if any(keyword in feedback_text for keyword in negative_keywords):
                needs_review = True
                issue_type.append("negative_feedback")
            
            # Mathematical accuracy concerns
            accuracy_keywords = ["calculation", "formula", "method", "approach", "solution is wrong"]
            if any(keyword in feedback_text for keyword in accuracy_keywords):
                needs_review = True
                issue_type.append("accuracy_concern")
            
            if needs_review:
                quality_entry = {
                    "id": len(quality_issues) + 1,
                    "feedback_id": feedback_entry.get("id"),
                    "query_id": feedback_entry.get("query_id"),
                    "issue_types": issue_type,
                    "priority": "high" if rating <= 2 else "medium",
                    "original_query": feedback_entry.get("original_query", ""),
                    "rating": rating,
                    "feedback": feedback_entry.get("feedback", ""),
                    "corrections": feedback_entry.get("corrections", ""),
                    "status": "pending_review",
                    "timestamp": datetime.now().isoformat()
                }
                
                quality_issues.append(quality_entry)
                
                with open(self.quality_control_file, "w") as f:
                    json.dump(quality_issues, f, indent=2)
                
                logger.warning(f"Quality control issue flagged: {issue_type} for query {feedback_entry.get('query_id')}")
            
        except Exception as e:
            logger.error(f"Error in quality control check: {e}")
    
    def _classify_problem_type(self, query: str) -> str:
        """Classify the type of mathematical problem"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["derivative", "differentiate", "d/dx"]):
            return "calculus_derivatives"
        elif any(word in query_lower for word in ["integral", "integrate", "∫"]):
            return "calculus_integrals"
        elif any(word in query_lower for word in ["quadratic", "x²", "x^2"]):
            return "algebra_quadratic"
        elif any(word in query_lower for word in ["linear", "slope", "y = mx"]):
            return "algebra_linear"
        elif any(word in query_lower for word in ["triangle", "circle", "area", "volume"]):
            return "geometry"
        elif any(word in query_lower for word in ["probability", "statistics", "mean", "median"]):
            return "statistics"
        elif any(word in query_lower for word in ["matrix", "vector", "eigenvalue"]):
            return "linear_algebra"
        else:
            return "general_math"
    
    def _extract_feedback_insights(self, feedback: str) -> str:
        """Extract key insights from feedback text"""
        feedback_lower = feedback.lower()
        
        insights = []
        
        if "confusing" in feedback_lower or "unclear" in feedback_lower:
            insights.append("clarity_issue")
        if "step" in feedback_lower and ("missing" in feedback_lower or "skip" in feedback_lower):
            insights.append("missing_steps")
        if "explanation" in feedback_lower and ("need" in feedback_lower or "want" in feedback_lower):
            insights.append("needs_more_explanation")
        if "example" in feedback_lower:
            insights.append("needs_examples")
        if "formula" in feedback_lower and "wrong" in feedback_lower:
            insights.append("formula_error")
        
        return ", ".join(insights) if insights else "general_feedback"
    
    def _identify_common_issues(self, feedback: str, corrections: str) -> List[str]:
        """Identify common issues from feedback and corrections"""
        issues = []
        combined_text = (feedback + " " + corrections).lower()
        
        issue_patterns = {
            "calculation_error": ["calculation", "arithmetic", "math error", "wrong number"],
            "method_error": ["wrong method", "approach", "technique", "procedure"],
            "missing_steps": ["missing step", "skip", "jump", "not shown"],
            "unclear_explanation": ["confusing", "unclear", "hard to understand", "explain better"],
            "formatting_issue": ["format", "presentation", "layout", "structure"]
        }
        
        for issue_type, keywords in issue_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                issues.append(issue_type)
        
        return issues
    
    def _identify_improvement_areas(self, corrections: str) -> List[str]:
        """Identify specific areas for improvement from corrections"""
        if not corrections:
            return []
        
        corrections_lower = corrections.lower()
        improvements = []
        
        improvement_patterns = {
            "add_more_steps": ["add step", "show work", "more detail", "break down"],
            "fix_calculation": ["calculate", "compute", "result", "answer"],
            "improve_explanation": ["explain", "clarify", "describe", "elaborate"],
            "correct_method": ["method", "approach", "way", "technique"],
            "add_examples": ["example", "instance", "case", "illustration"]
        }
        
        for improvement_type, keywords in improvement_patterns.items():
            if any(keyword in corrections_lower for keyword in keywords):
                improvements.append(improvement_type)
        
        return improvements
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning patterns for system improvement"""
        try:
            with open(self.learning_patterns_file, "r") as f:
                patterns = json.load(f)
            
            if not patterns:
                return {"message": "No learning patterns available yet"}
            
            # Analyze patterns
            problem_types = {}
            common_issues = {}
            improvement_areas = {}
            
            for pattern in patterns:
                # Count problem types
                ptype = pattern.get("query_type", "unknown")
                problem_types[ptype] = problem_types.get(ptype, 0) + 1
                
                # Count common issues
                for issue in pattern.get("common_issues", []):
                    common_issues[issue] = common_issues.get(issue, 0) + 1
                
                # Count improvement areas
                for area in pattern.get("improvement_areas", []):
                    improvement_areas[area] = improvement_areas.get(area, 0) + 1
            
            # Get top issues and improvements
            top_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            top_improvements = sorted(improvement_areas.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_patterns": len(patterns),
                "problem_type_distribution": problem_types,
                "top_common_issues": dict(top_issues),
                "top_improvement_areas": dict(top_improvements),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {"error": str(e)}
    
    async def get_quality_control_issues(self) -> Dict[str, Any]:
        """Get pending quality control issues for human review"""
        try:
            with open(self.quality_control_file, "r") as f:
                quality_issues = json.load(f)
            
            # Filter pending issues
            pending_issues = [issue for issue in quality_issues if issue.get("status") == "pending_review"]
            
            # Group by priority
            high_priority = [issue for issue in pending_issues if issue.get("priority") == "high"]
            medium_priority = [issue for issue in pending_issues if issue.get("priority") == "medium"]
            
            return {
                "total_pending": len(pending_issues),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "high_priority_issues": high_priority[:10],  # Limit to 10 for API response
                "medium_priority_issues": medium_priority[:10],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quality control issues: {e}")
            return {"error": str(e)}
    
    async def resolve_quality_issue(self, issue_id: int, resolution: str, reviewer: str) -> Dict[str, Any]:
        """Mark a quality control issue as resolved"""
        try:
            with open(self.quality_control_file, "r") as f:
                quality_issues = json.load(f)
            
            # Find and update the issue
            for issue in quality_issues:
                if issue.get("id") == issue_id:
                    issue["status"] = "resolved"
                    issue["resolution"] = resolution
                    issue["reviewer"] = reviewer
                    issue["resolved_at"] = datetime.now().isoformat()
                    break
            else:
                return {"success": False, "error": "Issue not found"}
            
            with open(self.quality_control_file, "w") as f:
                json.dump(quality_issues, f, indent=2)
            
            logger.info(f"Quality control issue {issue_id} resolved by {reviewer}")
            return {"success": True, "message": "Issue resolved successfully"}
            
        except Exception as e:
            logger.error(f"Error resolving quality issue: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_improved_solution_for_query(self, query: str) -> Optional[str]:
        """Get improved solution for a similar query if available"""
        try:
            with open(self.improved_solutions_file, "r") as f:
                improved_solutions = json.load(f)
            
            # Simple similarity check (in production, use embeddings)
            query_lower = query.lower()
            for solution in improved_solutions:
                original_query = solution.get("original_query", "").lower()
                if self._calculate_similarity(query_lower, original_query) > 0.7:
                    return solution.get("improved_solution")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting improved solution: {e}")
            return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation (Jaccard similarity)"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0