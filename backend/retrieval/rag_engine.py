# backend/retrieval/rag_engine.py
# ─────────────────────────────────────────────────────────
# Final production-grade RAG Engine with intent classification.
#
# Architecture:
#   Every question → Intent Classifier → Route to handler
#
#   GREETING     → Warm role-aware greeting (no retrieval)
#   SYSTEM       → Hardcoded system facts (no retrieval)
#   DOCUMENT     → Full RAG pipeline with confidence check
#   OUT_OF_SCOPE → Polite role-aware redirect (no retrieval)
#
# This handles every possible question correctly without
# keyword lists — the classifier understands intent from
# meaning, not pattern matching.
# ─────────────────────────────────────────────────────────

import json
from groq import Groq
from retrieval.retriever import DocumentRetriever, ROLE_ACCESS_MAP
from core.config import settings


# ── Hardcoded system facts ────────────────────────────────
# Never let the LLM generate these — it will hallucinate
DEPT_DOC_COUNTS = {
    "HR":         8,
    "Finance":    8,
    "IT":         10,
    "Legal":      7,
    "Operations": 9
}
TOTAL_DOCUMENTS = 42
TOTAL_CHUNKS    = 1193
TOTAL_DEPTS     = 5


# ── Intent classification prompt ──────────────────────────
def build_classifier_prompt(question: str, role: str,
                             conversation_history: list) -> str:
    """
    Builds the prompt for intent classification.
    Returns one of: GREETING, SYSTEM, DOCUMENT, OUT_OF_SCOPE
    """
    history_text = ""
    if conversation_history:
        recent = conversation_history[-4:]
        history_text = "\n".join([
            f"{m['role'] if isinstance(m, dict) else m.role}: "
            f"{m['content'] if isinstance(m, dict) else m.content}"
            for m in recent
        ])

    return f"""You are an intent classifier for an Enterprise AI Knowledge Assistant.

The user is a {role} employee. They have access to company internal documents.

Conversation history (last few messages):
{history_text if history_text else "No previous messages"}

Current question: "{question}"

Classify this question into EXACTLY ONE of these intents:

GREETING — casual greetings, small talk, social questions
  Examples: "hi", "hello", "how are you", "good morning",
  "how r u", "hey there", "what's up", "sup"

SYSTEM — questions about the AI system itself, its capabilities,
  what documents it has, how many files, what departments,
  who built it, what it can do, how it works
  Examples: "how many documents do you have", "who built you",
  "what can you do", "what departments can I access",
  "how many files", "tell me about yourself",
  "what all can you help me with", "how does this work"

DOCUMENT — questions that need information from company documents.
  This includes follow-up questions that refer to previous answers.
  Examples: "what is the leave policy", "how does budget approval work",
  "tell me more about that", "explain this further",
  "what are the IT security rules", "give me details"

OUT_OF_SCOPE — questions completely unrelated to company documents
  or the AI system. Political figures, general knowledge,
  personal advice, news, sports, entertainment, etc.
  Examples: "who is modi", "what is bitcoin", "tell me a joke",
  "what is the weather", "who won the match"

IMPORTANT RULES:
- If the question is a follow-up to a previous document answer
  (like "tell me more", "explain further", "give details"),
  classify as DOCUMENT
- If unsure between DOCUMENT and OUT_OF_SCOPE, choose DOCUMENT
- Respond with ONLY the intent word — nothing else

Intent:"""


# ── Role-aware system prompt for RAG ─────────────────────
def build_rag_system_prompt(role: str) -> str:
    accessible = ROLE_ACCESS_MAP.get(role, [role])
    dept_list  = ", ".join(accessible)

    suggestions = []
    if "HR"         in accessible:
        suggestions.append("HR policies (leave, attendance, dress code, exit)")
    if "Finance"    in accessible:
        suggestions.append("Finance (budget, expenses, investments, risk)")
    if "IT"         in accessible:
        suggestions.append("IT (security, cloud, AI, data science, compliance)")
    if "Legal"      in accessible:
        suggestions.append("Legal (data protection, IP rights, contracts, fraud)")
    if "Operations" in accessible:
        suggestions.append("Operations (office management, performance, ethics)")

    suggestion_text = "\n- ".join(suggestions)

    return f"""You are an Enterprise AI Knowledge Assistant.
The current user is a {role} with access to: {dept_list} documents.

RULES:
1. Answer ONLY using the provided document context
2. Always cite sources: mention the document name
3. Be professional, clear and concise
4. If the context doesn't fully answer the question, say so honestly
5. Never make up information not in the documents
6. Use conversation history to understand follow-up questions
7. Format answers clearly — use bullet points for lists

You can help this user with:
- {suggestion_text}"""


