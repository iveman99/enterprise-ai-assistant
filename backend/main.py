# backend/main.py
# ─────────────────────────────────────────────
# This is the entry point of our entire backend.
# Think of it as the front door of the building.
# All API routes will be registered here.
# ─────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# Create the FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered knowledge assistant for enterprise documents"
)

# Allow React frontend to talk to this backend
# (CORS = Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React runs here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check — confirms the server is alive
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

# Root
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} API"}