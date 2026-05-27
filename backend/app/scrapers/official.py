"""
Dispatcher for official hotel site scrapers.
Routes to the correct engine based on hotel.engine field.
"""
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult
from app.scrapers.engines.omnibees import OmnibeeScraper
from app.scrapers.engines.cloudbeds import CloudbedsScraper
from app.scrapers.engines.simplotel import SimplotelScraper
from app.scrapers.engines.generic import GenericScraper


ENGINE_MAP: dict[str, type[BaseScraper]] = {
    "omnibees": OmnibeeScraper,
    "cloudbeds": CloudbedsScraper,
    "simplotel": SimplotelScraper,
}


def get_official_scraper(hotel: dict) -> BaseScraper:
    engine = (hotel.get("engine") or "generic").lower()
    cls = ENGINE_MAP.get(engine, GenericScraper)
    return cls(official_url=hotel.get("official_url") or "")
