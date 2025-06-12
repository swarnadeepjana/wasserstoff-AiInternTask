# tests/test_extractor.py

from backend.app.services.extractor import extract_text_from_pdf as extract_text

def test_pdf_extraction():
    path = "backend/data/sample.pdf"  # make sure this file exists
    text = extract_text(path)
    assert isinstance(text, str)
    assert len(text) > 0


if __name__ == "__main__":
    print("✅ Running test_extractor test...")