# backend/main.py
# ─────────────────────────────────────────────────────────
# Entry point of the entire backend.
# Creates the FastAPI app and registers all routes.
# ─────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from core.config import settings

# Create the app
app = FastAPI(
    title=       settings.app_name,
    version=     settings.app_version,
    description= "AI-powered knowledge assistant for enterprise documents"
)

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=  ["http://localhost:3000", "*"],
    allow_methods=  ["*"],
    allow_headers=  ["*"],
)

# Register all routes under /api prefix
# So /query becomes /api/query
# So /health becomes /api/health
app.include_router(router, prefix="/api")

# Root
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs":    "Visit /docs for API documentation",
        "health":  "Visit /api/health to check status"
    }