from typing import List, Dict
import numpy as np

# Example only: you can replace this with real embedding model
# services/embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # or your own model

def embed_chunks(chunks: List[Dict]) -> List[Dict]:
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    for i in range(len(chunks)):
        chunks[i]["embedding"] = embeddings[i].tolist()

    return chunks


