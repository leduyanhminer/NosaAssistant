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
        new_content_to_sum = "\n".join([f"{m.role}: {m.content}" for m in to_summarize])
        summary_prompt = f"""
        Bạn là hệ thống nén bộ nhớ. Hãy cập nhật bản tóm tắt cũ bằng cách gộp thêm diễn biến mới.
        ---
        TÓM TẮT CŨ: {self.current_summary or "Khởi đầu hội thoại."}
        NỘI DUNG MỚI CẦN GỘP:
        {new_content_to_sum}
        ---
        YÊU CẦU:
        1. Viết dưới dạng các ý chính hoặc đoạn văn cực ngắn.
        2. Giữ lại tên dự án, thông số kỹ thuật, quyết định công nghệ.
        3. KHÔNG bắt đầu bằng "Bản tóm tắt là..." hay "AI đã thảo luận...".
        4. Ngôn ngữ: Tiếng Việt.
        BẢN TÓM TẮT MỚI:"""

        self.current_summary = self.summarize_llm.generate_text(system_prompt="", user_prompt=summary_prompt)
        print(f"\n--- [Hệ thống] Đã cập nhật tóm tắt mới: {self.current_summary[:50]}... ---\n")

    def get_full_prompt_messages(self, system_instruction: str):
        messages = [{"role": "system", "content": system_instruction}]
        if self.current_summary:
            messages[0]["content"] += f"\n\n Bối cảnh hội thoại trước đó: {self.current_summary}"
        
        messages.extend([m.to_llm_dict() for m in self.buffer_msg])
        return messages
    