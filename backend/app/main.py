from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import hotels, prices, scraper

settings = get_settings()

app = FastAPI(
    title="Villa Canziani & Donato — Hotel Monitor API",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels.router)
app.include_router(prices.router)
app.include_router(scraper.router)


@app.get("/health")
def health():
    return {"status": "ok"}
