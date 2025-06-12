# tests/test_vector_store.py
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app.core.vector_store import VectorStore

def test_vector_store_add_and_search(tmp_path):
    db_path = tmp_path / "test_store.pkl"
    store = VectorStore(dim=384, db_path=str(db_path))

    dummy_chunks = [
        {"text": "Test 1", "embedding": np.random.rand(384), "doc_id": "DOC001"},
        {"text": "Test 2", "embedding": np.random.rand(384), "doc_id": "DOC002"}
    ]
    store.add_embeddings(dummy_chunks)
    store.save()

    # Re-load and search
    new_store = VectorStore(dim=384, db_path=str(db_path))
    query_vector = dummy_chunks[0]["embedding"]
    results = new_store.search(query_vector=query_vector, top_k=1)

    assert len(results) == 1
    assert results[0]["doc_id"] in ["DOC001", "DOC002"]



