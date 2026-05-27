from fastapi import APIRouter, Depends, BackgroundTasks
from supabase import Client
from app.database import get_db
from app.schemas.scrape_job import ScrapeJob
from app.services.scraper_service import run_scrape
from datetime import date
from typing import Optional

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run", status_code=202)
async def trigger_scrape(
    hotel_id: Optional[str] = None,
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    guests: int = 2,
    db: Client = Depends(get_db),
):
    """Trigger a scrape run. Returns job ID immediately; runs in background."""
    job_id = await run_scrape(db, hotel_id, check_in, check_out, guests)
    return {"job_id": job_id, "status": "running"}


@router.get("/jobs", response_model=list[ScrapeJob])
async def list_jobs(limit: int = 20, db: Client = Depends(get_db)):
    return (
        db.table("scrape_jobs")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )


@router.get("/jobs/{job_id}", response_model=ScrapeJob)
async def get_job(job_id: str, db: Client = Depends(get_db)):
    result = db.table("scrape_jobs").select("*").eq("id", job_id).single().execute()
    return result.data
