from typing import List, Dict
from uuid import uuid4
import textwrap


def chunk_text_by_paragraph(pages: List[Dict], doc_id: str, max_chunk_size: int = 500) -> List[Dict]:
    """
    Splits text from each page into smaller chunks with citation metadata.
    Returns a list of dicts with: chunk_id, doc_id, page, chunk_index, text
    """
    chunks = []

    for page_obj in pages:
        page = page_obj["page"]
        text = page_obj["text"]
        paras = [p.strip() for p in text.split("\n") if p.strip()]
        chunk_idx = 0
        for para in paras:
            if len(para) > max_chunk_size:
                wrapped = textwrap.wrap(para, width=max_chunk_size)
                for part in wrapped:
                    chunks.append({
                        "chunk_id": f"{doc_id}-P{page}-C{chunk_idx}",
                        "doc_id": doc_id,
                        "page": page,
                        "chunk_index": chunk_idx,
                        "text": part.strip()
                    })
                    chunk_idx += 1
            else:
                chunks.append({
                    "chunk_id": f"{doc_id}-P{page}-C{chunk_idx}",
                    "doc_id": doc_id,
                    "page": page,
                    "chunk_index": chunk_idx,
                    "text": para.strip()
                })
                chunk_idx += 1
    return chunks
