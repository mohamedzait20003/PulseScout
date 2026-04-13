from models import PostModel


class ReportsController:
    def list_reports(self, max_count: int = 20) -> dict:
        posts = PostModel.find_recent("timestamp", hours=24 * 30)
        return {"count": len(posts[:max_count]), "posts": [p.to_dict() for p in posts[:max_count]]}

    def get_latest(self) -> dict:
        posts = PostModel.find_recent("timestamp", hours=24)
        if not posts:
            return {"error": "No recent posts found"}
        return {"count": len(posts), "posts": [p.to_dict() for p in posts]}
