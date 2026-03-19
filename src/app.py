import uvicorn
import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.vector_db import QdrantManager
from src.core.provider.jinaai_embedding import JinaAIEmbedder
from src.core.provider.ollama_llm import OllamaProvider
from src.core.engine import RAGAnswerEngine
from src.core.chunker import Chunker
from src.core.memory import ChatMemoryManager
from src.core.config import Config

app = FastAPI(title="RAG API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# summarize_llm = OllamaProvider(model_name="phi3.5:3.8b-instruct-q4_K_M", 
#                                base_url=Config.OLLAMA_URL_2)
llm = OllamaProvider(model_name="qwen2.5:14b-instruct-q4_K_M",
                     base_url=Config.OLLAMA_URL)
memory_manager = ChatMemoryManager(summarize_llm=llm, 
                                   threshold=10, 
                                   keep_recent=4)
embedder = JinaAIEmbedder(model_name="jina-embeddings-v3")

db_manager = QdrantManager(collection_name='test_collection', 
                           embedder=embedder)
rag_engine = RAGAnswerEngine(llm=llm, db_manager=db_manager)
chunker = Chunker()

class ChatRequest(BaseModel):
    query: str
    stream: bool = False

@app.get("/health")
async def health_check():
    return {"status": "active", "database": "connected"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ định dạng PDF.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        chunks = chunker.chunking_by_pages(file_path)

        db_manager.upsert_chunks(chunks)
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
        if request.stream:
            return StreamingResponse(
                rag_engine.generate_stream_response(request.query),
                media_type="text/plain"
            )
        
        answer = rag_engine.generate_response(request.query)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)