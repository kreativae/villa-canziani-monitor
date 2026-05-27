from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str  # service role key (bypasses RLS)
    supabase_anon_key: str

    # Scraper settings
    scraper_check_in_offset_days: int = 7   # days from today
    scraper_check_out_offset_days: int = 8  # +1 night default
    scraper_default_guests: int = 2
    scraper_request_delay_min: float = 2.0  # seconds
    scraper_request_delay_max: float = 5.0

    # Playwright
    playwright_headless: bool = True
    playwright_timeout_ms: int = 30_000

    cors_origins: list[str] = ["http://localhost:3000", "https://*.vercel.app"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
