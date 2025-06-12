# tests/test_chunker.py

from backend.app.services.chunker import chunk_text_by_paragraph as chunk_text

def test_chunking():
    sample_text = "This is a long document. It has multiple sentences for testing chunking functionality."
    chunks = chunk_text(sample_text)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert "text" in chunks[0]


if __name__ == "__main__":
    print("✅ Running test_chunker test...")
