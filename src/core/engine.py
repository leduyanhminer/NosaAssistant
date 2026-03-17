import os

class RAGAnswerEngine:
    def __init__(self, llm, db_manager):
        self.llm = llm
        self.db_manager = db_manager

    def generate_response(self, user_query: str):
        contexts = self.db_manager.get_relevant_context(user_query, top_k=3)
        
        if not contexts:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu."

        context_str = "\n\n".join([f"- {c}" for c in contexts])

        full_prompt = f"""
        [SYSTEM INSTRUCTION]
        Bạn là một trợ lý AI chuyên nghiệp. Hãy trả lời câu hỏi dựa TRỰC TIẾP vào ngữ cảnh được cung cấp. 
        Nếu thông tin không có trong ngữ cảnh, hãy thành thật trả lời là bạn không biết.
        ----------------
        NGỮ CẢNH:
        {context_str}
        ----------------
        CÂU HỎI: {user_query}
        ----------------
        TRẢ LỜI:
        """

        response = self.llm.invoke(full_prompt)
        return response