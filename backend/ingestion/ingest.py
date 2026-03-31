# backend/ingestion/ingest.py
# ─────────────────────────────────────────────────────────
# This is the MASTER script that runs the full pipeline.
# Run this once to process all your PDFs.
# Run it again whenever you add new documents.
#
# Pipeline:
#   READ (pdf_reader) → CHUNK (chunker) → STORE (vector_store)
# ─────────────────────────────────────────────────────────

import sys
import os

# Make sure Python can find our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.pdf_reader import load_documents_from_folder
from ingestion.chunker import create_chunks
from ingestion.vector_store import VectorStoreManager
from core.config import settings


def run_ingestion():
    print("\n" + "═" * 55)
    print("   🚀 Enterprise AI — Document Ingestion Pipeline")
    print("═" * 55)
    
    # ── STAGE 1: READ ──────────────────────────────────
    print("\n📖 STAGE 1: Reading PDFs...")
    documents = load_documents_from_folder(settings.documents_path)
    
    if not documents:
        print("❌ No documents found. Check your documents/ folder.")
        return
    
    # ── STAGE 2: CHUNK ─────────────────────────────────
    print("\n✂️  STAGE 2: Chunking documents...")
    chunks = create_chunks(documents)
    
    # ── STAGE 3+4: EMBED + STORE ───────────────────────
    print("\n🧠 STAGE 3: Embedding + storing in ChromaDB...")
    vector_store = VectorStoreManager()
    vector_store.store_chunks(chunks)
    
    # ── DONE ───────────────────────────────────────────
    stats = vector_store.get_stats()
    
    print("\n" + "═" * 55)
    print("   ✅ Ingestion Complete!")
    print("═" * 55)
    print(f"   📄 Documents processed : {len(documents)}")
    print(f"   ✂️  Chunks created      : {len(chunks)}")
    print(f"   💾 Chunks in vector DB : {stats['total_chunks']}")
    print(f"   📁 Database location   : {stats['db_path']}")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    run_ingestion()