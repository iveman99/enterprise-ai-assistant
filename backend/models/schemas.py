# backend/models/schemas.py

from pydantic import BaseModel


class ConversationMessage(BaseModel):
    """
    A single message in the conversation history.

    role    → "user" or "assistant"
    content → the actual message text
    """
    role:    str
    content: str


class QueryRequest(BaseModel):
    """
    What the frontend sends when asking a question.

    Now includes conversation_history so the AI
    remembers previous messages in the same session.

    Example JSON:
    {
        "question": "How many days do I get?",
        "role": "HR",
        "n_results": 5,
        "conversation_history": [
            {"role": "user", "content": "What is the leave policy?"},
            {"role": "assistant", "content": "The leave policy covers..."}
        ]
    }
    """
    question:             str
    role:                 str
    n_results:            int = 5
    conversation_history: list[ConversationMessage] = []


class SourceDocument(BaseModel):
    """A single source document cited in an answer."""
    filename:   str
    department: str
    score:      float


class QueryResponse(BaseModel):
    """What the API sends back after answering a question."""
    answer:      str
    sources:     list[SourceDocument]
    role:        str
    chunks_used: int
    question:    str


class StatsResponse(BaseModel):
    """Response for the /stats endpoint."""
    total_chunks:    int
    collection_name: str
    db_path:         str
    departments:     list[str]