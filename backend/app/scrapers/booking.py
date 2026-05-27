"""
Booking.com scraper using Playwright stealth mode.
Booking.com uses Cloudflare + fingerprinting — we rotate UA, add human-like
delays, and avoid obvious bot signals.
"""
from __future__ import annotations
import re
from playwright.async_api import async_playwright, Page
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
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error="No booking URL configured",
            )

        check_in_str = request.check_in.strftime("%Y-%m-%d")
        check_out_str = request.check_out.strftime("%Y-%m-%d")

        url = (
            f"{self.booking_url}"
            f"?checkin={check_in_str}"
            f"&checkout={check_out_str}"
            f"&group_adults={request.guests}"
            f"&no_rooms=1"
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.settings.playwright_headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            context = await browser.new_context(
                user_agent=random_user_agent(),
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
                timezone_id="America/Maceio",
                extra_http_headers={
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                },
            )

            # Mask webdriver property
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)

            page = await context.new_page()
            try:
                result = await self._extract(page, url, request)
            finally:
                await browser.close()

        return result

    async def _extract(self, page: Page, url: str, request: ScrapeRequest) -> ScrapeResult:
        await page.goto(url, wait_until="domcontentloaded",
                        timeout=self.settings.playwright_timeout_ms)
        await random_delay(2.0, 4.0)

        # Dismiss cookie banner if present
        try:
            await page.click('[id*="onetrust-accept"]', timeout=3000)
            await random_delay(0.5, 1.5)
        except Exception:
            pass

        # Wait for room list
        try:
            await page.wait_for_selector('[data-testid="recommended-units"]', timeout=10000)
        except Exception:
            # Page may not have loaded or property not available for dates
            availability = await self._check_no_availability(page)
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=True,
                availability=not availability,
                price=None,
                raw_data={"url": url},
            )

        # Extract cheapest room price
        price, room_name, breakfast, cancel = await self._parse_rooms(page)

        return ScrapeResult(
            hotel_id=request.hotel_id,
            source=self.source,
            success=True,
            price=price,
            room_name=room_name,
            breakfast_included=breakfast,
            cancellation_policy=cancel,
            availability=price is not None,
            raw_data={"url": url},
        )

    async def _parse_rooms(self, page: Page):
        price = None
        room_name = None
        breakfast = None
        cancel = None

        try:
            # Grab first (cheapest) room block
            room = page.locator('[data-testid="recommended-units"] [data-testid="property-unit"]').first
            room_name_el = room.locator('[data-testid="recommended-unit-title"]')
            if await room_name_el.count():
                room_name = await room_name_el.inner_text()

            # Price — Booking renders it as "R$ 1.234" or "BRL 1,234"
            price_el = room.locator('[data-testid="price-and-discounted-price"]')
            if await price_el.count():
                raw_price = await price_el.inner_text()
                price = _parse_brl(raw_price)

            # Breakfast
            try:
                breakfast_el = room.locator(':text("café da manhã"), :text("breakfast")')
                breakfast = await breakfast_el.count() > 0
            except Exception:
                pass

            # Cancellation
            try:
                cancel_el = room.locator(':text("cancelamento"), :text("cancellation")')
                if await cancel_el.count():
                    cancel = await cancel_el.first.inner_text()
            except Exception:
                pass
        except Exception:
            pass

        return price, room_name, breakfast, cancel

    async def _check_no_availability(self, page: Page) -> bool:
        text = await page.inner_text("body")
        no_avail_phrases = [
            "não está disponível",
            "not available",
            "fully booked",
            "esgotado",
        ]
        return any(p in text.lower() for p in no_avail_phrases)


def _parse_brl(text: str) -> float | None:
    """Parse 'R$ 1.234,00' or 'BRL 1,234.00' to float."""
    digits = re.sub(r"[^\d,.]", "", text)
    # Handle Brazilian format: 1.234,00
    if re.search(r"\d{1,3}\.\d{3},\d{2}$", digits):
        digits = digits.replace(".", "").replace(",", ".")
    elif "," in digits and "." not in digits:
        digits = digits.replace(",", ".")
    elif "," in digits:
        digits = digits.replace(",", "")
    try:
        return float(digits)
    except (ValueError, TypeError):
        return None
