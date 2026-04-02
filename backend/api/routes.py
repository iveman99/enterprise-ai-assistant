# backend/api/routes.py
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.responses import StreamingResponse
import json
from fastapi import APIRouter, HTTPException
from models.schemas import (
    QueryRequest,
    QueryResponse,
    SourceDocument,
    StatsResponse
)
from retrieval.rag_engine import RAGEngine, SYSTEM_PROMPT
from retrieval.retriever import ROLE_ACCESS_MAP
from core.config import settings
import chromadb
from chromadb.utils import embedding_functions

router = APIRouter()

print("🚀 Initializing RAG Engine...")
rag_engine = RAGEngine()
print("✅ RAG Engine initialized and ready!")


# ── GET /health ───────────────────────────────────────────
@router.get("/health")
async def health_check():
    return {
        "status":  "healthy",
        "message": "Enterprise AI Knowledge Assistant is running"
    }


# ── GET /download/{department}/{filename} ─────────────────
@router.get("/download/{department}/{filename}")
async def download_document(department: str, filename: str):
    """
    Serves a PDF file for download.
    Validates department and filename before serving.
    """

    # Prevent path traversal (important for interviews 🔥)
    if ".." in filename or "/" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Build file path
    file_path = Path(settings.documents_path) / department / filename

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {filename}"
        )

    # Only allow PDFs
    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be downloaded"
        )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )


# ── GET /stats ────────────────────────────────────────────
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    try:
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
    return {
        "departments": settings.departments
    }


# ── GET /roles ────────────────────────────────────────────
@router.get("/roles")
async def get_roles():
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


# ── POST /stream ──────────────────────────────────────────
@router.post("/stream")
async def stream_answer(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if request.role not in ROLE_ACCESS_MAP and \
       request.role not in settings.departments:
        raise HTTPException(status_code=400, detail=f"Unknown role: {request.role}")

    def generate():
        try:
            chunks = rag_engine.retriever.search_by_role(
                query=request.question,
                role=request.role,
                n_results=request.n_results
            )

            if not chunks:
                yield f"data: {json.dumps({'token': 'No relevant info found.', 'done': False})}\n\n"
                yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
                return

            context = "\n\n".join([
                f"[Source {i}: {c['filename']} | {c['department']}]\n{c['content']}"
                for i, c in enumerate(chunks, 1)
            ])

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            for msg in request.conversation_history[-10:]:
                messages.append({
                    "role": msg.role if hasattr(msg, 'role') else msg["role"],
                    "content": msg.content if hasattr(msg, 'content') else msg["content"]
                })

            messages.append({
                "role": "user",
                "content": f"{context}\n\nQuestion: {request.question}"
            })

            stream = rag_engine.groq_client.chat.completions.create(
                model=rag_engine.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                stream=True
            )

            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

            seen = set()
            sources = []
            for c in chunks:
                key = f"{c['department']}::{c['filename']}"
                if key not in seen:
                    seen.add(key)
                    sources.append({
                        "filename": c["filename"],
                        "department": c["department"],
                        "score": c["score"]
                    })

            yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True, 'sources': []})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )