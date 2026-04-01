# backend/retrieval/rag_engine.py
# ─────────────────────────────────────────────────────────
# RAG Engine with conversation history support.
#
# Now accepts the full conversation history and passes
# it to Groq so the AI understands context from
# previous messages in the same session.
# ─────────────────────────────────────────────────────────

from groq import Groq
from retrieval.retriever import DocumentRetriever
from core.config import settings


SYSTEM_PROMPT = """You are an Enterprise AI Knowledge Assistant.
Your job is to answer employee questions using ONLY the company
documents provided to you as context.

Rules you must follow:
1. Only use information from the provided context
2. Always mention which document your answer comes from
3. If the answer is not in the context say clearly:
   "I could not find this information in your accessible documents."
4. Be professional, clear and concise
5. Never make up information or use outside knowledge
6. You have access to the conversation history —
   use it to understand follow-up questions
7. Format your answer in clean readable paragraphs"""


class RAGEngine:
    """
    RAG Engine with conversation history support.

    Passes the full conversation history to Groq
    so follow-up questions are understood correctly.
    """

    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key)
        self.retriever   = DocumentRetriever()
        self.model       = "llama-3.1-8b-instant"

        print("✅ RAG Engine ready")
        print(f"   LLM      : {self.model} via Groq")
        print(f"   Retriever: ChromaDB + sentence-transformers")


    def answer(
        self,
        question:             str,
        role:                 str,
        n_chunks:             int  = 5,
        conversation_history: list = []
    ) -> dict:
        """
        Answers a question using retrieved context +
        full conversation history for follow-up support.

        Parameters:
            question             → current user question
            role                 → user's department role
            n_chunks             → chunks to retrieve
            conversation_history → list of previous messages
                                   [{"role": "user", "content": "..."},
                                    {"role": "assistant", "content": "..."}]
        """

        print(f"\n{'='*55}")
        print(f"❓ Question : {question}")
        print(f"👤 Role     : {role}")
        print(f"💬 History  : {len(conversation_history)} messages")
        print(f"{'='*55}")

        # ── STEP 1: Retrieve relevant chunks ─────────────
        # We search using the current question
        # History gives context but retrieval uses
        # the current question for best results
        chunks = self.retriever.search_by_role(
            query=question,
            role=role,
            n_results=n_chunks
        )

        if not chunks:
            return {
                "answer":      "I could not find any relevant "
                               "information in your accessible documents.",
                "sources":     [],
                "role":        role,
                "chunks_used": 0,
                "question":    question
            }

        # ── STEP 2: Build context from chunks ────────────
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['filename']} "
                f"| Department: {chunk['department']}]\n"
                f"{chunk['content']}"
            )
        context = "\n\n".join(context_parts)

        # ── STEP 3: Build messages for Groq ──────────────
        # This is the key part — we build the full message list:
        # [system prompt, ...history..., context + current question]
        #
        # Groq reads all messages in order — so it sees the full
        # conversation before answering the current question

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        # Add conversation history (previous messages)
        # Limit to last 10 messages to avoid token limits
        recent_history = conversation_history[-10:]
        for msg in recent_history:
            messages.append({
                "role":    msg.role if hasattr(msg, 'role') else msg["role"],
                "content": msg.content if hasattr(msg, 'content') else msg["content"]
            })

        # Add current question with retrieved context
        current_message = f"""Here are relevant excerpts from company documents:

{context}

---

Based ONLY on the above documents, please answer this question:
{question}

Remember to mention which document(s) your answer comes from.
Use the conversation history above to understand any follow-up context."""

        messages.append({
            "role":    "user",
            "content": current_message
        })

        # ── STEP 4: Send to Groq ──────────────────────────
        print(f"\n🤖 Sending to Groq with {len(messages)} messages...")

        response = self.groq_client.chat.completions.create(
            model=      self.model,
            messages=   messages,
            temperature=0.1,
            max_tokens= 1024
        )

        answer_text = response.choices[0].message.content

        # ── STEP 5: Build citations ───────────────────────
        seen    = set()
        sources = []
        for chunk in chunks:
            key = f"{chunk['department']}::{chunk['filename']}"
            if key not in seen:
                seen.add(key)
                sources.append({
                    "filename":   chunk["filename"],
                    "department": chunk["department"],
                    "score":      chunk["score"]
                })

        print(f"\n✅ Answer generated")
        print(f"   Sources: {[s['filename'] for s in sources]}")

        return {
            "answer":      answer_text,
            "sources":     sources,
            "role":        role,
            "chunks_used": len(chunks),
            "question":    question
        }