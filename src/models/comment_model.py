from .base_model import BaseModel


class CommentModel(BaseModel):
    collection_name = "comments"

    def __init__(self, id: str = "", post_id: str = "", body: str = "",
                 source: str = "", timestamp: str = ""):
        self.id = id
        self.post_id = post_id
        self.body = body
        self.source = source
        self.timestamp = timestamp

    def to_payload(self) -> dict:
        return {
            "comment_id": self.id,
            "post_id": self.post_id,
            "body": self.body,
            "source": self.source,
            "timestamp": self.timestamp,
        }

    def to_document(self) -> str:
        return self.body

    @classmethod
    def from_payload(cls, payload: dict):
        return cls(
            id=payload.get("comment_id", ""),
            post_id=payload.get("post_id", ""),
            body=payload.get("body", ""),
            source=payload.get("source", ""),
            timestamp=payload.get("timestamp", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "body": self.body,
            "source": self.source,
            "timestamp": self.timestamp,
        }
