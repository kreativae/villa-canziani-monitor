"""
Omnibees booking engine scraper.
Omnibees uses a REST JSON API under /Services/GetHotelsAvailability.
"""
from __future__ import annotations
import httpx
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult, random_delay


class OmnibeeScraper(BaseScraper):
    source = "official"

    def __init__(self, official_url: str):
        self.official_url = official_url

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        await random_delay(1.5, 3.5)

        # Omnibees sites embed a hotel code in the URL path
        # e.g. https://be.omnibees.com/hoteldetails.aspx?sid=XXXXX
        params = {
            "checkin": request.check_in.strftime("%Y-%m-%d"),
            "checkout": request.check_out.strftime("%Y-%m-%d"),
            "adult": request.guests,
            "child": 0,
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                resp = await client.get(self.official_url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error=str(exc),
            )

        price = _cheapest_price(data)
        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=price is not None,
            raw_data=data if isinstance(data, dict) else {},
        )


def _cheapest_price(data: dict) -> float | None:
    try:
        rooms = data.get("Rooms") or data.get("rooms") or []
        prices = []
        for room in rooms:
            rate = room.get("MinRate") or room.get("rate") or room.get("Price")
            if rate:
                prices.append(float(rate))
        return min(prices) if prices else None
    except Exception:
        return None
