from .scrape_routes import router as scrape_router
from .reports_routes import router as reports_router
from .search_routes import router as search_router
from .health_routes import router as health_router

__all__ = [
    "scrape_router",
    "reports_router",
    "search_router",
    "health_router",
]
