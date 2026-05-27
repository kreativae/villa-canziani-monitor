"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, Hotel, RefreshCw, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Dashboard", icon: BarChart2 },
  { href: "/hotels", label: "Hotéis", icon: Hotel },
  { href: "/settings", label: "Configurações", icon: Settings },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-56 bg-ocean-900 text-white flex flex-col shrink-0">
      <div className="px-4 py-5 border-b border-white/10">
        <p className="text-xs font-semibold text-blue-300 uppercase tracking-widest">Villa Canziani</p>
        <h1 className="text-sm font-bold mt-0.5 leading-tight">Radar Hoteleiro<br />do Patacho</h1>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              path === href
                ? "bg-white/15 text-white"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10 text-xs text-white/40">
        v1.0.0
      </div>
    </aside>
  );
}
