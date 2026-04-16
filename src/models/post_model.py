from .base_model import BaseModel


class PostModel(BaseModel):
    collection_name = "posts"
    indexed_fields = ["post_id", "batch_id", "timestamp"]

    def __init__(self, id: str = "", title: str = "", text: str = "",
                 score: int = 0, timestamp: str = "", source: str = "",
                 subreddit: str = "", batch_id: str = "", comments: list = None):
        self.id = id
        self.title = title
        self.text = text
        self.score = score
        self.timestamp = timestamp
        self.source = source
        self.subreddit = subreddit
        self.batch_id = batch_id
        self.comments = comments or []

    def to_payload(self) -> dict:
        return {
            "post_id": self.id,
            "title": self.title,
            "text": self.text,
            "score": self.score,
            "timestamp": self.timestamp,
            "source": self.source,
            "subreddit": self.subreddit,
            "batch_id": self.batch_id,
            "document": self.to_document(),
        }

    def to_document(self) -> str:
        parts = [self.title]
        if self.text:
            parts.append(self.text)
        if self.comments:
            parts.append("Comments: " + " | ".join(self.comments))
        return "\n".join(parts)

    @classmethod
    def from_payload(cls, payload: dict):
        return cls(
            id=payload.get("post_id", ""),
            title=payload.get("title", ""),
            text=payload.get("text", ""),
            score=payload.get("score", 0),
            timestamp=payload.get("timestamp", ""),
            source=payload.get("source", ""),
            subreddit=payload.get("subreddit", ""),
            batch_id=payload.get("batch_id", ""),
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            text=data.get("text", ""),
            score=data.get("score", 0),
            timestamp=data.get("timestamp", ""),
            source=data.get("source", ""),
            subreddit=data.get("subreddit", ""),
            batch_id=data.get("batch_id", ""),
            comments=data.get("comments", []),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "document": self.to_document(),
            "score": self.score,
            "timestamp": self.timestamp,
            "source": self.source,
            "subreddit": self.subreddit,
            "batch_id": self.batch_id,
        }
