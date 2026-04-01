# backend/api/routes.py
# ─────────────────────────────────────────────────────────
# This file defines all the API endpoints.
#
# Each function here is one URL the frontend can call.
# FastAPI handles all the HTTP details automatically —
# we just write normal Python functions.
#
# Endpoints:
#   GET  /health       → is the server alive?
#   GET  /stats        → how many docs are loaded?
#   GET  /departments  → what departments exist?
#   GET  /roles        → what roles exist?
#   POST /query        → ask a question, get an answer
# ─────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException
from models.schemas import (
    QueryRequest,
    QueryResponse,
    SourceDocument,
    StatsResponse
)
from retrieval.rag_engine import RAGEngine
from retrieval.retriever import ROLE_ACCESS_MAP
from core.config import settings
import chromadb
from chromadb.utils import embedding_functions


# Create a router — this gets registered in main.py
router = APIRouter()

# Create one RAG engine instance shared across all requests
# We do this once at startup — not on every request
# Loading the embedding model takes ~2 seconds
# so we don't want to reload it for every question
print("🚀 Initializing RAG Engine...")
rag_engine = RAGEngine()
print("✅ RAG Engine initialized and ready!")


# ── GET /health ───────────────────────────────────────────
@router.get("/health")
async def health_check():
    """
    Simple health check — confirms API is alive.
    Used by deployment platforms to monitor the service.
    """
    return {
        "status":  "healthy",
        "message": "Enterprise AI Knowledge Assistant is running"
    }


# ── GET /stats ────────────────────────────────────────────
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Returns statistics about what's loaded in the system.
    Useful for the frontend to show system status.
    """
    try:
        # Connect to ChromaDB to get current count
        embedding_fn = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        client = chromadb.PersistentClient(
            path=settings.chroma_db_path
        )
        collection = client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn
        )

        return StatsResponse(
            total_chunks=    collection.count(),
            collection_name= settings.collection_name,
            db_path=         settings.chroma_db_path,
            departments=     settings.departments
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


# ── GET /departments ──────────────────────────────────────
@router.get("/departments")
async def get_departments():
    """
    Returns list of all departments in the system.
    Frontend uses this to populate dropdown menus.
    """
    return {
        "departments": settings.departments
    }


# ── GET /roles ────────────────────────────────────────────
@router.get("/roles")
async def get_roles():
    """
    Returns all available roles and what they can access.
    Frontend uses this for the role selector in the demo.
    """
    roles = []
    for role, departments in ROLE_ACCESS_MAP.items():
        roles.append({
            "role":        role,
            "can_access":  departments,
            "description": f"Can access: {', '.join(departments)}"
        })

    return {"roles": roles}


# ── POST /query ───────────────────────────────────────────
@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Main endpoint — now supports conversation history
    for follow-up questions.
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if request.role not in ROLE_ACCESS_MAP and \
       request.role not in settings.departments:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown role: {request.role}"
        )

    try:
        result = rag_engine.answer(
            question=             request.question,
            role=                 request.role,
            n_chunks=             request.n_results,
            conversation_history= request.conversation_history
        )

        sources = [
            SourceDocument(
                filename=   s["filename"],
                department= s["department"],
                score=      s["score"]
            )
            for s in result["sources"]
        ]

        return QueryResponse(
            answer=      result["answer"],
            sources=     sources,
            role=        result["role"],
            chunks_used= result["chunks_used"],
            question=    result["question"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )
    # Validate the question is not empty
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # Validate the role exists
    if request.role not in ROLE_ACCESS_MAP and \
       request.role not in settings.departments:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown role: {request.role}. "
                   f"Valid roles: {list(ROLE_ACCESS_MAP.keys())}"
        )

    try:
        # Get answer from RAG engine
        result = rag_engine.answer(
            question=request.question,
            role=request.role,
            n_chunks=request.n_results
        )

        # Convert sources to Pydantic models
        sources = [
            SourceDocument(
                filename=   s["filename"],
                department= s["department"],
                score=      s["score"]
            )
            for s in result["sources"]
        ]

        return QueryResponse(
            answer=      result["answer"],
            sources=     sources,
            role=        result["role"],
            chunks_used= result["chunks_used"],
            question=    result["question"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )