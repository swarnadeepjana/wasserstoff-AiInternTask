# services/document_processor.py

import uuid
from ..services.extractor import extract_text_from_pdf as extract_text
from ..services.ocr import extract_text_from_scanned_pdf as extract_text_from_image
from ..services.chunker import chunk_text_by_paragraph as chunk_text
from ..services.embedder import embed_chunks 
from typing import List, Dict
import fitz  # PyMuPDF for page count
import io
import filetype

def process(filename: str, content: bytes, doc_id: str) -> List[Dict]:
    ext = filename.split(".")[-1].lower()
    chunks = []
    
    if not doc_id:
        doc_id = str(uuid.uuid4())

    if ext in ["pdf"]:
        try:
            text_by_page = extract_text(content)
        except:
            text_by_page = extract_text_from_image(content)  # fallback to OCR

        for page_num, page_text in enumerate(text_by_page):
            for i, chunk in enumerate(chunk_text(page_text)):
                chunks.append({
                    "doc_id": doc_id,
                    "page": page_num + 1,
                    "chunk_index": i,
                    "text": chunk
                })

    elif ext in ["jpg", "jpeg", "png"]:
        full_text = extract_text_from_image(content)
        for i, chunk in enumerate(chunk_text(full_text)):
            chunks.append({
                "doc_id": doc_id,
                "page": 1,
                "chunk_index": i,
                "text": chunk
            })

    elif ext in ["txt"]:
        text = content.decode("utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            chunks.append({
                "doc_id": doc_id,
                "page": 1,
                "chunk_index": i,
                "text": chunk
            })
            embedded_chunks = embed_chunks(chunks)

    return embedded_chunks



if __name__ == "__main__":
    print("✅ Running document_processor test...")


