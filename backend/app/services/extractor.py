import fitz  # PyMuPDF
import re
from typing import List, Dict


def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extracts structured text from a digital PDF.
    Returns a list of dictionaries containing page, para index, and text.
    """
    try:
        doc = fitz.open(pdf_path)
        paragraphs = []

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if not text:
                continue

            raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for para_index, para in enumerate(raw_paragraphs):
                paragraphs.append({
                    "page": page_num,
                    "para": para_index,
                    "text": para
                })

        return paragraphs

    except Exception as e:
        print(f"❌ Failed to extract text from PDF: {e}")
        return []


def extract_author_from_pages(pages: List[Dict]) -> str:
    """
    Extracts likely author names from the first 1–2 pages of a document.
    Strategy:
    - Author names are typically between the title and affiliation block
    - Affiliation block often includes keywords like university, department, email
    - We look for capitalized names of max length 30 chars
    """
    # Combine first 2 pages into lines
    full_text = "\n".join([page.get("text", "") for page in pages[:2]])
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    affiliation_keywords = [
        "university", "institute", "department", "college", "school", "faculty",
        "email", "@", "lab", "center", "programme", "laboratory"
    ]

    found_title = False
    potential_authors = []

    for i, line in enumerate(lines):
        lower_line = line.lower()

        # Skip title (assumed to be first long line)
        if not found_title and len(line.split()) >= 5:
            found_title = True
            continue

        # Stop if affiliation line reached
        if any(kw in lower_line for kw in affiliation_keywords):
            break

        if found_title:
            # Look for personal names
            name_pattern = r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}"
            matches = re.findall(name_pattern, line)
            for name in matches:
                if len(name) <= 30:
                    potential_authors.append(name)
                    
        

    if potential_authors:
        return ", ".join(potential_authors)
    return "Unknown"


     # ✅ Match "By John Doe" or "Authors: Jane Smith, Alex Ray"
    match = re.search(r'(?:by|author[s]?)[:\s]+([^\n]+)', line_clean, re.IGNORECASE)
    if match:
            names = match.group(1)
            # Split by comma or "and"
            for name in re.split(r',| and ', names):
                name = name.strip()
                # Reject if too long or looks like email/university
                if (
                    3 < len(name) < 20 and
                    not re.search(r'@|university|college|department|institute', name.lower())
                ):
                    # Optional: make sure it's name-like
                    if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', name):
                        possible_authors.append(name)

    return ", ".join(possible_authors) if possible_authors else "Unknown"