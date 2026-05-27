from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Any
import random
import asyncio


@dataclass
class ScrapeRequest:
    hotel_id: str
    check_in: date
    check_out: date
    guests: int = 2


@dataclass
class ScrapeResult:
    hotel_id: str
    source: str
    success: bool
    price: Optional[float] = None
    currency: str = "BRL"
    room_name: Optional[str] = None
    breakfast_included: Optional[bool] = None
    cancellation_policy: Optional[str] = None
    availability: Optional[bool] = None
    raw_data: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


async def random_delay(min_s: float = 2.0, max_s: float = 5.0) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


class BaseScraper(ABC):
    source: str = ""

    @abstractmethod
    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        pass

    async def safe_scrape(self, request: ScrapeRequest) -> ScrapeResult:
        try:
            return await self.scrape(request)
        except Exception as exc:
            return ScrapeResult(
                hotel_id=request.hotel_id,
                source=self.source,
                success=False,
                error=str(exc),
            )
