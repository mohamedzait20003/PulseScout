import os
import uuid
import hashlib
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)


class QdrantConnection:
    _instance: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        if cls._instance is None:
            url = os.getenv("QDRANT_URI") or "http://localhost:6333"
            api_key = os.getenv("QDRANT_KEY") or None
            cls._instance = QdrantClient(url=url, api_key=api_key)
        return cls._instance


class BaseModel:
    collection_name: str = ""
    vector_size: int = 384
    indexed_fields: list[str] = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def _client(cls) -> QdrantClient:
        return QdrantConnection.get_client()

    @classmethod
    def ensure_collection(cls):
        client = cls._client()
        collections = [c.name for c in client.get_collections().collections]
        if cls.collection_name not in collections:
            client.create_collection(
                collection_name=cls.collection_name,
                vectors_config=VectorParams(
                    size=cls.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            
            for field in cls.indexed_fields:
                client.create_payload_index(
                    collection_name=cls.collection_name,
                    field_name=field,
                    field_schema="keyword",
                )

    def to_payload(self) -> dict:
        raise NotImplementedError

    def to_document(self) -> str:
        raise NotImplementedError

    def to_point(self) -> PointStruct:
        return PointStruct(
            id=self._generate_id(),
            vector=self._embed(self.to_document()),
            payload=self.to_payload(),
        )

    def save(self):
        self.ensure_collection()
        self._client().upsert(
            collection_name=self.collection_name,
            points=[self.to_point()],
        )

    @classmethod
    def bulk_save(cls, instances: list) -> int:
        cls.ensure_collection()
        points = [inst.to_point() for inst in instances]
        if points:
            cls._client().upsert(collection_name=cls.collection_name, points=points)
        return len(points)

    @classmethod
    def find_by(cls, field: str, value: str, limit: int = 100) -> list:
        cls.ensure_collection()
        results, _ = cls._client().scroll(
            collection_name=cls.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key=field, match=MatchValue(value=value))]
            ),
            limit=limit,
        )
        return [cls.from_payload(p.payload) for p in results]

    @classmethod
    def exists(cls, field: str, value: str) -> bool:
        cls.ensure_collection()
        results, _ = cls._client().scroll(
            collection_name=cls.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key=field, match=MatchValue(value=value))]
            ),
            limit=1,
        )
        return len(results) > 0

    @classmethod
    def search(cls, query: str, limit: int = 10) -> list:
        cls.ensure_collection()
        vector = cls._embed_static(query)
        results = cls._client().query_points(
            collection_name=cls.collection_name,
            query=vector,
            limit=limit,
        )
        return [cls.from_payload(hit.payload) for hit in results.points]

    @classmethod
    def find_recent(cls, timestamp_field: str, hours: int = 24, limit: int = 1000) -> list:
        cls.ensure_collection()
        import datetime
        cutoff = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            - datetime.timedelta(hours=hours)
        ).isoformat()
        results, _ = cls._client().scroll(
            collection_name=cls.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key=timestamp_field, range=Range(gte=cutoff))]
            ),
            limit=limit,
        )
        return [cls.from_payload(p.payload) for p in results]

    @classmethod
    def from_payload(cls, payload: dict):
        raise NotImplementedError

    def _generate_id(self) -> str:
        key = getattr(self, "id", str(uuid.uuid4()))
        return str(uuid.uuid5(uuid.NAMESPACE_URL, str(key)))

    def _embed(self, text: str) -> list[float]:
        return self._embed_static(text)

    @classmethod
    def _embed_static(cls, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        vector = []
        for i in range(0, cls.vector_size * 2, 2):
            idx = i % len(h)
            vector.append((int(h[idx:idx + 2], 16) - 128) / 128.0)
        return vector
