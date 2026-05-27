import { createClient } from "@supabase/supabase-js";
import { getScrapeJobs } from "@/lib/api";
import { StatCard } from "@/components/dashboard/StatCard";
import { ScrapeButton } from "@/components/dashboard/ScrapeButton";
import { HotelTable } from "@/components/hotels/HotelTable";
import { formatDate } from "@/lib/utils";
import type { Hotel, ScrapeJob } from "@/types";

export const revalidate = 0;

async function fetchHotels(): Promise<Hotel[]> {
  // Read hotels + latest prices directly from Supabase (no backend needed)
  const db = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const { data: hotels } = await db
    .from("hotels")
    .select("*")
    .eq("active", true)
    .order("name");

  if (!hotels?.length) return [];

  // Latest price per hotel (one query)
  const ids = hotels.map((h) => h.id);
  const { data: snaps } = await db
    .from("price_snapshots")
    .select("hotel_id, source, price, scraped_at")
    .in("hotel_id", ids)
    .order("scraped_at", { ascending: false });

  const latest: Record<string, { official?: number; booking?: number; scraped_at?: string }> = {};
  for (const s of snaps ?? []) {
    if (!latest[s.hotel_id]) latest[s.hotel_id] = {};
    const e = latest[s.hotel_id];
    if (s.source === "official" && e.official == null) e.official = s.price;
    if (s.source === "booking" && e.booking == null) e.booking = s.price;
    if (!e.scraped_at) e.scraped_at = s.scraped_at;
  }

  return hotels.map((h) => {
    const p = latest[h.id] ?? {};
    const diff =
      p.official && p.booking
        ? parseFloat((((p.booking - p.official) / p.official) * 100).toFixed(2))
        : null;
    return {
      ...h,
      latest_official_price: p.official ?? null,
      latest_booking_price: p.booking ?? null,
      price_diff_pct: diff,
      last_scraped_at: p.scraped_at ?? null,
    };
  });
}

async function fetchJobs(): Promise<ScrapeJob[]> {
  try {
    return await getScrapeJobs(5);
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const [hotels, jobs] = await Promise.all([fetchHotels(), fetchJobs()]);

  const lastJob = jobs[0];

  const officialsWithPrice = hotels.filter((h) => h.latest_official_price != null);
  const avgOfficial =
    officialsWithPrice.length > 0
      ? officialsWithPrice.reduce((s, h) => s + h.latest_official_price!, 0) /
        officialsWithPrice.length
      : null;

  const bookingCheaper = hotels.filter(
    (h) =>
      h.latest_booking_price != null &&
      h.latest_official_price != null &&
      h.latest_booking_price < h.latest_official_price
  ).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Praia do Patacho · Alagoas · {hotels.length} propriedades monitoradas
          </p>
        </div>
        <ScrapeButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Hotéis monitorados" value={hotels.length} accent="blue" />
        <StatCard
          label="Preço médio (site oficial)"
          value={avgOfficial != null ? `R$ ${avgOfficial.toFixed(0)}` : "—"}
          accent="green"
        />
        <StatCard
          label="Booking mais barato"
          value={bookingCheaper}
          sub="propriedades"
          accent={bookingCheaper > 0 ? "red" : "gray"}
        />
        <StatCard
          label="Última atualização"
          value={lastJob ? formatDate(lastJob.completed_at ?? lastJob.created_at) : "—"}
          sub={lastJob?.status}
          accent={lastJob?.status === "running" ? "yellow" : "gray"}
        />
      </div>

      {lastJob?.status === "running" && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-yellow-50 border border-yellow-200 text-sm text-yellow-800">
          <span className="animate-pulse w-2 h-2 rounded-full bg-yellow-500 inline-block" />
          Varredura em andamento — {lastJob.hotels_done}/{lastJob.hotels_total ?? "?"} hotéis concluídos
        </div>
      )}

      <div>
        <h2 className="text-base font-semibold text-gray-800 mb-3">Todos os hotéis</h2>
        <HotelTable hotels={hotels} />
      </div>
    </div>
  );
}
