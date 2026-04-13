from models import PostModel


class SearchController:
    def search(self, query: str, n: int = 10) -> dict:
        posts = PostModel.search(query, limit=n)
        return {"query": query, "count": len(posts), "results": [p.to_dict() for p in posts]}
