from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, models, PointStruct
from typing import List, Dict, Any
import uuid

class QdrantManager:
    def __init__(self, collection_name, embedder, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.embedder = embedder
        self.collection_name = collection_name

    def create_collection(self, vector_size):
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                )
            }
        )

    def upsert_chunks(self, chunks):
        """
        chunks: list of dicts [{'text': '...', 'metadata': {...}}, ...]
        """
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
                        "content": chunk['text'],
                        **chunk['metadata']
                    }
                )
            )
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"✅ Đã nạp {len(points)} đoạn văn bản vào Qdrant.")

    def search_chunks(self, query: str, top_k: int = 3) -> List[Dict]:
        query_vector = self.embedder.get_embedding(query, task="retrieval.query")
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True
        )

        contexts = [res.payload.get("content", "") for res in search_results]
        return contexts
    