import os
import pytest
from backend.app.services.document_processor import process

# Prepare mock data
def load_binary_file(filepath):
    with open(filepath, "rb") as f:
        return f.read()

def test_process_txt():
    content = b"This is a sample document.\n\nIt has two paragraphs."
    result = process("sample.txt", content, "doc1")
    assert isinstance(result, list)
    assert all("text" in chunk for chunk in result)
    assert all("doc_id" in chunk for chunk in result)
    assert all("page" in chunk for chunk in result)

def test_process_image():
    image_path = os.path.join("tests", "sample_image.jpg")
    if not os.path.exists(image_path):
        pytest.skip("Sample image not found for OCR test.")
    content = load_binary_file(image_path)
    result = process("sample_image.jpg", content, "doc2")
    assert isinstance(result, list)
    assert all("text" in chunk for chunk in result)
    assert all("doc_id" in chunk for chunk in result)

def test_process_pdf():
    pdf_path = os.path.join("tests", "sample_pdf.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("Sample PDF not found for PDF test.")
    content = load_binary_file(pdf_path)
    result = process("sample_pdf.pdf", content, "doc3")
    assert isinstance(result, list)
    assert all("text" in chunk for chunk in result)
    assert all("doc_id" in chunk for chunk in result)


if __name__ == "__main__":
    print("✅ Running test_document_processor test...")