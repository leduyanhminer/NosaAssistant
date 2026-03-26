import json 
import requests
import os
from src.core.config import Config

class JinaAIEmbedder:
    def __init__(self, model_name='jina-embeddings-v3', api_key=None):
        self.api_key = api_key or Config.JINAAI_API_KEY
        self.model_name = model_name
        self.url = "https://api.jina.ai/v1/embeddings"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_embedding(self, texts, task, batch_size=16):
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i+batch_size]
            data = {
                "model": self.model_name,
                "task": task,
                "truncate": True,
                "input": batch
            }
            try:
                response = requests.post(self.url, headers=self.headers, json=data)
                result = response.json()
                batch_embeddings = [item["embedding"] for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"Lỗi tại batch khởi đầu từ vị trí {i}: {e}")
        
        return all_embeddings
