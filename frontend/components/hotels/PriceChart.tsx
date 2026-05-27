"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from "recharts";
import { PriceSnapshot } from "@/types";
import { formatBRL } from "@/lib/utils";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface PriceChartProps {
  snapshots: PriceSnapshot[];
}

export function PriceChart({ snapshots }: PriceChartProps) {
  // Group by date, merge official + booking on same date
  const byDate: Record<string, { date: string; official?: number; booking?: number }> = {};

  for (const s of snapshots) {
    const day = s.scraped_at.slice(0, 10);
    if (!byDate[day]) byDate[day] = { date: day };
    if (s.source === "official") byDate[day].official = s.price ?? undefined;
    if (s.source === "booking") byDate[day].booking = s.price ?? undefined;
  }

  const data = Object.values(byDate)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((d) => ({
      ...d,
      label: format(new Date(d.date + "T12:00:00"), "dd/MM", { locale: ptBR }),
    }));

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
        Nenhum histórico de preços disponível ainda.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v) => `R$${(v / 1000).toFixed(1)}k`} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v: number) => formatBRL(v)} />
        <Legend />
        <Line
          type="monotone"
          dataKey="official"
          name="Site Oficial"
          stroke="#2563eb"
          strokeWidth={2}
          dot={false}
          connectNulls
        />
        <Line
          type="monotone"
          dataKey="booking"
          name="Booking.com"
          stroke="#dc2626"
          strokeWidth={2}
          dot={false}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
