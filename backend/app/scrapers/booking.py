"""
Booking.com scraper.

Modo padrão: httpx com headers realistas — funciona para dados básicos.
Modo Playwright: ativado via variável PLAYWRIGHT_ENABLED=true (ambiente local/premium).
"""
from __future__ import annotations
import re
import httpx
from app.scrapers.base import BaseScraper, ScrapeRequest, ScrapeResult, random_user_agent, random_delay
from app.config import get_settings


class BookingScraper(BaseScraper):
    source = "booking"

    def __init__(self, booking_url: str):
        self.booking_url = booking_url
        self.settings = get_settings()

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        if not self.booking_url:
            return ScrapeResult(
                hotel_id=request.hotel_id, source=self.source,
                success=False, error="No booking URL configured",
            )

        if self.settings.playwright_enabled:
            return await self._scrape_playwright(request)
        return await self._scrape_httpx(request)

    async def _scrape_httpx(self, request: ScrapeRequest) -> ScrapeResult:
        """Scraping leve via httpx — sem Chromium."""
        await random_delay(
            self.settings.scraper_request_delay_min,
            self.settings.scraper_request_delay_max,
        )

        check_in = request.check_in.strftime("%Y-%m-%d")
        check_out = request.check_out.strftime("%Y-%m-%d")
        url = (
            f"{self.booking_url}"
            f"?checkin={check_in}&checkout={check_out}"
            f"&group_adults={request.guests}&no_rooms=1"
        )

        headers = {
            "User-Agent": random_user_agent(),
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.booking.com/",
        }

        try:
            async with httpx.AsyncClient(
                headers=headers, follow_redirects=True, timeout=20
            ) as client:
                resp = await client.get(url)
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id, source=self.source,
                success=False, error=str(exc),
            )

        price = _parse_price_from_html(resp.text)
        available = resp.status_code == 200 and "sold out" not in resp.text.lower()

        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=available and price is not None,
            raw_data={"url": url, "status": resp.status_code, "mode": "httpx"},
        )

    async def _scrape_playwright(self, request: ScrapeRequest) -> ScrapeResult:
        """Scraping completo com Chromium headless (requer playwright instalado)."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return await self._scrape_httpx(request)

        check_in = request.check_in.strftime("%Y-%m-%d")
        check_out = request.check_out.strftime("%Y-%m-%d")
        url = (
            f"{self.booking_url}"
            f"?checkin={check_in}&checkout={check_out}"
            f"&group_adults={request.guests}&no_rooms=1"
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = await browser.new_context(
                user_agent=random_user_agent(),
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
            )
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )
            page = await context.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                await random_delay(2, 4)
                try:
                    await page.click('[id*="onetrust-accept"]', timeout=3000)
                except Exception:
                    pass
                html = await page.content()
                price = _parse_price_from_html(html)
            finally:
                await browser.close()

        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            availability=price is not None,
            raw_data={"url": url, "mode": "playwright"},
        )


_BRL_RE = re.compile(r"R\$\s*[\d\.,]+")


def _parse_price_from_html(html: str) -> float | None:
    matches = _BRL_RE.findall(html)
    prices = []
    for m in matches:
        digits = re.sub(r"[^\d,.]", "", m)
        if re.search(r"\d{1,3}\.\d{3},\d{2}$", digits):
            digits = digits.replace(".", "").replace(",", ".")
        elif "," in digits and "." not in digits:
            digits = digits.replace(",", ".")
        try:
            v = float(digits)
            if 50 < v < 50_000:
                prices.append(v)
        except ValueError:
            pass
    return min(prices) if prices else None
