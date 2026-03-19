import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_URL = "http://localhost:11434"
    OLLAMA_URL_2 = "http://localhost:11435"
    JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")