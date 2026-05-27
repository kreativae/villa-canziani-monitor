"use client";
import { useState } from "react";
import { Hotel } from "@/types";
import { createHotel, updateHotel } from "@/lib/api";
import { useRouter } from "next/navigation";

interface HotelFormProps {
  hotel?: Hotel;
}

const ENGINE_OPTIONS = ["", "omnibees", "cloudbeds", "simplotel", "fastbooking", "custom"];
const CATEGORY_OPTIONS = ["", "hotel", "boutique", "pousada", "resort"];

export function HotelForm({ hotel }: HotelFormProps) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: hotel?.name ?? "",
    official_url: hotel?.official_url ?? "",
    booking_url: hotel?.booking_url ?? "",
    category: hotel?.category ?? "",
    region: hotel?.region ?? "Praia do Patacho",
    engine: hotel?.engine ?? "",
    notes: hotel?.notes ?? "",
    active: hotel?.active ?? true,
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      if (hotel) {
        await updateHotel(hotel.id, form);
      } else {
        await createHotel(form);
      }
      router.push("/hotels");
      router.refresh();
    } catch (err) {
      alert("Erro ao salvar: " + String(err));
    } finally {
      setSaving(false);
    }
  }

  const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
  const labelCls = "block text-xs font-semibold text-gray-600 mb-1";

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
      <div>
        <label className={labelCls}>Nome *</label>
        <input name="name" value={form.name} onChange={handleChange} required className={inputCls} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelCls}>Categoria</label>
          <select name="category" value={form.category} onChange={handleChange} className={inputCls}>
            {CATEGORY_OPTIONS.map((o) => <option key={o} value={o}>{o || "— selecionar —"}</option>)}
          </select>
        </div>
        <div>
          <label className={labelCls}>Motor de reservas</label>
          <select name="engine" value={form.engine} onChange={handleChange} className={inputCls}>
            {ENGINE_OPTIONS.map((o) => <option key={o} value={o}>{o || "— automático —"}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label className={labelCls}>URL Site Oficial</label>
        <input name="official_url" value={form.official_url} onChange={handleChange} type="url" className={inputCls} />
      </div>
      <div>
        <label className={labelCls}>URL Booking.com</label>
        <input name="booking_url" value={form.booking_url} onChange={handleChange} type="url" className={inputCls} />
      </div>
      <div>
        <label className={labelCls}>Região</label>
        <input name="region" value={form.region} onChange={handleChange} className={inputCls} />
      </div>
      <div>
        <label className={labelCls}>Observações</label>
        <textarea name="notes" value={form.notes} onChange={handleChange} rows={3} className={inputCls} />
      </div>
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="active"
          name="active"
          checked={form.active}
          onChange={handleChange}
          className="rounded"
        />
        <label htmlFor="active" className="text-sm text-gray-700">Ativo (monitorado)</label>
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={saving}
          className="px-5 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 disabled:opacity-60"
        >
          {saving ? "Salvando…" : hotel ? "Salvar alterações" : "Cadastrar hotel"}
        </button>
        <button
          type="button"
          onClick={() => router.back()}
          className="px-5 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
