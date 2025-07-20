# Math Routing Agent: Agentic-RAG System Proposal

## Introduction

This proposal outlines the design and implementation of an Agentic-RAG architecture system that replicates a mathematical professor. The system is designed to understand mathematical questions, generate step-by-step solutions, and simplify complex concepts for students. The system incorporates several key components including an AI Gateway with guardrails, a knowledge base for retrieving existing solutions, web search capabilities using Model Context Protocol (MCP), and a human-in-the-loop feedback mechanism for continuous improvement.

## System Architecture

### Overview

The Math Routing Agent is built using a modular architecture with the following components:

1. **FastAPI Backend**: Handles API requests, routes queries, and manages the overall workflow
2. **React Frontend**: Provides a user-friendly interface for submitting queries and receiving solutions
3. **AI Gateway with Guardrails**: Ensures appropriate content and educational focus
4. **Knowledge Base**: Stores and retrieves mathematical problems and solutions
5. **Web Search Integration**: Fetches information for queries not found in the knowledge base
6. **Human-in-the-Loop Feedback**: Collects user feedback and improves solutions

### Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React Frontend │────▶│  FastAPI Server │────▶│   AI Gateway   │
│                 │     │                 │     │   (Guardrails)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Feedback Loop  │◀────│  Math Solver    │◀────│  Query Router   │
│  (DSPy-powered) │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │                 │
                                               │ Knowledge Base  │
                                               │    (Chroma)     │
                                               └────────┬────────┘
                                                        │
                                                        │
                                               ┌────────▼────────┐
                                               │                 │
                                               │   Web Search    │
                                               │   (MCP/Tavily)  │
                                               └─────────────────┘
