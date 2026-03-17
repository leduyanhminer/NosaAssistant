import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient

from core.vector_db import QdrantManager
from core.provider.jinaai_embedding import JinaAIEmbedder
from core.provider.ollama_llm import OllamaProvider
from src.core.engine import RAGAnswerEngine

app = FastAPI(title="RAG API")

embedder = JinaAIEmbedder(model_name="jina-embeddings-v3")
llm = OllamaProvider(model_name="qwen2.5:14b-instruct-q4_K_M")

db_manager = QdrantManager(collection_name='test_collection', embedder=embedder)

rag_engine = RAGAnswerEngine(llm=llm, db_manager=db_manager)

class ChatRequest(BaseModel):
    query: str
    stream: bool = False

@app.get("/health")
async def health_check():
    return {"status": "active", "database": "connected"}

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
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)