import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OLLAMA_URL = "http://localhost:11434"
    # OLLAMA_URL_2 = "http://localhost:11435"
    JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # LLM_MODEL_NAME = "qwen2.5:14b-instruct-q4_K_M"
    # LLM_MODEL_NAME = "llama3.2"