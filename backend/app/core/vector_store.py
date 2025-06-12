import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Optional


class VectorStore:
    def __init__(self, dim: int, db_path: str):
        self.dim = dim
        self.db_path = db_path
        self.index = faiss.IndexFlatL2(dim)
        self.metadata: List[Dict] = []

        if os.path.exists(db_path):
            self._load()

    def _load(self):
        with open(self.db_path, "rb") as f:
            data = pickle.load(f)
            if "index" in data and "metadata" in data:
                self.index = data["index"]
                self.metadata = data["metadata"]
            else:
                print("⚠️ VectorStore: Invalid index file format.")

    def save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as f:
            pickle.dump({"index": self.index, "metadata": self.metadata}, f)

    def add_embeddings(self, chunks: List[Dict]):
        vectors = np.array([chunk["embedding"] for chunk in chunks]).astype("float32")
        self.index.add(vectors)
        self.metadata.extend([{k: v for k, v in chunk.items() if k != "embedding"} for chunk in chunks])

    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_doc_ids: Optional[List[str]] = None) -> List[Dict]:
        query_vector = query_vector.astype("float32").reshape(1, -1)
        scores, indices = self.index.search(query_vector, top_k * 5)  # oversample, filter later

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            if filter_doc_ids and meta["doc_id"] not in filter_doc_ids:
                continue
            meta["score"] = float(score)  # Add score for UI
            results.append(meta)
            if len(results) >= top_k:
                break

        return results
