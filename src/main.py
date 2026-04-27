import os
import sys
from fastapi import FastAPI
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
from routes import scrape_router, reports_router, search_router, health_router

app = FastAPI(
    title="PulseScout",
    description="Social Knowledge Doomscroll Agent — monitors YouTube & HackerNews for market insights, trends, and sentiment",
    version="1.0.0",
)

app.include_router(scrape_router, prefix="/scrape", tags=["Scrape"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(health_router, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
