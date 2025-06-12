from typing import List, Dict
from openai import OpenAI, RateLimitError
from backend.app.config import settings
import nltk
from nltk.tokenize import sent_tokenize
nltk.download("punkt_tab")

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def summarize_themes(query: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "No chunks to analyze."

    # Break into sentences
    sentence_chunks = []
    for chunk in chunks:
        sentences = sent_tokenize(chunk["text"])
        for s in sentences:
            sentence_chunks.append({
                "doc_id": chunk["doc_id"],
                "page": chunk.get("page", 0),
                "chunk_index": chunk.get("chunk_index", 0),
                "sentence": s
            })

    joined = "\n\n".join([
        f"Document: {c['doc_id']}, Page: {c['page']}, Chunk: {c['chunk_index']}\n{c['sentence']}"
        for c in sentence_chunks
    ])

    prompt = f"""
You are a research assistant. The user asked: "{query}".

You have these document excerpts:
{joined}

Your job:
1. Identify 2–4 main themes.
2. For each theme, give:
   - A short summary.
   - Exact sentences supporting the theme from the documents.
   - Include Document ID, Page Number, and Chunk Index.

Format:
Theme 1 – [Theme Name]
- DOC001, Page 2, Chunk 0: "Full sentence here..."
- DOC003, Page 5, Chunk 3: "Another supporting sentence..."

Only include exact sentences from the text above. Do not make up content.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return "⚠️ OpenAI API quota exceeded. Please check your usage or try again later."

    except Exception as e:
        return f"❌ OpenAI Error: {str(e)}"
