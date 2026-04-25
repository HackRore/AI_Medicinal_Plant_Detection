/**
 * PlantoAI: Plants Repository Page
 * Live sync with 13-class hardened botanical database.
 */
"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { getApiBase } from "@/utils/api";

export default function PlantsPage() {
  const [plants, setPlants]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string|null>(null);
  const [search, setSearch]   = useState("");

  const [retryCount, setRetryCount] = useState(0);
  const [isWaking, setIsWaking] = useState(false);

  useEffect(() => {
    const API_BASE = getApiBase();
    const url = `${API_BASE}/api/v1/plants?search=${search}&limit=50`;
    setLoading(true);
    setError(null);

    const timer = setTimeout(() => {
      if (loading) setIsWaking(true);
    }, 5000);

    fetch(url)
      .then(r => { 
        if (!r.ok) throw new Error("Connection timed out"); 
        return r.json(); 
      })
      .then(d  => { 
        setPlants(d.plants ?? []); 
        setLoading(false);
        setIsWaking(false);
      })
      .catch(() => {
        if (retryCount < 3) {
            setTimeout(() => setRetryCount(prev => prev + 1), 3000);
        } else {
            setError("Neural engine is taking longer than usual to initialize.");
            setLoading(false);
            setIsWaking(false);
        }
      });

    return () => {
        clearTimeout(timer);
        setIsWaking(false);
    };
  }, [search, retryCount]);

  return (
    <main className="min-h-screen bg-[#050505] pt-32 pb-24 px-4 sm:px-6 lg:px-8">
      <div className="absolute inset-0 bg-primary-500/5 pointer-events-none" />
      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <div className="mb-20 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full mb-4">
              <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-400">G9 Botanical Repository</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-black text-white mb-4 tracking-tighter uppercase leading-none">
            Neural <span className="text-primary-500">Knowledge</span> Base
          </h1>
          <p className="text-gray-500 max-w-2xl mx-auto font-medium italic">
            Synchronized clinical monographs. Verified against ancient Ayurvedic taxonomies and modern botanical datasets.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-2xl mx-auto mb-24">
          <input 
            value={search} 
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by common name, scientific name, or family..." 
            className="w-full h-20 pl-8 pr-16 bg-white/5 border border-white/10 rounded-3xl text-white placeholder-gray-700 focus:outline-none focus:border-primary-500/50 transition-all font-medium backdrop-blur-3xl text-lg" 
          />
          <div className="absolute right-8 top-1/2 -translate-y-1/2 text-primary-500">
            <svg className="w-8 h-8 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Status/Error */}
        {error && (
            <div className="text-center p-16 glass-card mb-12 border-rose-500/20">
               <span className="text-5xl mb-6 block">📡</span>
               <p className="text-rose-400 font-black text-xl uppercase tracking-widest mb-8">{error}</p>
               <button 
                 onClick={() => window.location.reload()}
                 className="px-12 py-4 bg-rose-500 text-white rounded-2xl font-black uppercase tracking-widest hover:bg-rose-600 transition-all shadow-2xl shadow-rose-500/20 active:scale-95"
               >
                 Re-Initialize Uplink
               </button>
            </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <AnimatePresence mode="wait">
            {loading ? (
                <div className="col-span-full space-y-12">
                   <div className="flex flex-col items-center justify-center p-20 glass-card border-dashed">
                      <div className="w-16 h-16 border-4 border-primary-500/20 border-t-primary-500 rounded-full animate-spin mb-8" />
                      <p className="text-[10px] font-black text-primary-500 uppercase tracking-[0.5em] animate-pulse">Synchronizing Monolith...</p>
                      {isWaking && (
                        <p className="text-[9px] text-amber-500 uppercase tracking-widest mt-4">Waking up neural engine on Render (30s cold start)...</p>
                      )}
                   </div>
                   <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                    {Array(8).fill(0).map((_, i) => (
                      <div key={i} className="h-80 rounded-[40px] bg-white/5 animate-pulse border border-white/5" />
                    ))}
                   </div>
                </div>
            ) : (
                <>
                {plants.map((p, i) => (
                  <Link
                    key={p.id || p.scientific_name}
                    href={`/plants/${p.id || p.scientific_name}`}
                  >
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      className="group glass-card p-0 overflow-hidden hover:border-primary-500/30 transition-all hover:bg-white/[0.07] cursor-pointer"
                    >
                      {/* Visual Asset */}
                      <div className="relative h-48 w-full overflow-hidden">
                          <img 
                              src={p.image_url || `https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=2670&auto=format&fit=crop&q=plant,${p.common_name || p.scientific_name}`}
                              alt={p.scientific_name}
                              className="w-full h-full object-cover grayscale group-hover:grayscale-0 group-hover:scale-110 transition-all duration-700 opacity-60 group-hover:opacity-100"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent" />
                          
                          <div className="absolute top-4 left-4">
                              <div className="w-10 h-10 bg-primary-500/10 backdrop-blur-xl rounded-xl flex items-center justify-center text-xl border border-white/10">
                                  {p.toxicity?.level_code === 0 ? "🌿" : p.toxicity?.level_code === 1 ? "⚠️" : "🚫"}
                              </div>
                          </div>
  
                          <div className="absolute top-4 right-4">
                              <span className={`text-[7px] font-black uppercase tracking-[0.3em] px-3 py-1.5 rounded-lg border backdrop-blur-xl ${
                                  p.toxicity?.level_code === 0 ? "bg-primary-500/20 text-primary-400 border-primary-500/30" :
                                  p.toxicity?.level_code === 1 ? "bg-amber-500/20 text-amber-400 border-amber-500/30" :
                                  "bg-rose-500/20 text-rose-400 border-rose-500/30"
                              }`}>
                                  {p.toxicity?.level || "Safe"}
                              </span>
                          </div>
                      </div>
  
                      <div className="p-8">
                          <h3 className="text-xl font-black text-white mb-1 group-hover:text-primary-400 transition-colors capitalize tracking-tighter">
                          {p.common_name || p.scientific_name}
                          </h3>
                          <p className="text-xs text-gray-500 font-medium italic mb-6 font-serif">
                          {p.scientific_name}
                          </p>
                          
                          <div className="space-y-3 pt-4 border-t border-white/5">
                              <div className="flex items-center justify-between">
                                  <span className="text-[9px] text-primary-500/40 font-black uppercase tracking-widest">Taxa Family</span>
                                  <span className="text-[9px] text-white font-bold uppercase tracking-widest">{p.family || "N/A"}</span>
                              </div>
                              <div className="flex items-center justify-between">
                                  <span className="text-[9px] text-primary-500/40 font-black uppercase tracking-widest">Registry ID</span>
                                  <span className="text-[9px] text-white/60 font-bold truncate max-w-[100px] text-right">{p.id || "Monolith-v3"}</span>
                              </div>
                          </div>
                      </div>
                    </motion.div>
                  </Link>
                ))}
                </>
            )}
          </AnimatePresence>
        </div>

        {/* Empty State */}
        {!loading && plants.length === 0 && (
            <div className="text-center py-32 glass-card border-dashed">
                <span className="text-6xl mb-8 block">🔎</span>
                <p className="text-gray-500 font-black uppercase tracking-widest text-sm">No Botanical Signature Matches Found</p>
                <button onClick={() => setSearch("")} className="mt-6 text-primary-500 font-black uppercase tracking-[0.3em] text-[10px] hover:text-white transition-all">Clear Search Filter</button>
            </div>
        )}
      </div>
    </main>
  );
}
