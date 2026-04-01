# backend/models/schemas.py
# ─────────────────────────────────────────────────────────
# These are Pydantic models — they define the exact shape
# of data coming into and going out of our API.
#
# WHY THIS MATTERS:
# - FastAPI automatically validates incoming data
# - If frontend sends wrong data, it gets a clear error
# - Auto-generates API documentation for free
# - Makes the code self-documenting
# ─────────────────────────────────────────────────────────

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """
    What the frontend sends when asking a question.

    Example JSON:
    {
        "question": "What is the leave policy?",
        "role": "HR",
        "n_results": 5
    }
    """
    question:  str        # the user's question
    role:      str        # user's department role
    n_results: int = 5    # how many chunks to retrieve (default 5)


class SourceDocument(BaseModel):
    """
    A single source document cited in an answer.

    Example:
    {
        "filename": "Leave Policy Template.pdf",
        "department": "HR",
        "score": 0.733
    }
    """
    filename:   str
    department: str
    score:      float


class QueryResponse(BaseModel):
    """
    What the API sends back after answering a question.

    Example JSON:
    {
        "answer": "According to the Leave Policy...",
        "sources": [...],
        "role": "HR",
        "chunks_used": 5,
        "question": "What is the leave policy?"
    }
    """
    answer:      str
    sources:     list[SourceDocument]
    role:        str
    chunks_used: int
    question:    str


class StatsResponse(BaseModel):
    """
    Response for the /stats endpoint.
    Shows what's loaded in the system.
    """
    total_chunks:    int
    collection_name: str
    db_path:         str
    departments:     list[str]