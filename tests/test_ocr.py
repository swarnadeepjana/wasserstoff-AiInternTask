# tests/test_ocr.py

from backend.app.services.ocr import extract_text_from_scanned_pdf as extract_text_from_image

def test_ocr_image_extraction():
    # Use a dummy image or mock path if needed
    image_path = "backend/data/sample_scan.png"  # make sure this exists for testing
    text = extract_text_from_image(image_path)
    assert isinstance(text, str)
    assert len(text) > 0  # or a known substring check


if __name__ == "__main__":
    print("✅ Running test_ocr test...")