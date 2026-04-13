import datetime
import requests

from config import scraper_config, scraper_urls, KEY_DEFAULTS, URL_DEFAULTS


class Scrapper:
    def __init__(self):
        self.devto_key = KEY_DEFAULTS["devto_key"]

        self.hn_api_url = URL_DEFAULTS["hn_api_url"]
        self.devto_api_url = URL_DEFAULTS["devto_api_url"]

        self.devto_headers = {}
        if self.devto_key:
            self.devto_headers["api-key"] = self.devto_key

    def _fetch_devto_comments(self, article_id: int, limit: int = 5) -> list[str]:
        try:
            resp = requests.get(
                f"{self.devto_api_url}/comments",
                params={"a_id": article_id},
                headers=self.devto_headers,
                timeout=10,
            )
            resp.raise_for_status()
            comments_data = resp.json()
            return [
                (c.get("body_html") or c.get("body") or "")[:500]
                for c in comments_data[:limit]
            ]
        except Exception:
            return []

    @scraper_urls
    @scraper_config
    def scrap_devto(self, tag: str = None, limit: int = 100,
                    num_comments: int = 5, timeout: int = 15,
                    max_text_length: int = 2000, devto_per_page: int = 30,
                    devto_api_url: str = None, **_):
        posts = []
        params = {"per_page": min(limit, devto_per_page), "page": 1}
        if tag:
            params["tag"] = tag

        fetched = 0
        while fetched < limit:
            resp = requests.get(
                f"{devto_api_url}/articles",
                params=params,
                headers=self.devto_headers,
                timeout=timeout,
            )
            resp.raise_for_status()
            articles = resp.json()
            if not articles:
                break

            for article in articles:
                comments = self._fetch_devto_comments(article["id"], num_comments)

                posts.append({
                    "id": str(article["id"]),
                    "title": article.get("title", ""),
                    "text": (article.get("description") or "")[:max_text_length],
                    "comments": comments,
                    "score": article.get("positive_reactions_count", 0),
                    "timestamp": article.get("published_at", ""),
                    "source": "devto",
                    "subreddit": tag or "",
                })
                fetched += 1
                if fetched >= limit:
                    break

            params["page"] += 1

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
