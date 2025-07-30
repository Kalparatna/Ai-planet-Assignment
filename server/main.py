from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
import json
import uvicorn
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Math Routing Agent",
    description="An Agentic-RAG system that replicates a mathematical professor",
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

# Initialize performance monitoring
from services.performance_monitor import PerformanceMonitor
performance_monitor = PerformanceMonitor()

# Add performance monitoring middleware
@app.middleware("http")
async def performance_monitoring_middleware(request: Request, call_next):
    # Generate a unique request ID
    import uuid
    request_id = str(uuid.uuid4())
    
    # Get endpoint path
    endpoint = request.url.path
    
    try:
        # Start timing the request
        performance_monitor.start_request(request_id, endpoint)
        
        # Process the request
        response = await call_next(request)
        
        # End timing and log performance metrics
        performance_monitor.end_request(request_id)
        
        return response
    except Exception as e:
        logger.error(f"Error in middleware: {e}")
        # Still end the performance monitoring in case of error
        if request_id in performance_monitor.current_requests:
            performance_monitor.end_request(request_id, success=False)
        raise

# Import modules after app initialization
from routes import math_router
from routes import pdf_router
from middleware.guardrails import input_guardrail, output_guardrail
from routes.feedback_router import feedback_router

# Register routers
app.include_router(math_router.router)
app.include_router(pdf_router.router)
app.include_router(feedback_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Math Routing Agent API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)