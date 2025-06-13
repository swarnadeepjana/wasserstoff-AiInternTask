import os
from dotenv import load_dotenv

load_dotenv()  
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "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")

    DOCUMENT_DIR = "backend/data/uploads/"
    VECTOR_DB_PATH = "backend/data/embeddings/index.pkl"


    MAX_CHUNK_SIZE: int = 500

settings = Settings()
