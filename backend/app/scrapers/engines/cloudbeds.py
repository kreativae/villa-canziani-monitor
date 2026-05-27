"""
Cloudbeds booking engine scraper.
Cloudbeds exposes a public availability widget endpoint.
"""
from __future__ import annotations
import httpx
import re
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult, random_delay


class CloudbedsScraper(BaseScraper):
    source = "official"

    def __init__(self, official_url: str):
        self.official_url = official_url

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        await random_delay(1.5, 3.5)

        # Cloudbeds widget URL pattern: https://hotels.cloudbeds.com/reservation/XXXXXXX
        params = {
            "checkin": request.check_in.strftime("%m/%d/%Y"),
            "checkout": request.check_out.strftime("%m/%d/%Y"),
            "adults": request.guests,
            "children": 0,
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                resp = await client.get(self.official_url, params=params)
                resp.raise_for_status()
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error=str(exc),
            )

        # Cloudbeds returns HTML; price is embedded in page
        price = _parse_price_from_html(resp.text)
        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=price is not None,
            raw_data={"url": self.official_url},
        )


_PRICE_RE = re.compile(r'"price":\s*([\d.]+)')


def _parse_price_from_html(html: str) -> float | None:
    matches = _PRICE_RE.findall(html)
    prices = []
    for m in matches:
        try:
            v = float(m)
            if 50 < v < 50_000:
                prices.append(v)
        except ValueError:
            pass
    return min(prices) if prices else None
