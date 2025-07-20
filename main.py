from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from api import chat, profile, memory
from core.vector_store import CustomVectorStore
from core.prompt_engineer import CustomPromptEngineer
from core.conversation_manager import CustomConversationManager

# Create FastAPI app
app = FastAPI(
    title="Personalized Tone Adaptation System",
    description="AI system that adapts communication tone based on user profiles, context, and feedback",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(memory.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Personalized Tone Adaptation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "profiles": "/api/profile",
            "chat": "/api/chat",
            "memory": "/api/memory/{user_id}",
            "feedback": "/api/chat/feedback"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 