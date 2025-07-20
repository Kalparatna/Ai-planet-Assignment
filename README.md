# Math Routing Agent: Agentic-RAG System

This project implements an Agentic-RAG architecture system that acts as a mathematical professor, generating step-by-step solutions to mathematical questions. The system incorporates an AI Gateway with guardrails, a knowledge base for retrieving existing solutions, web search capabilities with Model Context Protocol (MCP), and a human-in-the-loop feedback mechanism for continuous improvement.

## Project Structure

```
├── client/                 # React frontend
│   ├── public/             # Public assets
│   ├── src/                # Source code
│   ├── package.json        # Dependencies
│   └── run.bat             # Script to run the client
├── server/                 # FastAPI backend
│   ├── data/               # Data storage
│   ├── middleware/         # Middleware components
│   │   ├── guardrails.py   # Input/output guardrails
│   │   └── feedback.py     # Feedback processing
│   ├── routes/             # API routes
│   │   ├── math_router.py  # Math query endpoints
│   │   └── feedback_router.py # Feedback endpoints
│   ├── services/           # Core services
│   │   ├── knowledge_base.py # Vector database
│   │   ├── web_search.py   # Web Search Capabilities (via Tavily)
│   │   ├── math_solver.py  # Solution generation
│   │   └── feedback_service.py # Feedback processing
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Dependencies
│   └── run.bat             # Script to run the server
└── Math_Routing_Agent_Proposal.md # Detailed project proposal
```

## Features

- **AI Gateway with Guardrails**: Ensures appropriate content and educational focus
- **Knowledge Base**: Stores and retrieves mathematical problems and solutions using vector embeddings
- **Web Search Integration**: Fetches information for queries not found in the knowledge base
- **Human-in-the-Loop Feedback**: Collects user feedback and improves solutions using DSPy
- **Model Context Protocol (MCP)**: Enhances context for the LLM when generating solutions

## Setup Instructions

### Prerequisites

- Python 3.9+ for the backend
- Node.js 16+ for the frontend
- Google API Key (for Gemini 2.0 Flash)
- Tavily API Key (for web search)

### For Running for frontend and backend
```
.\start_all.bat
```
or 

### Backend Setup

1. Navigate to the server directory:
   ```
   cd server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file with the following:
   ```
   GOOGLE_API_KEY=your_google_api_key
   TAVILY_API_KEY=your_tavily_api_key
   PORT=8000
   ```

4. Run the server:
   ```
   run.bat
   ```
   or
   ```
   python run.py
   ```

### Frontend Setup

1. Navigate to the client directory:
   ```
   cd client
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the client:
   ```
   run.bat
   ```
   or
   ```
   npm run dev
   ```

## Usage

1. Open your browser and navigate to `http://localhost:5173` (or the port shown in your terminal)
2. Enter a mathematical question in the input field
3. View the step-by-step solution
4. Provide feedback on the solution to help improve the system

## Sample Questions

### From Knowledge Base

- "Solve the quadratic equation x² + 5x + 6 = 0 using the quadratic formula."
- "Find the derivative of f(x) = x³ + 2x² - 4x + 7 using the power rule."
- "Calculate the area of a circle with radius 5 cm."

### Web Search Required

- "Explain the Sieve of Eratosthenes algorithm for finding prime numbers."
- "How do you find the eigenvalues and eigenvectors of a 3x3 matrix?"
- "Explain the concept of conditional probability with the Monty Hall problem."

## Architecture

The system follows a modular architecture with the following components:

1. **FastAPI Backend**: Handles API requests, routes queries, and manages the overall workflow
2. **React Frontend**: Provides a user-friendly interface for submitting queries and receiving solutions
3. **AI Gateway with Guardrails**: Ensures appropriate content and educational focus
4. **Knowledge Base**: Stores and retrieves mathematical problems and solutions
5. **Web Search Integration**: Fetches information for queries not found in the knowledge base
6. **Human-in-the-Loop Feedback**: Collects user feedback and improves solutions

## License

This project is for educational purposes only.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [LangChain](https://python.langchain.com/)
- [Chroma](https://www.trychroma.com/)
- [DSPy](https://github.com/stanfordnlp/dspy)
- [Google Generative AI](https://ai.google.dev/)
- [Tavily](https://tavily.com/)