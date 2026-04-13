import os
from functools import wraps

METHOD_DEFAULTS = {
    "limit": 100,
    "num_comments": 5,
    "timeout": 15,
    "comment_timeout": 10,
    "max_text_length": 2000,
    "max_comment_length": 500,
    "devto_per_page": 30,
}

KEY_DEFAULTS = {
    "devto_key": os.getenv("DEV_TO_KEY"),
}

URL_DEFAULTS = {
    "devto_api_url": os.getenv("DEV_TO_URI") or "https://dev.to/api",
    "hn_api_url": os.getenv("HN_API_URI") or "https://hacker-news.firebaseio.com/v0",
}


def scraper_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for key, default in METHOD_DEFAULTS.items():
            if key in func.__code__.co_varnames and key not in kwargs:
                kwargs.setdefault(key, default)
        return func(*args, **kwargs)
    return wrapper


def scraper_keys(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for key, default in KEY_DEFAULTS.items():
            if key not in kwargs:
                kwargs.setdefault(key, getattr(self, key, default))
        return func(self, *args, **kwargs)
    return wrapper


def scraper_urls(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for key, default in URL_DEFAULTS.items():
            if key not in kwargs:
                kwargs.setdefault(key, getattr(self, key, default))
        return func(self, *args, **kwargs)
    return wrapper
