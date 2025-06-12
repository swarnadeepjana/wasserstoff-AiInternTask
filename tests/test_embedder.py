# tests/test_embedder.py
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.embedder import embed_chunks

def test_embed_chunks_returns_embeddings():
    chunks = [
        {"text": "This is a test sentence."},
        {"text": "Embedding models convert text to vectors."}
    ]
    result = embed_chunks(chunks)

    assert len(result) == 2
    assert "embedding" in result[0]
    assert hasattr(result[0]["embedding"], "__len__")  # Should behave like a vector
    assert len(result[0]["embedding"]) > 0


if __name__ == "__main__":
    print("✅ Running test_embedder test...")