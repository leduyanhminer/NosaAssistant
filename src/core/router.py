import os
import re
import json

from src.core.templates.prompt import *
from src.core.memory import SessionState

class RouterManager:
    def __init__(self, router_llm):
        self.router_llm = router_llm

    def route(self, session_state: SessionState, model_name):
        last_user_msg = session_state.buffer_msg[-1].content
        recent_msg = "\n".join([f"{m.role}: {m.content}" for m in session_state.buffer_msg[:-1]])
        context = session_state.current_summary or "Cuộc hội thoại mới bắt đầu."
        router_prompt = ROUTER_PROMPT.format(
            context=context,
            recent_history=recent_msg,
            user_msg=last_user_msg
        )
        response = self.router_llm.generate_text(user_prompt=router_prompt, model=model_name)
        try:
            clean_json = re.sub(r"```json|```", "", response).strip()
            result = json.loads(clean_json)
            
            return {
                "intent": result.get("intent", "RAG").upper(),
                "confidence": float(result.get("confidence", 0.5)),
                "reason": result.get("reason", "")
            }
        except Exception as e:
            # Nếu lỗi trả về default
            print(f"⚠️ Router Parse Error: {e}")
            return {"intent": "RAG", "confidence": 0.0, "reason": "Parse failed"}
