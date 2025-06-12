# api/router.py
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from backend.app.services import document_processor, embedder, theme_identifier
from backend.app.core.vector_store import VectorStore
from backend.app.config import settings
from backend.app.models.answer import QueryResponse, Answer
import numpy as np
import uuid
import os

router = APIRouter()

# Initialize vector store (assume 384-dim for MiniLM)
vector_store = VectorStore(dim=384, db_path=settings.VECTOR_DB_PATH)

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    all_chunks = []
    for file in files:
        doc_id = str(uuid.uuid4())[:8]
        ext = file.filename.split(".")[-1].lower()

        content = await file.read()
        with open(f"{settings.DOCUMENT_DIR}/{doc_id}.{ext}", "wb") as f:
            f.write(content)

        chunks = document_processor.process(file.filename, content, doc_id)
        chunks = embedder.embed_chunks(chunks)
        all_chunks.extend(chunks)

    vector_store.add_embeddings(all_chunks)
    vector_store.save()
    return {"status": "success", "documents_uploaded": len(files)}

@router.post("/query")
async def query_documents(query: str = Form(...)) -> QueryResponse:
    embedding = embedder.model.encode([query], normalize_embeddings=True)[0]
    top_chunks = vector_store.search(np.array(embedding), top_k=8)

    answers = []
    for chunk in top_chunks:
        answers.append(Answer(
            doc_id=chunk.get("doc_id"),
            page=chunk.get("page", 0),
            chunk_index=chunk.get("chunk_index", 0),
            text=chunk.get("text")
        ))

    summary = theme_identifier.summarize_themes(query, top_chunks)

    return QueryResponse(
        question=query,
        answers=answers,
        summary=summary
    )
