from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import json
from fastapi import APIRouter, HTTPException

from models.schemas import (
    QueryRequest,
    QueryResponse,
    SourceDocument,
    StatsResponse
)

from retrieval.rag_engine import RAGEngine, build_rag_system_prompt
from retrieval.retriever import ROLE_ACCESS_MAP
from core.config import settings

import chromadb
from chromadb.utils import embedding_functions


router = APIRouter()

print("🚀 Initializing RAG Engine...")
rag_engine = RAGEngine()
print("✅ RAG Engine initialized and ready!")


# ── HEALTH ───────────────────────────────────────────────
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Enterprise AI Knowledge Assistant is running"
    }


# ── DOWNLOAD ─────────────────────────────────────────────
@router.get("/download/{department}/{filename}")
async def download_document(department: str, filename: str):

    if ".." in filename or "/" in filename:
        raise HTTPException(400, "Invalid filename")

    file_path = Path(settings.documents_path) / department / filename

    if not file_path.exists():
        raise HTTPException(404, f"Document not found: {filename}")

    if not filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )


# ── STATS ────────────────────────────────────────────────
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    try:
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        client = chromadb.PersistentClient(path=settings.chroma_db_path)

        collection = client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn
        )

        return StatsResponse(
            total_chunks=collection.count(),
            collection_name=settings.collection_name,
            db_path=settings.chroma_db_path,
            departments=settings.departments
        )

    except Exception as e:
        raise HTTPException(500, f"Error getting stats: {str(e)}")


# ── ROLES ────────────────────────────────────────────────
@router.get("/roles")
async def get_roles():
    roles = []
    for role, departments in ROLE_ACCESS_MAP.items():
        roles.append({
            "role": role,
            "can_access": departments,
            "description": f"Can access: {', '.join(departments)}"
        })
    return {"roles": roles}


# ── QUERY ────────────────────────────────────────────────
@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    if request.role not in ROLE_ACCESS_MAP and request.role not in settings.departments:
        raise HTTPException(400, f"Unknown role: {request.role}")

    try:
        result = rag_engine.answer(
            question=request.question,
            role=request.role,
            n_chunks=request.n_results,
            conversation_history=request.conversation_history
        )

        sources = [
            SourceDocument(
                filename=s["filename"],
                department=s["department"],
                score=s["score"]
            )
            for s in result["sources"]
        ]

        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            role=result["role"],
            chunks_used=result["chunks_used"],
            question=result["question"]
        )

    except Exception as e:
        raise HTTPException(500, f"Error generating answer: {str(e)}")


# ── STREAM ───────────────────────────────────────────────
@router.post("/stream")
async def stream_answer(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    if request.role not in ROLE_ACCESS_MAP and request.role not in settings.departments:
        raise HTTPException(400, f"Unknown role: {request.role}")

    def generate():
        try:
            # ── INTENT CLASSIFICATION ─────────────
            intent = rag_engine._classify_intent(
                request.question,
                request.role,
                request.conversation_history
            )

            print(f"🎯 Stream intent: {intent}")

            # ── HANDLE SIMPLE INTENTS ─────────────
            if intent in ("GREETING", "SYSTEM", "OUT_OF_SCOPE"):

                if intent == "GREETING":
                    result = rag_engine._handle_greeting(
                        request.role, request.question
                    )
                elif intent == "SYSTEM":
                    result = rag_engine._handle_system(
                        request.role, request.question
                    )
                else:
                    result = rag_engine._handle_out_of_scope(
                        request.role, request.question
                    )

                for word in result["answer"].split(" "):
                    yield f"data: {json.dumps({'token': word + ' ', 'done': False})}\n\n"

                yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
                return

            # ── DOCUMENT FLOW ─────────────
            chunks = rag_engine.retriever.search_by_role(
                query=request.question,
                role=request.role,
                n_results=request.n_results
            )

            if not chunks:
                accessible = ROLE_ACCESS_MAP.get(request.role, [request.role])
                msg = (
                    f"I could not find any relevant information "
                    f"in your accessible documents "
                    f"({', '.join(accessible)}). "
                    f"Try rephrasing your question."
                )

                yield f"data: {json.dumps({'token': msg, 'done': False})}\n\n"
                yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
                return

            # ── CONTEXT ─────────────
            top_score = chunks[0]["score"]
            low_confidence = top_score < 0.25

            context = "\n\n".join([
                f"[Source {i}: {c['filename']} | {c['department']} | Relevance: {round(c['score']*100)}%]\n{c['content']}"
                for i, c in enumerate(chunks, 1)
            ])

            # ── BUILD PROMPT (FIXED) ─────────────
            messages = [{
                "role": "system",
                "content": build_rag_system_prompt(request.role)
            }]

            for msg in request.conversation_history[-10:]:
                messages.append({
                    "role": msg.role if hasattr(msg, 'role') else msg["role"],
                    "content": msg.content if hasattr(msg, 'content') else msg["content"]
                })

            confidence_note = ""
            if low_confidence:
                confidence_note = "\n\nNote: Low relevance documents retrieved. Be honest."

            messages.append({
                "role": "user",
                "content": (
                    f"Here are relevant excerpts:\n\n{context}\n\n---\n\n"
                    f"Answer:\n{request.question}\n\n"
                    f"Cite sources.{confidence_note}"
                )
            })

            # ── STREAM FROM LLM ─────────────
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

            # ── SOURCES ─────────────
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
            print(f"❌ Stream error: {e}")
            yield f"data: {json.dumps({'token': 'Something went wrong.', 'done': False})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )