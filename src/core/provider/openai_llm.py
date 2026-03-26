import os
from openai import OpenAI
from typing import List, Dict, Any, Optional

class OpenAIProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key không được cung cấp và không tìm thấy biến môi trường OPENAI_API_KEY.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, 
                      user_prompt: str, 
                      model: str = "gpt-4o-mini", 
                      system_prompt: str = "You are a helpful assistant.",
                      temperature: float = 0.7,
                      max_tokens: int = 1000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi khi gọi OpenAI API: {e}")
            return ""

    def generate_text_stream(self, 
                             user_prompt: str, 
                             model: str = "gpt-4o-mini", 
                             system_prompt: str = "You are a helpful assistant.",
                             temperature: float = 0.7,
                             max_tokens: int = 1000):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        except Exception as e:
            print(f"Lỗi khi gọi OpenAI API: {e}")
            yield ""
