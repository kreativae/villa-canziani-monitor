import Link from "next/link";
import { createClient } from "@supabase/supabase-js";
import { HotelTable } from "@/components/hotels/HotelTable";
import { Plus } from "lucide-react";
import type { Hotel } from "@/types";

export const revalidate = 0;

async function fetchHotels(): Promise<Hotel[]> {
  const db = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data } = await db.from("hotels").select("*").order("name");
  return (data ?? []) as Hotel[];
}

export default async function HotelsPage() {
  const hotels = await fetchHotels();

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hotéis</h1>
          <p className="text-sm text-gray-500 mt-0.5">{hotels.length} propriedades cadastradas</p>
        </div>
        <Link
          href="/hotels/new"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
        >
          <Plus size={15} /> Cadastrar hotel
        </Link>
      </div>
      <HotelTable hotels={hotels} />
    </div>
  );
}
