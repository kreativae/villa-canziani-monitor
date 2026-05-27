import { getHotel, getPriceHistory, comparePrice } from "@/lib/api";
import { PriceChart } from "@/components/hotels/PriceChart";
import { ScrapeButton } from "@/components/dashboard/ScrapeButton";
import { formatBRL, formatDate, formatPct, diffColor } from "@/lib/utils";
import Link from "next/link";
import { ArrowLeft, ExternalLink, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";

export const revalidate = 0;

export default async function HotelDetailPage({ params }: { params: { id: string } }) {
  const [hotel, history, comparison] = await Promise.all([
    getHotel(params.id),
    getPriceHistory(params.id, undefined, 90),
    comparePrice(params.id).catch(() => null),
  ]);

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      {/* Back */}
      <Link href="/hotels" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800">
        <ArrowLeft size={14} /> Hotéis
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{hotel.name}</h1>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
            <span className="capitalize bg-gray-100 px-2 py-0.5 rounded-full">{hotel.category ?? "hotel"}</span>
            <span>{hotel.region}</span>
            {hotel.engine && <span className="text-blue-600 font-medium">{hotel.engine}</span>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ScrapeButton hotelId={hotel.id} />
          <Link
            href={`/hotels/${hotel.id}/edit`}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50"
          >
            <Pencil size={13} /> Editar
          </Link>
        </div>
      </div>

      {/* Price comparison cards */}
      <div className="grid grid-cols-3 gap-4">
        <PriceCard
          label="Site Oficial"
          price={comparison?.official?.price}
          sub={formatDate(comparison?.official?.scraped_at)}
          link={hotel.official_url}
          color="blue"
        />
        <PriceCard
          label="Booking.com"
          price={comparison?.booking?.price}
          sub={formatDate(comparison?.booking?.scraped_at)}
          link={hotel.booking_url}
          color="red"
        />
        <div className="rounded-xl border p-4 bg-white shadow-sm">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Diferença</p>
          <p className={cn("text-2xl font-bold", diffColor(comparison?.diff_pct))}>
            {formatPct(comparison?.diff_pct)}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {comparison?.cheaper_source
              ? `${comparison.cheaper_source === "official" ? "Oficial" : "Booking"} mais barato`
              : "Sem dados suficientes"}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Histórico de preços (90 dias)</h2>
        <PriceChart snapshots={history} />
      </div>

      {/* Urls */}
      {(hotel.official_url || hotel.booking_url || hotel.notes) && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-2 text-sm">
          {hotel.official_url && (
            <a href={hotel.official_url} target="_blank" rel="noreferrer"
               className="flex items-center gap-2 text-blue-600 hover:underline">
              <ExternalLink size={13} /> Site oficial
            </a>
          )}
          {hotel.booking_url && (
            <a href={hotel.booking_url} target="_blank" rel="noreferrer"
               className="flex items-center gap-2 text-blue-600 hover:underline">
              <ExternalLink size={13} /> Booking.com
            </a>
          )}
          {hotel.notes && <p className="text-gray-500">{hotel.notes}</p>}
        </div>
      )}
    </div>
  );
}

function PriceCard({
  label, price, sub, link, color,
}: {
  label: string;
  price?: number;
  sub?: string;
  link?: string;
  color: "blue" | "red";
}) {
  const border = color === "blue" ? "border-blue-400" : "border-red-400";
  return (
    <div className={`rounded-xl border-l-4 ${border} bg-white p-4 shadow-sm`}>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold mt-1">{formatBRL(price)}</p>
      <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
      {link && (
        <a href={link} target="_blank" rel="noreferrer"
           className="inline-flex items-center gap-1 text-xs text-blue-500 hover:underline mt-2">
          <ExternalLink size={10} /> ver site
        </a>
      )}
    </div>
  );
}
