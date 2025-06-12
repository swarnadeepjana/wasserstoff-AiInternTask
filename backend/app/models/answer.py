# models/answer.py
from pydantic import BaseModel
from typing import List

class Answer(BaseModel):
    doc_id: str
    page: int
    chunk_index: int
    text: str

class QueryResponse(BaseModel):
    question: str
    answers: List[Answer]
    summary: str
