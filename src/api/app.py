from fastapi import FastAPI

from ..routes import scrape_router, reports_router, search_router, health_router

app = FastAPI(
    title="PulseScout",
    description="Social Knowledge Doomscroll Agent — monitors DEV.to & HackerNews for trends and insights",
    version="1.0.0",
)

app.include_router(scrape_router, prefix="/scrape", tags=["Scrape"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(health_router, tags=["Health"])
