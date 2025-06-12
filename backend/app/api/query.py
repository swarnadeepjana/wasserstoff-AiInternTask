# --- query.py ---
from fastapi import APIRouter, Request
from sentence_transformers import SentenceTransformer
from backend.app.config import settings
from backend.app.core.vector_store import VectorStore
import requests
import re
from nltk.tokenize import sent_tokenize

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_context_snippet(text: str, keyword: str) -> str:
    """
    Extracts a context snippet around the keyword using only periods (.) as sentence delimiters.
    Returns the sentence before, the sentence containing the keyword, and the one after.
    """
    # Split by '.' and clean each sentence
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    for i, sentence in enumerate(sentences):
        if keyword.lower() in sentence.lower():
            before = sentences[i - 1] + '.' if i > 0 else ''
            current = sentence + '.'
            after = sentences[i + 1] + '.' if i < len(sentences) - 1 else ''
            return f"{before} {current} {after}".strip()

    # If keyword not found, fallback
    return text



def synthesize_themes(answers: list, question: str) -> str:
    prompt = f"You are a research assistant. Given the question: \"{question}\", analyze the following answers:\n\n"
    for i, ans in enumerate(answers):
        citation = f"Doc: {ans['doc_id']}, Page: {ans.get('page')}, Para: {ans.get('para', ans.get('chunk_index'))}"
        prompt += f"{i+1}. \"{ans['text']}\" ({citation})\n"
    prompt += "\nIdentify main themes and provide a summary per theme with citations."

    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        return res.json()["response"].strip()
    except Exception as e:
        return f"❌ Ollama Error: {str(e)}"


@router.post("/query")
async def query_documents(request: Request):
    data = await request.json()
    question = data.get("query")
    doc_ids = data.get("doc_ids")
    top_k = data.get("top_k", 10)

    if not question:
        return {"error": "Query cannot be empty."}

    query_embedding = model.encode([question])[0]
    store = VectorStore(dim=len(query_embedding), db_path=settings.VECTOR_DB_PATH)
    results = store.search(query_embedding, top_k=top_k, filter_doc_ids=doc_ids)

    answers = []
    for res in results:
        snippet = extract_context_snippet(res["text"], question)
        answers.append({
            "doc_id": res["doc_id"],
            "page": res.get("page"),
            "chunk_index": res.get("chunk_index"),
            "para": res.get("para"),
            "text": snippet,
            "filename": res.get("filename") 
        })

    summary = synthesize_themes(answers, question)
    return {"question": question, "answers": answers, "theme_summary": summary}
