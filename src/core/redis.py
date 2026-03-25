import redis
from typing import Optional
from src.core.memory import SessionState

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password, 
            decode_responses=True
        )

    def save_session(self, session_id: str, state: SessionState, ttl: int = 3600):
        """Lưu SessionState xuống Redis (mặc định hết hạn sau 1h)"""
        key = f"session:{session_id}"
        self.client.set(key, state.model_dump_json(), ex=ttl)

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Lấy dữ liệu và ép kiểu ngược lại thành Object Pydantic"""
        key = f"session:{session_id}"
        data = self.client.get(key)
        if data:
            return SessionState.model_validate_json(data)
        return None