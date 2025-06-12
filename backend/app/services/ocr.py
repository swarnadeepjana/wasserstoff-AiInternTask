import pytesseract
from pdf2image import convert_from_path
import os
from typing import List


def extract_text_from_scanned_pdf(pdf_path: str) -> List[str]:
    """
    Extracts text from a scanned PDF using OCR (Tesseract).
    Returns list of strings, one per page.
    """
    try:
        images = convert_from_path(pdf_path)
        page_texts = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            page_texts.append(text)
        return page_texts
    except Exception as e:
        print(f"OCR failed for {pdf_path}: {e}")
        return []