```

## Input & Output Guardrails

### Approach

The system implements both input and output guardrails to ensure educational integrity and content appropriateness:

#### Input Guardrails

- **Topic Filtering**: Ensures queries are related to mathematics by checking against a list of mathematical topics and patterns
- **Content Moderation**: Filters out inappropriate content, non-educational queries, and potential harmful prompts
- **Query Sanitization**: Removes potentially harmful elements while preserving the mathematical intent

#### Output Guardrails

- **Content Verification**: Ensures solutions contain only mathematical content and educational explanations
- **Educational Value Check**: Verifies that solutions provide step-by-step explanations rather than just answers
- **Disclaimer Addition**: Adds appropriate disclaimers for complex topics or when solutions might be incomplete

### Implementation

The guardrails are implemented in the `guardrails.py` module using a combination of pattern matching, keyword filtering, and contextual analysis. This approach was chosen because it provides a balance between performance and accuracy, allowing for real-time filtering without significant latency.

## Knowledge Base

### Dataset Details

The knowledge base is built using a collection of common mathematical problems and solutions across various domains including algebra, calculus, geometry, and statistics. The data is stored in a Chroma vector database using HuggingFace embeddings for efficient semantic retrieval.

### Sample Questions

1. **Algebra**: "Solve the quadratic equation x² + 5x + 6 = 0 using the quadratic formula."
   - The system will retrieve the step-by-step solution showing the application of the quadratic formula, resulting in x = -2 and x = -3.

2. **Calculus**: "Find the derivative of f(x) = x³ + 2x² - 4x + 7 using the power rule."
   - The system will provide a detailed solution showing the application of the power rule for each term, resulting in f'(x) = 3x² + 4x - 4.

3. **Geometry**: "Calculate the area of a circle with radius 5 cm."
   - The system will explain the formula for the area of a circle (A = πr²) and show the calculation: A = π × 5² = 25π ≈ 78.54 cm².

## Web Search Capabilities & MCP Setup

### Strategy

When a query is not found in the knowledge base, the system uses a multi-stage web search approach:

1. **Primary Search**: Uses the Tavily API to perform a targeted search for mathematical content
2. **Specialized Site Scraping**: Targets educational mathematics websites like Mathway, WolframAlpha, and Symbolab
3. **MCP Integration**: Uses the Model Context Protocol to enhance the context provided to the LLM

### MCP Implementation

The system leverages MCP to provide rich context to the LLM when generating solutions. This is implemented using the `mcp.config.usrlocalmcp.Fetch` server, which allows the system to fetch and process web content in real-time, providing the LLM with the most relevant information for generating accurate solutions.

### Sample Questions (Not in Knowledge Base)

1. **Number Theory**: "Explain the Sieve of Eratosthenes algorithm for finding prime numbers."
   - The system will search the web, find educational resources explaining the algorithm, and generate a step-by-step explanation with a visual representation if available.

2. **Linear Algebra**: "How do you find the eigenvalues and eigenvectors of a 3x3 matrix?"
   - The system will search for detailed explanations, compile the information, and generate a comprehensive solution with examples.

3. **Probability**: "Explain the concept of conditional probability with the Monty Hall problem."
   - The system will search for explanations of the Monty Hall problem, gather different perspectives, and provide a clear explanation with probability calculations.

## Human-in-the-Loop Feedback Routing

### Feedback Mechanism

The system implements a comprehensive feedback mechanism that allows users to rate solutions and provide specific comments. This feedback is used to improve future solutions through a DSPy-powered learning system.

### DSPy Integration

The feedback system uses DSPy to create a self-improving loop:

1. **Feedback Collection**: Users provide ratings (1-5 stars) and optional text feedback
2. **Solution Improvement**: DSPy modules (`MathSolutionSignature` and `MathSolutionModule`) process the feedback to generate improved solutions
3. **Knowledge Base Update**: Improved solutions are added to the knowledge base for future retrieval
4. **Continuous Learning**: The system learns from patterns in user feedback to improve its solution generation capabilities

### Workflow

```
User Feedback → DSPy Processing → Improved Solution → Knowledge Base Update → Enhanced Future Responses
```

This approach was chosen because it combines the strengths of LLMs with human expertise, allowing the system to continuously improve based on real user interactions rather than relying solely on pre-trained knowledge.

## Implementation Details

### Backend (FastAPI)

The backend is implemented using FastAPI with the following components:

- **Routers**: `math_router.py` and `feedback_router.py` handle the main API endpoints
- **Services**: `knowledge_base.py`, `web_search.py`, `math_solver.py`, and `feedback_service.py` implement the core functionality
- **Middleware**: `guardrails.py` implements the input and output guardrails

### Frontend (React)

The frontend is implemented using React with the following features:

- **Query Interface**: A clean, user-friendly interface for submitting mathematical questions
- **Solution Display**: Formatted display of step-by-step solutions with source information
- **Feedback System**: Interface for rating solutions and providing detailed feedback
- **Query History**: Tracking of previous queries for easy reference

## Conclusion

The Math Routing Agent represents a comprehensive approach to creating an AI-powered mathematical assistant that combines the strengths of knowledge retrieval, web search, and human feedback. By implementing guardrails, a robust knowledge base, efficient web search capabilities, and a human-in-the-loop feedback mechanism, the system provides accurate, educational, and continuously improving mathematical solutions to students.

---

## Appendix: Technical Implementation

### Dependencies

- **Backend**: FastAPI, Uvicorn, LangChain, Chroma, DSPy, Google Generative AI, Tavily
- **Frontend**: React, Vite, Axios
- **Vector Database**: Chroma with HuggingFace Embeddings
- **LLM**: Google Gemini 2.0 Flash

### API Endpoints

- **POST /math/solve**: Submit a mathematical question for solving
- **POST /feedback/submit**: Submit feedback for a solution
- **GET /feedback/stats**: Get statistics about collected feedback

### Future Enhancements

- Integration with additional mathematical tools and libraries
- Support for mathematical notation rendering (LaTeX)
- Expanded knowledge base with more specialized topics
- Enhanced visualization capabilities for geometric problems