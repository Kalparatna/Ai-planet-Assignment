"""DSPy Feedback Loop - Implements feedback-driven optimization for retrieval and generation"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
import dspy
from dspy.teleprompt import BootstrapFewShot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DSPy with the appropriate LLM
class DSPyFeedbackService:
    """Service for optimizing retrieval and generation using DSPy and feedback loops"""
    
    def __init__(self):
        # Initialize DSPy with Google's Gemini model
        api_key = os.getenv("GOOGLE_API_KEY")
        # Use langchain's GoogleGenerativeAI instead of dspy's
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Create a wrapper to adapt langchain's LLM to dspy
        class LangchainToDSPyWrapper:
            def __init__(self, langchain_llm):
                self.langchain_llm = langchain_llm
                self.kwargs = {}
                # Set default temperature
                self.temperature = 0.7
                # Add other LLM parameters that DSPy might expect
                self.max_tokens = None
                self.top_p = 1.0
                self.frequency_penalty = 0.0
                self.presence_penalty = 0.0
            
            def __call__(self, prompt, **kwargs):
                # Create a new instance of the LLM with the temperature parameter
                # This is more reliable than modifying the existing instance
                model_name = getattr(self.langchain_llm, 'model_name', 'gemini-2.5-flash')
                api_key = os.getenv("GOOGLE_API_KEY")
                
                # Create a new LLM instance with the current temperature
                temp_llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=self.temperature
                )
                
                # Use the new LLM instance to invoke the prompt
                response = temp_llm.invoke(prompt)
                return response.content
                
            # DSPy expects this method for configuring the LM
            def with_config(self, **kwargs):
                # Create a new instance with updated config
                new_wrapper = LangchainToDSPyWrapper(self.langchain_llm)
                # Copy existing attributes
                for key, value in self.__dict__.items():
                    setattr(new_wrapper, key, value)
                # Update with new config values
                for key, value in kwargs.items():
                    setattr(new_wrapper, key, value)
                return new_wrapper
        
        langchain_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
        self.llm = LangchainToDSPyWrapper(langchain_llm)
        
        # Create a simple retrieval model for DSPy
        class SimpleRM:
            def __init__(self):
                pass
                
            def __call__(self, query, k=3, **kwargs):
                # This is a simple mock retrieval model that returns empty passages
                # In a real implementation, this would connect to a vector database
                class Passage:
                    def __init__(self, text):
                        self.text = text
                        self.long_text = text
                        self.title = ""
                        self.id = 0
                        
                # Return k empty passages
                return [Passage(f"Passage {i} for query: {query}") for i in range(k)]
        
        # Configure DSPy with both LM and RM
        dspy.settings.configure(lm=self.llm, rm=SimpleRM())
        
        # Initialize optimized modules
        self.retriever_module = None
        self.solver_module = None
        self.feedback_history = []
    
    def _initialize_retriever_module(self):
        """Initialize the retrieval module using DSPy"""
        class MathRetriever(dspy.Module):
            def __init__(self):
                super().__init__()
                self.retrieve = dspy.Retrieve(k=3)
                
            def forward(self, query):
                context = self.retrieve(query).passages
                return dspy.Prediction(context=context)
        
        self.retriever_module = MathRetriever()
    
    def _initialize_solver_module(self):
        """Initialize the math solver module using DSPy"""
        class MathSolver(dspy.Module):
            def __init__(self):
                super().__init__()
                self.generate_solution = dspy.ChainOfThought(
                    "query, context -> solution"
                )
            
            def forward(self, query, context=None):
                solution = self.generate_solution(query=query, context=context or "")
                return dspy.Prediction(solution=solution.solution)
        
        self.solver_module = MathSolver()
    
    async def optimize_with_feedback(self, examples: List[Dict[str, Any]]):
        """Optimize modules using feedback examples"""
        if not self.retriever_module:
            self._initialize_retriever_module()
        
        if not self.solver_module:
            self._initialize_solver_module()
        
        # Convert examples to DSPy format
        dspy_examples = []
        for ex in examples:
            dspy_examples.append(dspy.Example(
                query=ex["query"],
                context=ex.get("context", ""),
                solution=ex["solution"]
            ))
        
        # Optimize retriever using bootstrap few-shot
        retriever_teleprompter = BootstrapFewShot(metric="contains_answer")
        self.optimized_retriever = retriever_teleprompter.compile(self.retriever_module, dspy_examples)
        
        # Optimize solver using bootstrap few-shot
        solver_teleprompter = BootstrapFewShot(metric="answer_correctness")
        self.optimized_solver = solver_teleprompter.compile(self.solver_module, dspy_examples)
        
        logger.info("Optimized retriever and solver modules with feedback examples")
    
    async def process_feedback(self, query: str, generated_solution: str, correct_solution: str, feedback: str):
        """Process user feedback to improve future generations"""
        # Add to feedback history
        self.feedback_history.append({
            "query": query,
            "generated_solution": generated_solution,
            "correct_solution": correct_solution,
            "feedback": feedback
        })
        
        # Create DSPy example from feedback
        example = dspy.Example(
            query=query,
            solution=correct_solution
        )
        
        # Re-optimize if we have enough new feedback
        if len(self.feedback_history) % 5 == 0:  # Re-optimize every 5 feedback items
            examples = []
            for item in self.feedback_history:
                examples.append(dspy.Example(
                    query=item["query"],
                    solution=item["correct_solution"]
                ))
            
            await self.optimize_with_feedback(examples)
    
    async def retrieve_with_feedback(self, query: str) -> List[str]:
        """Retrieve relevant context using feedback-optimized retriever"""
        # Initialize retriever if not already done
        if not hasattr(self, 'retriever_module') or self.retriever_module is None:
            self._initialize_retriever_module()
            logger.warning("Using unoptimized retriever - no feedback data yet")
        
        # Use optimized retriever if available, otherwise use base retriever
        retriever = self.optimized_retriever if hasattr(self, 'optimized_retriever') and self.optimized_retriever is not None else self.retriever_module
        
        # Get prediction from retriever (synchronously since AsyncPrompt doesn't exist)
        prediction = retriever(query)
        
        return prediction.context
    
    async def solve_with_feedback(self, query: str, context: Optional[str] = None) -> str:
        """Generate solution using feedback-optimized solver"""
        if not hasattr(self, 'optimized_solver') or self.optimized_solver is None:
            self._initialize_solver_module()
            logger.warning("Using unoptimized solver - no feedback data yet")
            solver = self.solver_module
        else:
            solver = self.optimized_solver
        
        # Get prediction from solver (synchronously since AsyncPrompt doesn't exist)
        prediction = solver(query=query, context=context or "")
        
        return prediction.solution
    
    async def end_to_end_solution(self, query: str) -> Dict[str, Any]:
        """Generate end-to-end solution using optimized modules"""
        # First retrieve relevant context
        context = await self.retrieve_with_feedback(query)
        
        # Then generate solution using context
        solution = await self.solve_with_feedback(query, context)
        
        return {
            "found": True,
            "solution": solution,
            "confidence": 0.9,  # Optimized solutions have high confidence
            "source": "dspy_optimized",
            "references": ["🧠 DSPy Optimized Solution"]
        }
        
    async def solve_problem(self, query: str) -> Dict[str, Any]:
        """Alias for end_to_end_solution to maintain compatibility with math_router.py"""
        return await self.end_to_end_solution(query)