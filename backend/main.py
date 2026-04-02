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
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered knowledge assistant for enterprise documents"
)

# ✅ UPDATED CORS (important for ngrok + Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # allow all origins
    allow_credentials=True,
    allow_methods=["*"],           # allow all HTTP methods
    allow_headers=["*"],           # allow all headers
)

# Register all routes under /api prefix
# So /query becomes /api/query
# So /health becomes /api/health
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "Visit /docs for API documentation",
        "health": "Visit /api/health to check status"
    }