from pymongo import MongoClient
from src.core.memory import SessionState
import time

class MongoSessionStorage:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client["NosaAssistant"]
        self.collection = self.db["chat_sessions"]
        self.collection.create_index("session_id", unique=True)

    def save(self, state: SessionState):
        state_dict = state.model_dump()
        state_dict["updated_at"] = time.time()

        self.collection.update_one(
            {"session_id": state.session_id},
            {"$set": state_dict},
            upsert=True
        )
    
    def load(self, session_id):
        data = self.collection.find_one({"session_id": session_id})
        return SessionState(**data) if data else None

    def delete(self, session_id):
        self.collection.delete_one({"session_id": session_id})