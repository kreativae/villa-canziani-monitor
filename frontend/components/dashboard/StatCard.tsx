import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: "green" | "blue" | "red" | "yellow" | "gray";
}

const accentMap = {
  green: "border-green-400 bg-green-50",
  blue: "border-blue-400 bg-blue-50",
  red: "border-red-400 bg-red-50",
  yellow: "border-yellow-400 bg-yellow-50",
  gray: "border-gray-300 bg-white",
};

export function StatCard({ label, value, sub, accent = "gray" }: StatCardProps) {
  return (
    <div className={cn("rounded-xl border-l-4 p-4 shadow-sm", accentMap[accent])}>
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  );
}
