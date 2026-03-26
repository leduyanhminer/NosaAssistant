from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, PointStruct, PayloadSchemaType, FieldCondition, MatchValue
from typing import List, Dict, Any
import uuid

from src.core.config import Config

class QdrantManager:
    def __init__(self, collection_name, embedder, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.embedder = embedder
        self.collection_name = collection_name
        self._is_initialized = False

    def create_collection(self):
        if self._is_initialized:
            return
        if not self.client.collection_exists(self.collection_name):
            print(f"🚀 Creating new collection: {self.collection_name}")
            vector_size = Config.EMBEDDING_SIZE

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            # Tạo Index cho session_id
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="session_id",
                field_schema=PayloadSchemaType.KEYWORD
            )
        self._is_initialized = True

    def upsert_chunks(self, session_id: str, chunks: List[Dict]):
        """
        chunks: list of dicts [{'text': '...', 'metadata': {...}}, ...]
        """
        self.create_collection()
        texts = [chunk['text'] for chunk in chunks]
        vectors = self.embedder.get_embedding(texts, task="retrieval.passage")
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "session_id": session_id,
                        "content": chunk['text'],
                        **chunk.get('metadata', {})
                    }
                )
            )
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"✅ Đã nạp {len(points)} đoạn văn bản vào Qdrant.")

    def search_chunks(self, session_id: str, query: str, top_k: int = 3) -> List[Dict]:
        query_vector = self.embedder.get_embedding(query, task="retrieval.query")
        query_vector = query_vector[0]
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=session_id)
                    )
                ]
            ),
            limit=top_k,
            with_payload=True
        ).points
        contexts = [res.payload.get("content", "") for res in search_results]
        return contexts
    
    def delete_session(self, session_id: str):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(
                    key="session_id", match=MatchValue(value=session_id)
                )]
            )
        )
        print(f"🗑️ Đã xóa dữ liệu của session: {session_id} khỏi collection!")