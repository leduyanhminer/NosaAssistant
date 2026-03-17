import ollama
from typing import Generator, Optional

class OllamaProvider:
    def __init__(self, model_name: str = "qwen2.5:14b-instruct-q4_K_M", base_url: Optional[str] = None):
        self.model_name = model_name
        self.client = ollama.Client(host='http://localhost:11434')
    
    def invoke(self, system_prompt: str, user_prompt, temperature: float = 0.2) -> str:
        try:
            response = self.client.generate(
                model=self.model_name,
                system=system_prompt,
                prompt=user_prompt,
                options={
                    "temperature": temperature,
                    "num_ctx": 8192 
                }
            )
            return response.response
        except Exception as e:
            return f"Lỗi kết nối Ollama: {str(e)}"
        
    def stream(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Generator:
        try:
            stream = self.client.generate(
                model=self.model_name,
                system=system_prompt,
                prompt=user_prompt,
                stream=True,
                options={"temperature": temperature}
            )
            for chunk in stream:
                yield chunk['response']
        except Exception as e:
            yield f"Lỗi Stream Ollama: {str(e)}"