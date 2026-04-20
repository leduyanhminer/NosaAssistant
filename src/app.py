import uvicorn
import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import redis

from core.db.vector_db import QdrantManager
from src.core.provider.jinaai_embedding import JinaAIEmbedder
from src.core.provider.ollama_llm import OllamaProvider
from src.core.provider.openai_llm import OpenAIProvider
from src.core.engine import RAGAnswerEngine, GeneralChatEngine
from src.core.chunker import Chunker
from src.core.memory import ChatMemoryManager, SessionState
from src.core.config import Config
from core.db.redis import RedisManager
from src.core.router import RouterManager
from core.db.mongo import MongoSessionStorage

app = FastAPI(title="RAG API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# summarize_llm = OllamaProvider(model_name="phi3.5:3.8b-instruct-q4_K_M", 
#                                base_url=Config.OLLAMA_URL_2)
# llm = OllamaProvider(model_name=Config.LLM_MODEL_NAME,
#                      base_url=Config.OLLAMA_URL)

llm = OpenAIProvider(api_key=Config.OPENAI_API_KEY)
embedder = JinaAIEmbedder(model_name="jina-embeddings-v3")
db_manager = QdrantManager(collection_name='my_collection', 
                           embedder=embedder)
db_manager.create_collection()
rag_engine = RAGAnswerEngine(llm=llm, db_manager=db_manager)
chat_engine = GeneralChatEngine(llm=llm)
router_manager = RouterManager(router_llm=llm)
chunker = Chunker()
redis_db = RedisManager()
mongo_db = MongoSessionStorage()

class ChatRequest(BaseModel):
    query: str
    session_id: str
    stream: bool = False

@app.get("/health")
async def health_check():
    return {"status": "active", "database": "connected"}

@app.post("/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ định dạng PDF.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        chunks = chunker.chunking_by_pages(file_path)

        db_manager.upsert_chunks(session_id=session_id, chunks=chunks)
        return {
            "message": f"Đã nạp thành công '{file.filename}'",
            "pages_processed": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")
    finally:
        # Tùy chọn: Xóa file sau khi nạp xong để tiết kiệm bộ nhớ
        if os.path.exists(file_path):
            os.remove(file_path)

# --- ENDPOINT CHAT ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if request.stream: # to fix
            return StreamingResponse(
                rag_engine.generate_stream_response(request.query),
                media_type="text/plain"
            )
        session_id = request.session_id
        session_state = redis_db.get_session(session_id)
        if not session_state:
            session_state = mongo_db.load(session_id)
            if session_state:
                redis_db.save_session(session_id, session_state)
            else:
                session_state = SessionState(session_id=session_id)
        memory_manager = ChatMemoryManager(session_state=session_state, summarize_llm=llm, threshold=10, keep_recent=4)
        memory_manager.add_message(role='user', content=request.query)
        router_results = router_manager.route(session_state=session_state, model_name='gpt-4o-mini')
        print(router_results)
        if router_results['intent'] == 'RAG' and router_results['confidence'] > 0.7:
            answer = rag_engine.generate_response(session_state=session_state)
        else:
            answer = chat_engine.generate_response(session_state=session_state)
        memory_manager.add_message(role='assistant', content=answer)
        redis_db.save_session(request.session_id, session_state)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)