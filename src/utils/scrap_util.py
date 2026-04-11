import praw
import datetime
import requests

class Scrapper:
    def __init__(self, client_id: str, client_secret: str, user_agent: str = "PulseScout/1.0"):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

    def scrap_reddit(self, subreddit_name: str, limit: int = 100,
                     time_filter: str = "hot", num_comments: int = 5):
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)

        if time_filter == "hot":
            submissions = subreddit.hot(limit=limit)
        elif time_filter == "new":
            submissions = subreddit.new(limit=limit)
        else:
            submissions = subreddit.top(limit=limit, time_filter=time_filter)

        for submission in submissions:
            submission.comment_sort = "best"
            submission.comments.replace_more(limit=0)
            top_comments = [c.body for c in submission.comments[:num_comments]]

            posts.append({
                "id": submission.id,
                "title": submission.title,
                "text": (submission.selftext or "")[:2000],
                "comments": top_comments,
                "score": submission.score,
                "timestamp": datetime.datetime.fromtimestamp(
                    submission.created_utc, tz=datetime.timezone.utc
                ).isoformat(),
                "source": "reddit",
                "subreddit": subreddit_name,
            })

        return posts

    def scrap_hackernews(self, limit: int = 100, num_comments: int = 5):
        posts = []
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=15,
        ).json()[:limit]

        for item_id in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                timeout=15,
            ).json()
            if not item:
                continue

            comments = []
            for kid_id in (item.get("kids") or [])[:num_comments]:
                kid = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{kid_id}.json",
                    timeout=10,
                ).json()
                if kid and kid.get("text"):
                    comments.append(kid["text"][:500])

            posts.append({
                "id": str(item.get("id")),
                "title": item.get("title", ""),
                "text": (item.get("text") or "")[:2000],
                "comments": comments,
                "score": item.get("score", 0),
                "timestamp": datetime.datetime.fromtimestamp(
                    item.get("time", 0), tz=datetime.timezone.utc
                ).isoformat(),
                "source": "hackernews",
                "subreddit": "",
            })

        return posts
