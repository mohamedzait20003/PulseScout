import chromadb
import datetime

class Storage:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="social_posts",
            metadata={"hnsw:space": "cosine"},
        )

    def add_posts(self, posts: list[dict], batch_id: str) -> int:
        added = 0
        for post in posts:
            if self.post_exists(post["id"]):
                continue

            document = self._build_document(post)
            metadata = {
                "post_id": post["id"],
                "title": post["title"],
                "score": post["score"],
                "timestamp": post["timestamp"],
                "source": post["source"],
                "subreddit": post.get("subreddit", ""),
                "batch_id": batch_id,
            }

            self.collection.add(
                ids=[post["id"]],
                documents=[document],
                metadatas=[metadata],
            )
            added += 1

        return added

    def post_exists(self, post_id: str) -> bool:
        results = self.collection.get(ids=[post_id])
        return len(results["ids"]) > 0

    def query_similar(self, query: str, n: int = 10) -> list[dict]:
        results = self.collection.query(query_texts=[query], n_results=n)
        return self._unpack_results(results)

    def get_batch(self, batch_id: str) -> list[dict]:
        results = self.collection.get(
            where={"batch_id": batch_id},
            include=["documents", "metadatas"],
        )
        return self._unpack_get(results)

    def get_recent(self, hours: int = 24) -> list[dict]:
        cutoff = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            - datetime.timedelta(hours=hours)
        ).isoformat()
        results = self.collection.get(
            where={"timestamp": {"$gte": cutoff}},
            include=["documents", "metadatas"],
        )
        return self._unpack_get(results)

    def _build_document(self, post: dict) -> str:
        parts = [post["title"]]
        if post.get("text"):
            parts.append(post["text"])
        if post.get("comments"):
            parts.append("Comments: " + " | ".join(post["comments"]))
        return "\n".join(parts)

    def _unpack_results(self, results: dict) -> list[dict]:
        items = []
        for i, doc_id in enumerate(results["ids"][0]):
            items.append({
                "id": doc_id,
                "document": results["documents"][0][i],
                **results["metadatas"][0][i],
            })
        return items

    def _unpack_get(self, results: dict) -> list[dict]:
        items = []
        for i, doc_id in enumerate(results["ids"]):
            item = {"id": doc_id, "document": results["documents"][i]}
            item.update(results["metadatas"][i])
            items.append(item)
        return items
