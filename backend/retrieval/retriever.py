# backend/retrieval/retriever.py
# ─────────────────────────────────────────────────────────
# This file is the search engine of our system.
#
# It takes a user's question and finds the most relevant
# chunks from ChromaDB — filtered by department so users
# only see documents they are allowed to access.
#
# This is the "R" in RAG — Retrieval Augmented Generation.
# Without good retrieval, even the best LLM gives bad answers.
# ─────────────────────────────────────────────────────────

import chromadb
from chromadb.utils import embedding_functions
from core.config import settings


# Department access rules — who can see what
# This is our Role Based Access Control (RBAC) map
# Key   = the role/department of the logged in user
# Value = list of departments they can search
ROLE_ACCESS_MAP = {
    "HR":         ["HR"],
    "Finance":    ["Finance"],
    "IT":         ["IT"],
    "Legal":      ["Legal"],
    "Operations": ["Operations"],

    # HR Manager can see HR + Operations
    "HR_Manager": ["HR", "Operations"],

    # IT Manager can see IT + Operations
    "IT_Manager": ["IT", "Operations"],

    # Finance Manager can see Finance + Legal
    "Finance_Manager": ["Finance", "Legal"],

    # Executive can see everything
    "Executive":  ["HR", "Finance", "IT", "Legal", "Operations"],
}


class DocumentRetriever:
    """
    Searches the vector store for relevant document chunks.

    Two types of search:
    1. search_by_role()   → filters by user's department access
    2. search_all()       → searches everything (admin only)
    """

    def __init__(self):
        # Load the same embedding model we used during ingestion
        # This is critical — query and documents must use
        # the exact same model, otherwise search won't work
        self.embedding_fn = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )

        # Connect to the existing ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path
        )

        # Get our collection — must already exist (ingestion creates it)
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        total = self.collection.count()
        print(f"✅ Retriever ready — {total} chunks available")


    def search_by_role(
        self,
        query: str,
        role: str,
        n_results: int = 5
    ) -> list[dict]:
        """
        Searches for relevant chunks — filtered by user's role.

        Parameters:
            query     → the user's question in plain English
            role      → the user's department/role (e.g. "HR", "Finance")
            n_results → how many chunks to return (default 5)

        Returns:
            List of dicts, each containing:
            - content    : the actual text of the chunk
            - filename   : which document it came from
            - department : which department it belongs to
            - score      : how relevant it is (0-1, higher = better)
        """

        # Get the list of departments this role can access
        allowed_departments = ROLE_ACCESS_MAP.get(role, [role])

        if not allowed_departments:
            print(f"⚠️  Unknown role: {role}")
            return []

        print(f"\n🔍 Searching for: '{query}'")
        print(f"   Role: {role} → Access: {allowed_departments}")

        # Build the ChromaDB filter
        # This tells ChromaDB to ONLY search chunks where
        # the department metadata matches allowed departments
        if len(allowed_departments) == 1:
            # Simple filter for single department
            where_filter = {
                "department": {"$eq": allowed_departments[0]}
            }
        else:
            # OR filter for multiple departments
            where_filter = {
                "$or": [
                    {"department": {"$eq": dept}}
                    for dept in allowed_departments
                ]
            }

        # Perform the search
        # ChromaDB converts the query to a vector automatically
        # using our embedding_fn, then finds closest matches
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Format the results into clean readable dicts
        return self._format_results(results)


    def search_all(
        self,
        query: str,
        n_results: int = 5
    ) -> list[dict]:
        """
        Searches ALL departments — no access filtering.
        Use this only for admin/testing purposes.
        """

        print(f"\n🔍 Searching ALL departments for: '{query}'")

        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        return self._format_results(results)


    def _format_results(self, raw_results: dict) -> list[dict]:
        """
        Converts raw ChromaDB results into clean readable dicts.

        ChromaDB returns results in a nested list format:
        results["documents"] = [["chunk1", "chunk2", ...]]
        results["metadatas"] = [[{meta1}, {meta2}, ...]]
        results["distances"] = [[0.12, 0.34, ...]]

        We flatten this into a clean list of dicts.

        Distance → Score conversion:
        ChromaDB returns "distance" (lower = more similar)
        We convert to "score" (higher = more relevant) as:
        score = 1 - distance  (for cosine similarity)
        """

        formatted = []

        # ChromaDB wraps results in an extra list — we unwrap it
        documents = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            # Convert distance to relevance score
            # Distance 0.0 = perfect match → score 1.0
            # Distance 1.0 = no match      → score 0.0
            score = round(1 - dist, 4)

            formatted.append({
                "content":    doc,
                "filename":   meta.get("filename", "Unknown"),
                "department": meta.get("department", "Unknown"),
                "score":      score
            })

        # Sort by score — most relevant first
        formatted.sort(key=lambda x: x["score"], reverse=True)

        print(f"   ✅ Found {len(formatted)} relevant chunks")
        for r in formatted:
            print(f"      [{r['score']:.3f}] {r['department']} → "
                  f"{r['filename'][:45]}")

        return formatted


    def get_accessible_departments(self, role: str) -> list[str]:
        """Returns the list of departments a role can access."""
        return ROLE_ACCESS_MAP.get(role, [role])