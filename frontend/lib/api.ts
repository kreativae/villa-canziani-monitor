import type { Hotel, PriceSnapshot, ScrapeJob, PriceComparison } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

// Hotels
export const getHotels = (activeOnly = true) =>
  apiFetch<Hotel[]>(`/hotels/?active_only=${activeOnly}`);

export const getHotel = (id: string) =>
  apiFetch<Hotel>(`/hotels/${id}`);

export const createHotel = (data: Partial<Hotel>) =>
  apiFetch<Hotel>("/hotels/", { method: "POST", body: JSON.stringify(data) });

export const updateHotel = (id: string, data: Partial<Hotel>) =>
  apiFetch<Hotel>(`/hotels/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const deleteHotel = (id: string) =>
  apiFetch<void>(`/hotels/${id}`, { method: "DELETE" });

// Prices
export const getPriceHistory = (hotelId: string, source?: string, limit = 90) => {
  const params = new URLSearchParams({ limit: String(limit) });
  if (source) params.set("source", source);
  return apiFetch<PriceSnapshot[]>(`/prices/${hotelId}?${params}`);
};

export const comparePrice = (hotelId: string) =>
  apiFetch<PriceComparison>(`/prices/compare/${hotelId}`);

// Scraper
export const triggerScrape = (hotelId?: string) =>
  apiFetch<{ job_id: string; status: string }>("/scraper/run", {
    method: "POST",
    body: JSON.stringify(hotelId ? { hotel_id: hotelId } : {}),
  });

export const getScrapeJobs = (limit = 20) =>
  apiFetch<ScrapeJob[]>(`/scraper/jobs?limit=${limit}`);

export const getScrapeJob = (jobId: string) =>
  apiFetch<ScrapeJob>(`/scraper/jobs/${jobId}`);
