# backend/retrieval/rag_engine.py
# ─────────────────────────────────────────────────────────
# This is the brain of the system.
#
# It connects retrieval (Step 3) with Groq LLM to produce
# grounded answers — answers based on actual company docs,
# not the AI's general knowledge.
#
# Flow:
#   question + role
#       → retrieve relevant chunks (DocumentRetriever)
#       → build a prompt with those chunks as context
#       → send to Groq
#       → return answer + source citations
# ─────────────────────────────────────────────────────────

from groq import Groq
from retrieval.retriever import DocumentRetriever
from core.config import settings


# ── System prompt ────────────────────────────────────────
# This tells Groq exactly how to behave.
# It is sent with every single request.
SYSTEM_PROMPT = """You are an Enterprise AI Knowledge Assistant.
Your job is to answer employee questions using ONLY the company 
documents provided to you as context.

Rules you must follow:
1. Only use information from the provided context
2. Always mention which document your answer comes from
3. If the answer is not in the context, say clearly:
   "I could not find this information in your accessible documents."
4. Be professional, clear and concise
5. Never make up information or use outside knowledge
6. Format your answer in clean readable paragraphs"""


class RAGEngine:
    """
    Retrieval Augmented Generation engine.

    Takes a question + role, retrieves relevant chunks,
    builds a prompt, sends to Groq, returns the answer
    with source citations.
    """

    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=settings.groq_api_key
        )

        # Initialize retriever (connects to ChromaDB)
        self.retriever = DocumentRetriever()

        # Groq model — llama3 is fast, free, and excellent
        self.model = "llama-3.1-8b-instant"

        print("✅ RAG Engine ready")
        print(f"   LLM     : {self.model} via Groq")
        print(f"   Retriever: ChromaDB + sentence-transformers")


    def answer(
        self,
        question: str,
        role: str,
        n_chunks: int = 5
    ) -> dict:
        """
        Main method — takes a question and returns an answer.

        Parameters:
            question → user's question in plain English
            role     → user's department role (e.g. "HR", "Finance")
            n_chunks → how many document chunks to use as context

        Returns a dict with:
            answer      → the AI generated answer
            sources     → list of documents used
            role        → the role used for filtering
            chunks_used → number of chunks retrieved
            question    → the original question
        """

        print(f"\n{'='*55}")
        print(f"❓ Question : {question}")
        print(f"👤 Role     : {role}")
        print(f"{'='*55}")

        # ── STEP 1: Retrieve relevant chunks ─────────────
        chunks = self.retriever.search_by_role(
            query=question,
            role=role,
            n_results=n_chunks
        )

        # If no chunks found — return gracefully
        if not chunks:
            return {
                "answer":      "I could not find any relevant information "
                               "in your accessible documents.",
                "sources":     [],
                "role":        role,
                "chunks_used": 0,
                "question":    question
            }

        # ── STEP 2: Build context from chunks ────────────
        # We combine all retrieved chunks into one context block
        # Each chunk is labeled with its source document
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['filename']} "
                f"| Department: {chunk['department']}]\n"
                f"{chunk['content']}"
            )

        context = "\n\n".join(context_parts)

        # ── STEP 3: Build the full prompt ─────────────────
        # We give Groq the context + the question
        # It must answer using ONLY the context
        user_prompt = f"""Here are relevant excerpts from company documents:

{context}

---

Based ONLY on the above documents, please answer this question:
{question}

Remember to mention which document(s) your answer comes from."""

        # ── STEP 4: Send to Groq ──────────────────────────
        print(f"\n🤖 Sending to Groq ({self.model})...")

        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.1,  # low = more factual, less creative
            max_tokens=1024
        )

        answer_text = response.choices[0].message.content

        # ── STEP 5: Build source citations ────────────────
        # Deduplicate sources — same file might appear multiple times
        seen = set()
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

        # ── STEP 6: Return everything ─────────────────────
        print(f"\n✅ Answer generated")
        print(f"   Sources used: {[s['filename'] for s in sources]}")

        return {
            "answer":      answer_text,
            "sources":     sources,
            "role":        role,
            "chunks_used": len(chunks),
            "question":    question
        }