"""
Orchestrates scraping runs: fetches hotel list, dispatches scrapers in
parallel (with concurrency limit), persists results to Supabase.
"""
import asyncio
from datetime import date, timedelta
from typing import Optional
from supabase import Client

from app.config import get_settings
from app.scrapers.booking import BookingScraper
from app.scrapers.official import get_official_scraper
from app.scrapers.base import ScrapeRequest, ScrapeResult


settings = get_settings()
_CONCURRENCY = 4  # max parallel scrapers


async def run_scrape(
    db: Client,
    hotel_id: Optional[str] = None,
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    guests: int = 2,
) -> str:
    """Start a scrape job. Returns job ID."""
    if check_in is None:
        check_in = date.today() + timedelta(days=settings.scraper_check_in_offset_days)
    if check_out is None:
        check_out = check_in + timedelta(days=1)

    # Fetch hotels to scrape
    query = db.table("hotels").select("*").eq("active", True)
    if hotel_id:
        query = query.eq("id", hotel_id)
    hotels = query.execute().data

    # Create job record
    job_row = db.table("scrape_jobs").insert({
        "hotel_id": hotel_id,
        "triggered_by": "manual",
        "status": "running",
        "hotels_total": len(hotels),
        "started_at": "now()",
    }).execute().data[0]
    job_id = job_row["id"]

    # Run in background so endpoint returns immediately
    asyncio.create_task(
        _execute_job(db, job_id, hotels, check_in, check_out, guests)
    )
    return job_id


async def _execute_job(
    db: Client,
    job_id: str,
    hotels: list[dict],
    check_in: date,
    check_out: date,
    guests: int,
) -> None:
    semaphore = asyncio.Semaphore(_CONCURRENCY)
    done = 0
    failed = 0
    errors: list[dict] = []

    async def scrape_hotel(hotel: dict):
        nonlocal done, failed
        async with semaphore:
            results = await _scrape_one(hotel, check_in, check_out, guests)
            snapshots = []
            for r in results:
                if r.success:
                    snapshots.append(_result_to_snapshot(r, hotel["id"], check_in, check_out, guests))
                else:
                    errors.append({"hotel": hotel["name"], "source": r.source, "error": r.error})

            if snapshots:
                db.table("price_snapshots").insert(snapshots).execute()
                done += 1
            else:
                failed += 1

    await asyncio.gather(*[scrape_hotel(h) for h in hotels])

    db.table("scrape_jobs").update({
        "status": "completed",
        "hotels_done": done,
        "hotels_failed": failed,
        "error_log": errors or None,
        "completed_at": "now()",
    }).eq("id", job_id).execute()


async def _scrape_one(
    hotel: dict, check_in: date, check_out: date, guests: int
) -> list[ScrapeResult]:
    req = ScrapeRequest(
        hotel_id=hotel["id"],
        check_in=check_in,
        check_out=check_out,
        guests=guests,
    )
    tasks = []

    if hotel.get("official_url"):
        scraper = get_official_scraper(hotel)
        tasks.append(scraper.safe_scrape(req))

    if hotel.get("booking_url"):
        booking = BookingScraper(hotel["booking_url"])
        tasks.append(booking.safe_scrape(req))

    return list(await asyncio.gather(*tasks)) if tasks else []


def _result_to_snapshot(r: ScrapeResult, hotel_id: str, check_in: date, check_out: date, guests: int) -> dict:
    return {
        "hotel_id": hotel_id,
        "source": r.source,
        "price": r.price,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "guests": guests,
        "breakfast_included": r.breakfast_included,
        "cancellation_policy": r.cancellation_policy,
        "availability": r.availability,
        "raw_data": r.raw_data,
    }
