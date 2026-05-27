"""
Generic fallback scraper: loads the official URL and tries common price
patterns. Works for many simple hotel sites; override with a dedicated
engine scraper when needed.
"""
from __future__ import annotations
import re
import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult, random_user_agent, random_delay


class GenericScraper(BaseScraper):
    source = "official"

    def __init__(self, official_url: str):
        self.official_url = official_url

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        if not self.official_url:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error="No official URL configured",
            )

        await random_delay(1.5, 3.0)

        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": random_user_agent()},
                follow_redirects=True,
                timeout=20,
            ) as client:
                resp = await client.get(self.official_url)
                resp.raise_for_status()
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error=str(exc),
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        price = _extract_price(soup)

        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=price is not None,
            raw_data={"url": self.official_url, "status_code": resp.status_code},
        )


_BRL_PATTERN = re.compile(r"R\$\s*([\d\.]+(?:,\d{2})?)")


def _extract_price(soup: BeautifulSoup) -> float | None:
    """Best-effort price extraction from arbitrary hotel HTML."""
    # Try meta tags first (structured data)
    for meta in soup.find_all("meta", {"property": ["og:price:amount", "product:price:amount"]}):
        val = meta.get("content", "")
        try:
            return float(val)
        except ValueError:
            pass

    # JSON-LD
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        import json
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                price = (
                    data.get("priceRange")
                    or data.get("offers", {}).get("price")
                )
                if price:
                    cleaned = re.sub(r"[^\d,.]", "", str(price))
                    return float(cleaned.replace(",", ".")) if cleaned else None
        except Exception:
            pass

    # Inline R$ pattern
    text = soup.get_text(" ")
    matches = _BRL_PATTERN.findall(text)
    for m in matches:
        try:
            val = float(m.replace(".", "").replace(",", "."))
            if 50 < val < 50_000:   # sanity-check price range
                return val
        except ValueError:
            pass

    return None
