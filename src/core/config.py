import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_URL = "http://localhost:11434"
    JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")