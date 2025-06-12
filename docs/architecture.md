# System Architecture

## Overview
This system is a document-aware chatbot capable of:
- Ingesting 75+ documents (PDF, scanned, or text)
- Answering questions with accurate citations
- Summarizing themes across documents

## Components

### 1. **Frontend**
- Built using Streamlit
- Allows document upload and natural language question input

### 2. **Backend**
- FastAPI-based microservice
- Endpoints: `/upload`, `/query`, `/themes`
- Handles processing, embedding, and querying

### 3. **Processing Pipeline**
- OCR (Tesseract + pdf2image)
- Text Chunking (by paragraph)
- Embedding (MiniLM from HuggingFace)
- Vector Store (FAISS)

### 4. **Theme Identifier**
- Groups relevant answers by theme using cosine similarity
- Synthesizes themes into a chat-style response

### 5. **Storage**
- In-memory FAISS vector index
