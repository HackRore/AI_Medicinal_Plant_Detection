"use client";
import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ShieldCheck, AlertCircle } from "lucide-react";

export default function DemoBanner() {
  const [status, setStatus] = useState<"connecting" | "live" | "fallback">("connecting");

  useEffect(() => {
    const api = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com";
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    fetch(`${api}/health`, { signal: controller.signal })
      .then(async (res) => {
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          setStatus(data.status === "synchronized" ? "live" : "fallback");
        } else {
          setStatus("fallback");
        }
      })
      .catch(() => {
        clearTimeout(timeoutId);
        setStatus("fallback");
      });

    return () => clearTimeout(timeoutId);
  }, []);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 left-0 w-full z-[100] pointer-events-none"
      >
        <div className="container mx-auto px-4 py-3 flex justify-center">
          <div className="flex items-center gap-4 px-6 py-2 bg-black/40 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl pointer-events-auto">
            {status === "connecting" && (
              <>
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-[9px] font-black uppercase tracking-[0.3em] text-blue-400">Syncing Neural Monolith...</span>
              </>
            )}
            {status === "live" && (
              <>
                <div className="relative">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping absolute inset-0" />
                  <div className="w-2 h-2 rounded-full bg-emerald-500 relative" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-black uppercase tracking-[0.3em] text-emerald-400">System Live</span>
                  <div className="h-3 w-px bg-white/10 mx-1" />
                  <span className="text-[8px] font-bold text-white/40 uppercase tracking-widest">G9 Core Active</span>
                </div>
              </>
            )}
            {status === "fallback" && (
              <>
                <div className="w-2 h-2 rounded-full bg-amber-500" />
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-black uppercase tracking-[0.3em] text-amber-400">Offline Intelligence Mode</span>
                  <div className="h-3 w-px bg-white/10 mx-1" />
                  <span className="text-[8px] font-bold text-white/40 uppercase tracking-widest">Local Knowledge Base</span>
                </div>
              </>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
