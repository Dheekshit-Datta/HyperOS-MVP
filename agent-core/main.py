"""
HyperOS Agent Core - FastAPI Server
Provides REST API for the Electron frontend to communicate with the agent
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from agent import get_agent, HyperOSAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HyperOSServer')


# Pydantic models for request/response validation
class TaskRequest(BaseModel):
    """Request model for task execution"""
    task: str = Field(..., min_length=1, max_length=1000, description="Task description")


class TaskResponse(BaseModel):
    """Response model for task execution"""
    status: str
    message: Optional[str] = None
    history: Optional[list] = None
    steps_completed: Optional[int] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    capabilities: list
    system: dict


class CancelResponse(BaseModel):
    """Response model for cancel request"""
    success: bool
    message: str


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting HyperOS Agent Core...")
    
    # Initialize agent on startup to validate configuration
    try:
        agent = get_agent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise
    
    yield
    
    logger.info("Shutting down HyperOS Agent Core...")


# Create FastAPI app
app = FastAPI(
    title="HyperOS Agent Core",
    description="Vision-enabled desktop AI automation agent",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",       # Alternative dev port
        "http://127.0.0.1:3000",
        "file://",                     # Electron file protocol
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions globally"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


@app.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns server status, version, and capabilities.
    """
    try:
        agent = get_agent()
        system_status = agent.get_system_status()
        
        return HealthResponse(
            status="HyperOS Agent Active",
            version="1.1.0",
            capabilities=[
                "screen_capture",
                "vision_analysis",
                "click_automation",
                "type_automation",
                "keyboard_control",
                "window_detection"
            ],
            system=system_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest) -> TaskResponse:
    """
    Execute a task using the HyperOS agent.
    
    This endpoint accepts a natural language task description and
    runs the Analyze-Plan-Execute loop to complete it.
    
    Note: This is a blocking operation that may take several seconds.
    """
    logger.info(f"Received task: {request.task}")
    
    try:
        agent = get_agent()
        
        # Check if agent is already running
        if agent.is_running:
            raise HTTPException(
                status_code=409,
                detail="Another task is already in progress. Cancel it first or wait."
            )
        
        # Execute the task (blocking)
        result = agent.execute_instruction(request.task)
        
        return TaskResponse(
            status=result.get("status", "error"),
            message=result.get("message"),
            history=result.get("history", []),
            steps_completed=result.get("steps_completed")
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel", response_model=CancelResponse)
async def cancel_task() -> CancelResponse:
    """
    Cancel the currently running task.
    
    If a task is running, this will signal it to stop after the current step.
    """
    try:
        agent = get_agent()
        
        if not agent.is_running:
            return CancelResponse(
                success=False,
                message="No task is currently running"
            )
        
        cancelled = agent.request_cancel()
        
        if cancelled:
            return CancelResponse(
                success=True,
                message="Cancel request sent. Task will stop after current step."
            )
        else:
            return CancelResponse(
                success=False,
                message="Failed to cancel task"
            )
            
    except Exception as e:
        logger.error(f"Cancel request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    Get the current agent status.
    
    Returns information about whether a task is running and system state.
    """
    try:
        agent = get_agent()
        return {
            "is_running": agent.is_running,
            "current_task": agent.current_task,
            "system": agent.get_system_status()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for the server"""
    print("\n" + "="*50)
    print("  HYPEROS AGENT CORE - Starting...")
    print("="*50 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
