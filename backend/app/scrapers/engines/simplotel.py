"""
Simplotel booking engine scraper.
Simplotel exposes a REST endpoint at /api/v1/availability.
"""
from __future__ import annotations
import httpx
from urllib.parse import urlparse
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult, random_delay


class SimplotelScraper(BaseScraper):
    source = "official"

    def __init__(self, official_url: str):
        self.official_url = official_url

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        await random_delay(1.5, 3.5)

        parsed = urlparse(self.official_url)
        api_base = f"{parsed.scheme}://{parsed.netloc}"

        params = {
            "check_in": request.check_in.isoformat(),
            "check_out": request.check_out.isoformat(),
            "adults": request.guests,
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                resp = await client.get(
                    f"{api_base}/api/v1/availability",
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error=str(exc),
            )

        price = _cheapest(data)
        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=price is not None,
            raw_data=data if isinstance(data, dict) else {},
        )


def _cheapest(data) -> float | None:
    try:
        rooms = data.get("rooms", []) or data.get("data", {}).get("rooms", [])
        prices = [float(r["price"]) for r in rooms if r.get("price")]
        return min(prices) if prices else None
    except Exception:
        return None
