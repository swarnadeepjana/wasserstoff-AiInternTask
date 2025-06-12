from fastapi import UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
from fastapi import Form
from typing import List,Optional
import os
import json
import requests
import os
from uuid import uuid4
import pandas as pd
from datetime import datetime
import shutil
import re
import filetype
import shutil
from backend.app.config import settings
from backend.app.services.extractor import extract_text_from_pdf, extract_author_from_pages
from backend.app.services.chunker import chunk_text_by_paragraph
from backend.app.services.embedder import embed_chunks
from ..services.ocr import extract_text_from_scanned_pdf as extract_text_from_image

from backend.app.core.vector_store import VectorStore

router = APIRouter()

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    author: str = Form("..."),
    doc_type: str = Form("...")
):
    if not files or len(files) == 0:
        return JSONResponse(status_code=400, content={"error": "No files were uploaded."})

    try:
        print("🚀 Upload started")
        print("📂 VECTOR_DB_PATH is:", settings.VECTOR_DB_PATH)

        all_chunks = []
        metadata_path = "backend/data/embeddings/metadata.json"
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata_list = json.load(f)
        else:
            metadata_list = []

        for file in files:
            file_path = os.path.join(settings.DOCUMENT_DIR, file.filename)
            
            
            # ✅ Prevent duplicate uploads
            if os.path.exists(file_path):
                print(f"⚠️ Duplicate file skipped: {file.filename}")
                continue
            
            
            print(f"📥 Saving {file.filename} to {file_path}")
            os.makedirs(settings.DOCUMENT_DIR, exist_ok=True)

            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)



            # Step 1: Extract text from PDF
            pages = extract_text_from_pdf(file_path)
            author_name = extract_author_from_pages(pages)
            
            
            # Step 2: Use OCR if needed
            if not pages or not any(p["text"].strip() for p in pages):
                texts = extract_text_from_image(file_path)
                pages = [{"page": i + 1, "text": t} for i, t in enumerate(texts)]

            if not pages or not any(p["text"].strip() for p in pages):
                print(f"❌ No text found in {file.filename}, skipping.")
                continue



            # Step 3: Generate doc_id
            doc_id = f"DOC{str(uuid4().int)[:6]}"



            # Step 4: Chunk and embed
            chunks = chunk_text_by_paragraph(pages, max_chunk_size=settings.MAX_CHUNK_SIZE, doc_id=doc_id)
            embedded = embed_chunks(chunks)
            for chunk in embedded:
                chunk["doc_id"] = doc_id
            all_chunks.extend(embedded)



            # Step 5: Save metadata
            preview = pages[0]["text"][:300] + "..." if pages else "No preview available"
            metadata = {
                "doc_id": doc_id,
                "filename": file.filename,
                "filetype": filetype.guess(file_path).extension if filetype.guess(file_path) else "unknown",
                "upload_time": datetime.now().isoformat(),
                "author": author_name,
                "date": datetime.now().date().isoformat(),
                "type": doc_type,
                "relevance_score": None,
                "preview": preview
            }

            metadata_list.append(metadata)
            shutil.copy(file_path, f"backend/data/embeddings/{file.filename}")


        # Save metadata.json
        with open(metadata_path, "w") as f:
            json.dump(metadata_list, f, indent=2)



        # Step 6: Save to vector DB
        if all_chunks:
            dim = len(all_chunks[0]["embedding"])
            store = VectorStore(dim=dim, db_path=settings.VECTOR_DB_PATH)
            store.add_embeddings(all_chunks)
            os.makedirs(os.path.dirname(settings.VECTOR_DB_PATH), exist_ok=True)
            print(f"🧠 Saving vector store with {len(all_chunks)} chunks to {settings.VECTOR_DB_PATH}")
            store.save()

        return {"message": f"✅ Uploaded and processed {len(files)} documents."}

    except Exception as e:
        print("❌ Upload failed:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    
    
    