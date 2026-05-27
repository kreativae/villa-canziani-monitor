"use client";
import Link from "next/link";
import { Hotel } from "@/types";
import { formatBRL, formatPct, formatDate, diffColor, cn } from "@/lib/utils";
import { ExternalLink, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface HotelTableProps {
  hotels: Hotel[];
}

export function HotelTable({ hotels }: HotelTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <th className="px-4 py-3">Hotel</th>
            <th className="px-4 py-3">Categoria</th>
            <th className="px-4 py-3 text-right">Site Oficial</th>
            <th className="px-4 py-3 text-right">Booking</th>
            <th className="px-4 py-3 text-right">Diferença</th>
            <th className="px-4 py-3">Atualizado</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {hotels.map((h, i) => {
            const diff = h.price_diff_pct;
            const DiffIcon = diff == null ? Minus : diff > 0 ? TrendingUp : TrendingDown;
            return (
              <tr
                key={h.id}
                className={cn(
                  "border-b border-gray-50 hover:bg-blue-50/40 transition-colors",
                  i % 2 === 0 ? "bg-white" : "bg-gray-50/40"
                )}
              >
                <td className="px-4 py-3 font-medium text-gray-900 max-w-xs">
                  <Link href={`/hotels/${h.id}`} className="hover:text-blue-600 hover:underline">
                    {h.name}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <span className="inline-block px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 text-xs capitalize">
                    {h.category ?? "—"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {formatBRL(h.latest_official_price)}
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {formatBRL(h.latest_booking_price)}
                </td>
                <td className={cn("px-4 py-3 text-right font-semibold flex items-center justify-end gap-1", diffColor(diff))}>
                  <DiffIcon size={13} />
                  {formatPct(diff)}
                </td>
                <td className="px-4 py-3 text-xs text-gray-400">
                  {formatDate(h.last_scraped_at)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {h.official_url && (
                      <a href={h.official_url} target="_blank" rel="noreferrer"
                         className="text-gray-400 hover:text-blue-500" title="Site oficial">
                        <ExternalLink size={14} />
                      </a>
                    )}
                    {h.booking_url && (
                      <a href={h.booking_url} target="_blank" rel="noreferrer"
                         className="text-gray-400 hover:text-blue-700" title="Booking">
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
