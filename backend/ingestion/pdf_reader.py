# backend/ingestion/pdf_reader.py
# ─────────────────────────────────────────────────────────
# This file is responsible for ONE thing only:
# Open a PDF file and extract all the text from it.
#
# We use PyMuPDF (imported as fitz) — it's the best
# PDF parser available. It handles scanned docs, tables,
# multi-column layouts better than any other library.
# ─────────────────────────────────────────────────────────

import fitz  # This is PyMuPDF — fitz is its internal name
import os
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a single PDF file and extracts all text from it.
    
    What happens inside:
    - Opens the PDF
    - Loops through every page
    - Extracts text from each page
    - Joins everything into one big string
    
    Returns: the full text as a string
    """
    text = ""
    
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Loop through every page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text from this page
            page_text = page.get_text()
            
            # Add a page marker so we know where pages start
            # This helps with debugging later
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page_text
        
        doc.close()
        
    except Exception as e:
        print(f"  ⚠️  Could not read {pdf_path}: {e}")
        return ""
    
    return text.strip()


def load_documents_from_folder(documents_path: str) -> list[dict]:
    """
    Walks through the entire documents/ folder structure.
    
    Folder structure it expects:
        documents/
            HR/          ← department name
                file1.pdf
                file2.pdf
            Finance/
                file3.pdf
    
    For each PDF it finds, it creates a dict like:
    {
        "content": "full extracted text...",
        "department": "HR",
        "filename": "Leave Policy.pdf",
        "filepath": "documents/HR/Leave Policy.pdf"
    }
    
    Returns: list of these dicts — one per PDF
    """
    
    documents = []
    documents_path = Path(documents_path)
    
    print(f"\n📂 Scanning documents folder: {documents_path}")
    print("─" * 50)
    
    # Loop through each department folder (HR, Finance, IT...)
    for dept_folder in sorted(documents_path.iterdir()):
        
        # Skip if it's not a folder
        if not dept_folder.is_dir():
            continue
        
        department = dept_folder.name  # "HR", "Finance", etc.
        pdf_files = list(dept_folder.glob("*.pdf"))
        
        print(f"\n📁 {department}/ → found {len(pdf_files)} PDF(s)")
        
        # Loop through each PDF in this department folder
        for pdf_file in sorted(pdf_files):
            print(f"   📄 Reading: {pdf_file.name}...", end=" ")
            
            # Extract text from this PDF
            content = extract_text_from_pdf(str(pdf_file))
            
            if not content:
                print("❌ empty or unreadable")
                continue
            
            # Build the document record
            doc_record = {
                "content": content,
                "department": department,
                "filename": pdf_file.name,
                "filepath": str(pdf_file)
            }
            
            documents.append(doc_record)
            
            # Show how much text was extracted
            word_count = len(content.split())
            print(f"✅ {word_count:,} words extracted")
    
    print(f"\n{'─' * 50}")
    print(f"✅ Total documents loaded: {len(documents)}")
    
    return documents