class RAGEngine:
    """
    Production-grade RAG Engine with intent classification.

    Flow:
    1. Classify intent (GREETING/SYSTEM/DOCUMENT/OUT_OF_SCOPE)
    2. Route to appropriate handler
    3. Return grounded, role-aware answer
    """

    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key)
        self.retriever   = DocumentRetriever()
        self.model       = "llama-3.1-8b-instant"

        print("✅ RAG Engine ready")
        print(f"   LLM      : {self.model} via Groq")
        print(f"   Retriever: ChromaDB + sentence-transformers")
        print(f"   Mode     : Intent classification enabled")


    # ── Public method ─────────────────────────────────────
    def answer(
        self,
        question:             str,
        role:                 str,
        n_chunks:             int  = 5,
        conversation_history: list = []
    ) -> dict:
        """
        Main entry point. Classifies intent then routes
        to the appropriate handler.
        """

        print(f"\n{'='*55}")
        print(f"❓ Question : {question}")
        print(f"👤 Role     : {role}")
        print(f"💬 History  : {len(conversation_history)} messages")

        # Step 1 — Classify intent
        intent = self._classify_intent(
            question, role, conversation_history
        )
        print(f"🎯 Intent   : {intent}")
        print(f"{'='*55}")

        # Step 2 — Route to handler
        if intent == "GREETING":
            return self._handle_greeting(role, question)

        elif intent == "SYSTEM":
            return self._handle_system(role, question)

        elif intent == "OUT_OF_SCOPE":
            return self._handle_out_of_scope(role, question)

        else:  # DOCUMENT — default
            return self._handle_document(
                question, role, n_chunks, conversation_history
            )


    # ── Intent Classifier ─────────────────────────────────
    def _classify_intent(
        self,
        question:             str,
        role:                 str,
        conversation_history: list
    ) -> str:
        """
        Uses Groq to classify the intent of the question.
        Returns: GREETING / SYSTEM / DOCUMENT / OUT_OF_SCOPE
        """
        try:
            prompt = build_classifier_prompt(
                question, role, conversation_history
            )

            response = self.groq_client.chat.completions.create(
                model=       self.model,
                messages=    [{"role": "user", "content": prompt}],
                temperature= 0,      # deterministic classification
                max_tokens=  10      # we only need one word back
            )

            intent = response.choices[0].message.content.strip().upper()

            # Validate — only accept known intents
            valid_intents = {
                "GREETING", "SYSTEM", "DOCUMENT", "OUT_OF_SCOPE"
            }
            if intent not in valid_intents:
                # Default to DOCUMENT if unclear
                return "DOCUMENT"

            return intent

        except Exception as e:
            print(f"⚠️  Classifier error: {e} — defaulting to DOCUMENT")
            return "DOCUMENT"


    # ── Handler: GREETING ─────────────────────────────────
    def _handle_greeting(self, role: str, question: str) -> dict:
        """
        Warm, role-aware greeting. No retrieval needed.
        """
        accessible = ROLE_ACCESS_MAP.get(role, [role])
        dept_list  = ", ".join(accessible)

        # Build role-specific suggestions
        examples = []
        if "HR"         in accessible:
            examples.append("leave and attendance policies")
        if "Finance"    in accessible:
            examples.append("budget approval processes")
        if "IT"         in accessible:
            examples.append("IT security guidelines")
        if "Legal"      in accessible:
            examples.append("data protection laws")
        if "Operations" in accessible:
            examples.append("office management procedures")

        example_text = examples[0] if examples else "company policies"

        answer = (
            f"Hello! 👋 I'm your Enterprise AI Knowledge Assistant.\n\n"
            f"As a **{role}**, I can help you instantly find "
            f"information from your **{dept_list}** documents — "
            f"no more searching through PDFs manually.\n\n"
            f"Try asking me something like:\n"
            f"*\"What is the {example_text}?\"*\n\n"
            f"What would you like to know?"
        )

        return {
            "answer":      answer,
            "sources":     [],
            "role":        role,
            "chunks_used": 0,
            "question":    question,
            "intent":      "GREETING"
        }


    # ── Handler: SYSTEM ───────────────────────────────────
    def _handle_system(self, role: str, question: str) -> dict:
        """
        Answers questions about the system itself.
        Uses hardcoded facts — never lets LLM generate stats.
        """
        accessible      = ROLE_ACCESS_MAP.get(role, [role])
        dept_list       = ", ".join(accessible)
        accessible_docs = sum(
            DEPT_DOC_COUNTS.get(d, 0) for d in accessible
        )
        accessible_chunks = round(
            TOTAL_CHUNKS * accessible_docs / TOTAL_DOCUMENTS
        )

        question_lower = question.lower()

        # Identity questions
        identity_words = [
            "who built", "who build", "who made", "who created",
            "who developed", "what is your name", "what are you",
            "who are you", "introduce", "tell me about yourself",
            "about you"
        ]
        is_identity = any(w in question_lower for w in identity_words)

        # Capability questions
        capability_words = [
            "what can you do", "what all can you", "how can you help",
            "what can you help", "what do you do", "how does this work",
            "what are your features", "what all you can"
        ]
        is_capability = any(w in question_lower for w in capability_words)

        if is_identity:
            answer = (
                f"I'm the **Enterprise AI Knowledge Assistant** — "
                f"an intelligent document search system built for "
                f"your organization.\n\n"
                f"**What I do:**\n"
                f"- Search {TOTAL_DOCUMENTS} company documents "
                f"instantly using AI\n"
                f"- Understand questions in plain English\n"
                f"- Provide grounded answers with source citations\n"
                f"- Respect role-based access control\n"
                f"- Remember conversation context\n\n"
                f"**Tech stack:** Python, FastAPI, ChromaDB, "
                f"Groq LLM, React\n\n"
                f"**Your access ({role}):** {dept_list} — "
                f"{accessible_docs} documents, "
                f"~{accessible_chunks} searchable chunks\n\n"
                f"What would you like to know?"
            )

        elif is_capability:
            suggestions = []
            if "HR"         in accessible:
                suggestions.append(
                    "📋 **HR** — leave policies, attendance, "
                    "dress code, exit procedures"
                )
            if "Finance"    in accessible:
                suggestions.append(
                    "💰 **Finance** — budget SOPs, investments, "
                    "risk management, stakeholder reports"
                )
            if "IT"         in accessible:
                suggestions.append(
                    "💻 **IT** — security procedures, cloud management, "
                    "AI policies, compliance"
                )
            if "Legal"      in accessible:
                suggestions.append(
                    "⚖️  **Legal** — data protection, IP rights, "
                    "consumer laws, fraud policies"
                )
            if "Operations" in accessible:
                suggestions.append(
                    "⚙️  **Operations** — office management, "
                    "performance, ethics, communication"
                )

            suggestions_text = "\n".join(suggestions)

            answer = (
                f"As a **{role}**, here's everything I can help "
                f"you with:\n\n"
                f"{suggestions_text}\n\n"
                f"I can also:\n"
                f"- Answer follow-up questions in context\n"
                f"- Download source documents\n"
                f"- Search across {accessible_docs} PDFs "
                f"simultaneously\n\n"
                f"Just ask your question in plain English!"
            )

        else:
            # Document stats question
            dept_breakdown = "\n".join([
                f"  - {d}: {DEPT_DOC_COUNTS.get(d, 0)} documents"
                for d in accessible
            ])

            answer = (
                f"Here's your document access summary "
                f"as **{role}**:\n\n"
                f"**Departments you can access:** {dept_list}\n\n"
                f"**Your documents:**\n{dept_breakdown}\n\n"
                f"**Total documents you can search:** "
                f"{accessible_docs} PDFs\n"
                f"**Searchable chunks:** ~{accessible_chunks}\n\n"
                f"*(Full system: {TOTAL_DOCUMENTS} documents, "
                f"{TOTAL_CHUNKS:,} chunks across "
                f"{TOTAL_DEPTS} departments)*\n\n"
                f"What would you like to know?"
            )

        return {
            "answer":      answer,
            "sources":     [],
            "role":        role,
            "chunks_used": 0,
            "question":    question,
            "intent":      "SYSTEM"
        }


    # ── Handler: OUT_OF_SCOPE ─────────────────────────────
    def _handle_out_of_scope(
        self, role: str, question: str
    ) -> dict:
        """
        Politely redirects out-of-scope questions.
        Mentions only the user's accessible departments.
        """
        accessible = ROLE_ACCESS_MAP.get(role, [role])
        dept_list  = ", ".join(accessible)

        suggestions = []
        if "HR"         in accessible:
            suggestions.append("HR policies")
        if "Finance"    in accessible:
            suggestions.append("Finance procedures")
        if "IT"         in accessible:
            suggestions.append("IT guidelines")
        if "Legal"      in accessible:
            suggestions.append("Legal compliance")
        if "Operations" in accessible:
            suggestions.append("Operations processes")

        suggestion_text = ", ".join(suggestions[:3])

        answer = (
            f"I'm only able to answer questions based on your "
            f"company's internal documents.\n\n"
            f"As a **{role}**, I have access to your "
            f"**{dept_list}** documents. Try asking me about "
            f"{suggestion_text}, or any other topic covered "
            f"in your department documents.\n\n"
            f"What would you like to know?"
        )

        return {
            "answer":      answer,
            "sources":     [],
            "role":        role,
            "chunks_used": 0,
            "question":    question,
            "intent":      "OUT_OF_SCOPE"
        }


    # ── Handler: DOCUMENT ─────────────────────────────────
    def _handle_document(
        self,
        question:             str,
        role:                 str,
        n_chunks:             int,
        conversation_history: list
    ) -> dict:
        """
        Full RAG pipeline:
        1. Retrieve relevant chunks (RBAC filtered)
        2. Check confidence (relevance scores)
        3. Build prompt with context + history
        4. Generate grounded answer via Groq
        5. Return answer + citations
        """

        # Step 1 — Retrieve
        chunks = self.retriever.search_by_role(
            query=    question,
            role=     role,
            n_results=n_chunks
        )

        if not chunks:
            accessible = ROLE_ACCESS_MAP.get(role, [role])
            return {
                "answer": (
                    f"I could not find any relevant information "
                    f"about this in your accessible documents "
                    f"({', '.join(accessible)}).\n\n"
                    f"Try rephrasing your question or ask about "
                    f"a different topic."
                ),
                "sources":     [],
                "role":        role,
                "chunks_used": 0,
                "question":    question,
                "intent":      "DOCUMENT"
            }

        # Step 2 — Confidence check
        # If all chunks score below 25%, we're not confident
        top_score    = chunks[0]["score"]
        low_confidence = top_score < 0.25

        # Step 3 — Build context
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['filename']} "
                f"| Department: {chunk['department']} "
                f"| Relevance: {round(chunk['score']*100)}%]\n"
                f"{chunk['content']}"
            )
        context = "\n\n".join(context_parts)

        # Step 4 — Build messages with history
        messages = [
            {
                "role":    "system",
                "content": build_rag_system_prompt(role)
            }
        ]

        # Add last 10 messages of history
        recent_history = conversation_history[-10:]
        for msg in recent_history:
            messages.append({
                "role": (
                    msg.role if hasattr(msg, 'role')
                    else msg["role"]
                ),
                "content": (
                    msg.content if hasattr(msg, 'content')
                    else msg["content"]
                )
            })

        # Add confidence note if needed
        confidence_note = ""
        if low_confidence:
            confidence_note = (
                "\n\nNote: The retrieved documents have low "
                "relevance to this question. Be honest about "
                "uncertainty and tell the user if you cannot "
                "find a confident answer."
            )

        messages.append({
            "role":    "user",
            "content": (
                f"Here are relevant excerpts from company documents:"
                f"\n\n{context}\n\n---\n\n"
                f"Based ONLY on the above documents, answer:\n"
                f"{question}\n\n"
                f"Always cite which document(s) your answer "
                f"comes from.{confidence_note}"
            )
        })

        # Step 5 — Generate answer
        print(f"\n🤖 Sending to Groq ({self.model})...")
        print(f"   Top chunk score: {round(top_score*100)}% "
              f"({'low confidence' if low_confidence else 'good'})")

        response = self.groq_client.chat.completions.create(
            model=       self.model,
            messages=    messages,
            temperature= 0.1,
            max_tokens=  1024
        )

        answer_text = response.choices[0].message.content

        # Step 6 — Build citations (deduplicated)
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

        print(f"✅ Answer generated")
        print(f"   Sources: {[s['filename'] for s in sources]}")

        return {
            "answer":      answer_text,
            "sources":     sources,
            "role":        role,
            "chunks_used": len(chunks),
            "question":    question,
            "intent":      "DOCUMENT"
        }