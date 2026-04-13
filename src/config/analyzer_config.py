import os
from functools import wraps

ANALYZER_METHOD_DEFAULTS = {
    "timeout": 120,
    "max_post_length": 800,
}

ANALYZER_KEY_DEFAULTS = {
    "api_key": os.getenv("OLLAMA_KEY"),
}

ANALYZER_URL_DEFAULTS = {
    "base_url": os.getenv("OLLAMA_URI") or "https://ollama.com",
}

ANALYZER_MODEL_DEFAULTS = {
    "model": os.getenv("OLLAMA_MODEL") or "gemma3:12b",
}


def analyzer_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for key, default in ANALYZER_METHOD_DEFAULTS.items():
            if key in func.__code__.co_varnames and key not in kwargs:
                kwargs.setdefault(key, default)
        return func(*args, **kwargs)
    return wrapper


def analyzer_keys(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for key, default in ANALYZER_KEY_DEFAULTS.items():
            if key not in kwargs:
                kwargs.setdefault(key, getattr(self, key, default))
        return func(self, *args, **kwargs)
    return wrapper


def analyzer_urls(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for key, default in ANALYZER_URL_DEFAULTS.items():
            if key not in kwargs:
                kwargs.setdefault(key, getattr(self, key, default))
        return func(self, *args, **kwargs)
    return wrapper
