import os
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import time


class MessageState(BaseModel):
    role : str
    content: str
    timestamp: float = Field(default_factory=time.time)
    def to_llm_dict(self):
        """Chuyển đổi sang định dạng mà các thư viện LLM (Ollama, OpenAI) yêu cầu"""
        return {"role": self.role, "content": self.content}

class ChatMemoryManager:
    def __init__(self, summarize_llm, threshold=10, keep_recent=4):
        self.summarize_llm = summarize_llm
        self.threshold = threshold
        self.keep_recent = keep_recent

        self.buffer_msg : List[MessageState] = []
        self.current_summary: str = ""

    def add_message(self, role: str, content: str):
        msg = MessageState(role=role, content=content)
        self.buffer_msg.append(msg)
        if len(self.buffer) > self.threshold:
            self._summarize_old_message()
        
    def _summarize_old_message(self):
        to_summarize = self.buffer_msg[:-self.keep_recent]
        self.buffer_msg = self.buffer_msg[-self.keep_recent:]
        