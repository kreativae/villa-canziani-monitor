"use client";
import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { triggerScrape, getScrapeJob } from "@/lib/api";

interface ScrapeButtonProps {
  hotelId?: string;
  onComplete?: () => void;
}

export function ScrapeButton({ hotelId, onComplete }: ScrapeButtonProps) {
  const [state, setState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);

  async function handleClick() {
    setState("running");
    setProgress(null);
    try {
      const { job_id } = await triggerScrape(hotelId);
      // Poll until done
      const interval = setInterval(async () => {
        const job = await getScrapeJob(job_id);
        setProgress({ done: job.hotels_done, total: job.hotels_total ?? 0 });
        if (job.status === "completed" || job.status === "failed") {
          clearInterval(interval);
          setState(job.status === "completed" ? "done" : "error");
          onComplete?.();
          setTimeout(() => setState("idle"), 3000);
        }
      }, 2000);
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 3000);
    }
  }

  const labels = {
    idle: "Atualizar Agora",
    running: progress ? `Atualizando… ${progress.done}/${progress.total}` : "Iniciando…",
    done: "Concluído!",
    error: "Erro — tentar novamente",
  };

  return (
    <button
      onClick={handleClick}
      disabled={state === "running"}
      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-ocean-600 text-white text-sm font-semibold
                 hover:bg-ocean-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
    >
      <RefreshCw size={15} className={state === "running" ? "animate-spin" : ""} />
      {labels[state]}
    </button>
  );
}
