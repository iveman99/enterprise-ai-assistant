# backend/ingestion/chunker.py
# ─────────────────────────────────────────────────────────
# This file takes a large document text and splits it
# into smaller overlapping chunks.
#
# WHY OVERLAP?
# Imagine a sentence is split exactly at the boundary:
#   Chunk 1: "Employees are entitled to 20 days of annual"
#   Chunk 2: "leave as per company policy section 4.2"
#
# Without overlap, searching for "annual leave" might
# miss this because the answer is split across chunks!
#
# With overlap (50 words), chunk 2 starts 50 words
# earlier, so both chunks contain the full sentence.
# ─────────────────────────────────────────────────────────

from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings


def create_chunks(documents: list[dict]) -> list[dict]:
    """
    Takes the list of document dicts from pdf_reader.py
    and splits each document's content into chunks.
    
    Input:  list of {content, department, filename, filepath}
    Output: list of {content, department, filename, filepath, chunk_index}
            (same structure but content is now a small chunk)
    
    RecursiveCharacterTextSplitter is the smartest splitter —
    it tries to split at paragraphs first, then sentences,
    then words. It never cuts mid-word.
    """
    
    # Create the splitter with our config settings
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,       # 500 characters per chunk
        chunk_overlap=settings.chunk_overlap,  # 50 char overlap between chunks
        length_function=len,
        
        # Try to split at these boundaries in order:
        # paragraph → sentence → word → character
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    all_chunks = []
    
    print(f"\n✂️  Chunking {len(documents)} documents...")
    print(f"   Chunk size: {settings.chunk_size} chars")
    print(f"   Overlap:    {settings.chunk_overlap} chars")
    print("─" * 50)
    
    for doc in documents:
        # Split this document's content into chunks
        text_chunks = splitter.split_text(doc["content"])
        
        print(f"   📄 {doc['filename'][:40]:<40} → {len(text_chunks)} chunks")
        
        # For each chunk, create a new record
        # keeping all the original metadata
        for i, chunk_text in enumerate(text_chunks):
            chunk_record = {
                "content": chunk_text,
                "department": doc["department"],
                "filename": doc["filename"],
                "filepath": doc["filepath"],
                "chunk_index": i,  # which chunk number this is
                
                # Unique ID for this chunk in the vector store
                # Format: HR_LeavePolicy.pdf_chunk_0
                "chunk_id": f"{doc['department']}_{doc['filename']}_chunk_{i}"
            }
            all_chunks.append(chunk_record)
    
    print(f"\n✅ Total chunks created: {len(all_chunks)}")
    return all_chunks
