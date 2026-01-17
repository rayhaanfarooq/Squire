"""
Squire Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pathlib import Path
from app.api import agents, analysis

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Squire API",
    description="Backend API for Squire hackathon project",
    version="0.1.0"
)

# Include routers
app.include_router(agents.router)
app.include_router(analysis.router)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure SQLite database directory exists
# Path: backend/data/squire.db (relative to backend directory)
DB_PATH = Path(__file__).parent.parent / "data" / "squire.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialize database connection and create tables
from app.db.database import init_db
init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "squire-backend",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Squire API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    # Port 8002 to avoid conflict with SAM webui gateway on 8000
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)

