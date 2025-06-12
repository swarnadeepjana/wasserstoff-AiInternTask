from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.upload import router as upload_router
from backend.app.api.query import router as query_router  # if exists
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Document Research & Theme Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)  # Handles POST /upload
app.include_router(query_router)   # Handles POST /query
pdf_dir = os.path.join("backend", "data", "embeddings")
app.mount("/pdfs", StaticFiles(directory="backend/data/embeddings"), name="pdfs")

@app.get("/")
def root():
    return {"message": "Document Theme Chatbot API is running."}
