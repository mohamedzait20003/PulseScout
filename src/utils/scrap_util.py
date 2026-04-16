import datetime
import requests

from config import scraper_config, scraper_urls, KEY_DEFAULTS, URL_DEFAULTS


class Scrapper:
    def __init__(self):
        self.youtube_key = KEY_DEFAULTS["youtube_key"]
        self.youtube_api_url = URL_DEFAULTS["youtube_api_url"]
        self.hn_api_url = URL_DEFAULTS["hn_api_url"]

    def _fetch_youtube_comments(self, video_id: str, limit: int = 5) -> list[str]:
        try:
            resp = requests.get(
                f"{self.youtube_api_url}/commentThreads",
                params={
                    "part": "snippet",
                    "videoId": video_id,
                    "maxResults": limit,
                    "order": "relevance",
                    "key": self.youtube_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            return [
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"][:500]
                for item in items
            ]
        except Exception:
            return []

    @scraper_urls
    @scraper_config
    def scrap_youtube(self, tag: str = None, limit: int = 25,
                      num_comments: int = 5, timeout: int = 15,
                      max_text_length: int = 2000,
                      youtube_api_url: str = None, **_):
        posts = []

        search_resp = requests.get(
            f"{youtube_api_url}/search",
            params={
                "part": "snippet",
                "q": tag or "trending",
                "type": "video",
                "order": "relevance",
                "maxResults": min(limit, 50),
                "key": self.youtube_key,
            },
            timeout=timeout,
        )
        search_resp.raise_for_status()
        search_items = search_resp.json().get("items", [])

        # Get video statistics in bulk
        video_ids = [item["id"]["videoId"] for item in search_items]
        stats = {}
        if video_ids:
            stats_resp = requests.get(
                f"{youtube_api_url}/videos",
                params={
                    "part": "statistics",
                    "id": ",".join(video_ids),
                    "key": self.youtube_key,
                },
                timeout=timeout,
            )
            stats_resp.raise_for_status()
            for item in stats_resp.json().get("items", []):
                stats[item["id"]] = item.get("statistics", {})

        for item in search_items:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            video_stats = stats.get(video_id, {})

            comments = self._fetch_youtube_comments(video_id, num_comments)

            posts.append({
                "id": video_id,
                "title": snippet.get("title", ""),
                "text": (snippet.get("description") or "")[:max_text_length],
                "comments": comments,
                "score": int(video_stats.get("viewCount", 0)),
                "timestamp": snippet.get("publishedAt", ""),
                "source": "youtube",
                "subreddit": tag or "",
            })

        return posts

    @scraper_urls
    @scraper_config
    def scrap_hackernews(self, limit: int = 100, num_comments: int = 5,
                         timeout: int = 15, comment_timeout: int = 10,
                         max_text_length: int = 2000,
                         max_comment_length: int = 500,
                         hn_api_url: str = None, **_):
        posts = []
        ids = requests.get(
            f"{hn_api_url}/topstories.json",
            timeout=timeout,
        ).json()[:limit]

        for item_id in ids:
            item = requests.get(
                f"{hn_api_url}/item/{item_id}.json",
                timeout=timeout,
            ).json()
            if not item:
                continue

            comments = []
            for kid_id in (item.get("kids") or [])[:num_comments]:
                kid = requests.get(
                    f"{hn_api_url}/item/{kid_id}.json",
                    timeout=comment_timeout,
                ).json()
                if kid and kid.get("text"):
                    comments.append(kid["text"][:max_comment_length])

            posts.append({
                "id": str(item.get("id")),
                "title": item.get("title", ""),
                "text": (item.get("text") or "")[:max_text_length],
                "comments": comments,
                "score": item.get("score", 0),
                "timestamp": datetime.datetime.fromtimestamp(
                    item.get("time", 0), tz=datetime.timezone.utc
                ).isoformat(),
                "source": "hackernews",
                "subreddit": "",
            })

        return posts
