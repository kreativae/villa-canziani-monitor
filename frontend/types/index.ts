export interface Hotel {
  id: string;
  name: string;
  official_url?: string;
  booking_url?: string;
  booking_id?: string;
  category?: string;
  region: string;
  notes?: string;
  engine?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
  // enriched fields
  latest_official_price?: number;
  latest_booking_price?: number;
  price_diff_pct?: number;
  last_scraped_at?: string;
}

export interface PriceSnapshot {
  id: string;
  hotel_id: string;
  room_type_id?: string;
  source: "official" | "booking";
  price?: number;
  currency: string;
  check_in?: string;
  check_out?: string;
  guests: number;
  breakfast_included?: boolean;
  cancellation_policy?: string;
  availability?: boolean;
  scraped_at: string;
}

export interface ScrapeJob {
  id: string;
  hotel_id?: string;
  triggered_by: string;
  status: "pending" | "running" | "completed" | "failed";
  hotels_total?: number;
  hotels_done: number;
  hotels_failed: number;
  error_log?: unknown[];
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface PriceComparison {
  hotel_id: string;
  official?: PriceSnapshot;
  booking?: PriceSnapshot;
  diff_pct?: number;
  cheaper_source?: "official" | "booking";
}
