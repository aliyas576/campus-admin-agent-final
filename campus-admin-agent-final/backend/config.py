import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./campus.db")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    AGENT_MODEL = os.getenv("AGENT_MODEL", "llama-3.1-8b-instant")
    PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "./storage/pdfs")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./storage/vector_db")

settings = Settings()