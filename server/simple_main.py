from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Math Routing Agent - Simple Version",
    description="A simplified version of the Math Routing Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Math Routing Agent API is running (Simple Version)"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Math endpoint
@app.post("/math/solve")
async def solve_math_problem(query: str):
    return {
        "solution": f"This is a placeholder solution for: {query}",
        "source": "generated",
        "confidence": 0.8,
        "references": []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)