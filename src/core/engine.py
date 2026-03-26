import os
from src.core.templates.prompt import *
from typing import Generator
from src.core.memory import SessionState

class RAGAnswerEngine:
    def __init__(self, llm, db_manager):
        self.llm = llm
        self.db_manager = db_manager

    def generate_response(self, session_state: SessionState, model_name: str = "gpt-4o-mini"):
        session_id = session_state.session_id
        new_query = self.rewrite_query(session_state, model_name=model_name)
        contexts = self.db_manager.search_chunks(session_id, new_query, top_k=3)    
        user_msg = session_state.buffer_msg[-1].content
        recent_msg = "\n".join([f"{m.role}: {m.content}" for m in session_state.buffer_msg[:-1]])
        current_summary = session_state.current_summary
        print('current_summary: ', current_summary)
        print('recent_msg: ', recent_msg)
        print('user_msg: ', user_msg)
        print("new_query: ", new_query)
        # print(contexts)
        if not contexts:
            return "Xin lỗi, tôi không tìm thấy tài liệu liên quan."

        context_str = "\n\n".join([f"- {c}" for c in contexts])

        user_prompt = RAG_USER_TEMPLATE.format(
            current_summary=current_summary,
            recent_msg=recent_msg,
            retrieved_docs=context_str,
            user_msg=user_msg
        )
        response = self.llm.generate_text(system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_prompt, model=model_name)
        return response
    
    # def generate_stream_response(self, user_query: str) -> Generator: #to fix
    #     """Trả về từng token (Stream)"""
    #     contexts = self.db_manager.search_chunks(user_query, top_k=3)
    #     if not contexts:
    #         yield "Xin lỗi, tôi không tìm thấy tài liệu liên quan."
    #         return

    #     context_str = "\n\n".join([f"- {c}" for c in contexts])

    #     user_msg = RAG_USER_TEMPLATE.format(
    #         context=context_str,
    #         query=user_query
    #     )

    #     for chunk in self.llm.generate_text_stream(system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_msg):
    #         yield chunk
    
    def rewrite_query(self, session_state: SessionState, model_name='gpt-4o-mini'):
        current_summary = session_state.current_summary
        recent_msg = recent_msg = "\n".join([f"{m.role}: {m.content}" for m in session_state.buffer_msg[:-1]])
        user_msg = session_state.buffer_msg[-1].content
        rewrite_prompt = REWRITE_PROMPT.format(
            current_summary=current_summary,
            recent_msg=recent_msg,
            user_msg=user_msg
        )
        response = self.llm.generate_text(user_prompt=rewrite_prompt, model=model_name)
        return response
    
class GeneralChatEngine:
    def __init__(self, llm):
        self.llm = llm

    def generate_response(self, session_state: SessionState, model_name: str = "gpt-4o-mini"):
        user_msg = session_state.buffer_msg[-1].content
        recent_msg = "\n".join([f"{m.role}: {m.content}" for m in session_state.buffer_msg[:-1]])
        current_summary = session_state.current_summary
        user_prompt = CHAT_USER_TEMPLATE.format(
            current_summary=current_summary,
            recent_msg=recent_msg,
            user_msg=user_msg
        )
        print('current_summary: ', current_summary)
        print('recent_msg: ', recent_msg)
        print('user_msg: ', user_msg)
        response = self.llm.generate_text(system_prompt=CHAT_SYSTEM_PROMPT, user_prompt=user_prompt, model=model_name)
        return response
    
    # def generate_stream_response(self, user_query: str) -> Generator:
    #     """Trả về từng token (Stream)"""

    #     user_msg = CHAT_USER_TEMPLATE.format(
    #         query=user_query
    #     )

    #     for chunk in self.llm.generate_text_stream(system_prompt=CHAT_SYSTEM_PROMPT, user_prompt=user_msg):
    #         yield chunk