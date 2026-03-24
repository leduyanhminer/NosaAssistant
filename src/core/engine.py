import os
from src.core.templates.prompt import *
from typing import Generator

class RAGAnswerEngine:
    def __init__(self, llm, db_manager):
        self.llm = llm
        self.db_manager = db_manager

    def generate_response(self, user_query: str, model_name: str = "gpt-5-nano"):
        contexts = self.db_manager.search_chunks(user_query, top_k=3)
        
        if not contexts:
            return "Xin lỗi, tôi không tìm thấy tài liệu liên quan."

        context_str = "\n\n".join([f"- {c}" for c in contexts])

        user_msg = RAG_USER_TEMPLATE.format(
            context=context_str,
            query=user_query
        )
        # print(user_msg)
        response = self.llm.generate_text(system_prompt=RAG_SYSTEM_INSTRUCTION, user_prompt=user_msg, model=model_name)
        return response
    
    def generate_stream_response(self, user_query: str) -> Generator:
        """Trả về từng token (Stream)"""
        contexts = self.db_manager.search_chunks(user_query, top_k=3)
        if not contexts:
            yield "Xin lỗi, tôi không tìm thấy tài liệu liên quan."
            return

        context_str = "\n\n".join([f"- {c}" for c in contexts])

        user_msg = RAG_USER_TEMPLATE.format(
            context=context_str,
            query=user_query
        )

        for chunk in self.llm.generate_text_stream(system_prompt=RAG_SYSTEM_INSTRUCTION, user_prompt=user_msg):
            yield chunk