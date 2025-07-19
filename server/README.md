# Math Routing Agent - Server

This is the FastAPI backend for the Math Routing Agent, an Agentic-RAG architecture system that replicates a mathematical professor. The system understands mathematical questions, checks a knowledge base for existing solutions, performs web searches when needed, and generates step-by-step solutions.

## Features

- **AI Gateway with Guardrails**: Input and output validation to ensure appropriate mathematical content
- **Knowledge Base**: Vector database storage of mathematical problems and solutions
- **Web Search Integration**: Fallback to web search when knowledge base doesn't have an answer
- **Human-in-the-Loop Feedback**: Mechanism to collect user feedback and improve solutions
- **DSPy Integration**: Self-learning capabilities through feedback

## Setup

### Prerequisites

- Python 3.9+
- API keys for Google Gemini and Tavily (for web search)

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file:
   ```
   GOOGLE_API_KEY="your-google-api-key"
   TAVILY_API_KEY="your-tavily-api-key"
   ```

### Running the Server

```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

### Math Queries

- `POST /math/solve`: Solve a mathematical problem
  - Request body: `{"query": "Solve the quadratic equation: x^2 - 5x + 6 = 0"}`
  - Response: Step-by-step solution with source information

### Feedback

- `POST /feedback/submit`: Submit feedback on a solution
  - Request body includes the original query, solution, user feedback, and rating
  - Response includes an improved solution based on feedback

- `GET /feedback/stats`: Get statistics about feedback and system improvements

## Architecture

### Components

1. **Guardrails**: Input and output validation in `middleware/guardrails.py`
2. **Knowledge Base**: Vector storage in `services/knowledge_base.py`
3. **Web Search**: External search in `services/web_search.py`
4. **Math Solver**: Solution generation in `services/math_solver.py`
5. **Feedback System**: Human-in-the-loop in `services/feedback_service.py`

### Workflow

1. User submits a mathematical question
2. Input guardrails validate the question
3. System checks the knowledge base for similar questions
4. If not found, system performs a web search
5. If still not found, system generates a solution using LLM
6. Output guardrails validate the solution
7. User can provide feedback to improve future solutions

## Sample Questions

### From Knowledge Base

1. "Solve the quadratic equation: x^2 - 5x + 6 = 0"
2. "Find the derivative of f(x) = x^3 - 4x^2 + 7x - 9"
3. "Find the area of a circle with radius 5 cm"

### For Web Search

1. "What is the formula for the volume of a cone?"
2. "How do you solve a system of linear equations using matrices?"
3. "Explain the binomial theorem with an example"