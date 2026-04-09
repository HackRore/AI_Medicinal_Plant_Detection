/**
 * PlantoAI: Plants Repository Page
 * Live sync with 13-class hardened botanical database.
 */
"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function PlantsPage() {
  const [plants, setPlants]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string|null>(null);
  const [search, setSearch]   = useState("");

  useEffect(() => {
    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/plants?search=${search}&limit=50`;
    setLoading(true);
    fetch(url)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d  => { setPlants(d.plants ?? []); setLoading(false); })
      .catch(() => {
        setError("AI engine is warming up. Please wait 30 seconds and refresh.");
        setLoading(false);
      });
  }, [search]);

  return (
    <main className="min-h-screen bg-gray-900 pt-32 pb-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tighter">
            Botanical <span className="text-primary-400">Intelligence</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto font-medium">
            Explore India's premier medicinal herb repository. Every entry is verified 
            against the G9 Scientific Spec for Ayurvedic authenticity.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-xl mx-auto mb-16">
          <input 
            value={search} 
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by common or scientific name..." 
            className="w-full h-14 pl-6 pr-14 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all font-medium backdrop-blur-md" 
          />
          <div className="absolute right-5 top-1/2 -translate-y-1/2 text-primary-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Status/Error */}
        {error && (
            <div className="text-center p-12 bg-red-900/10 border border-red-500/20 rounded-3xl mb-12">
               <span className="text-3xl mb-4 block">🧪</span>
               <p className="text-red-400 font-bold mb-6">{error}</p>
               <button 
                 onClick={() => window.location.reload()}
                 className="px-8 py-3 bg-red-500 text-white rounded-xl font-bold hover:bg-red-600 transition-colors shadow-lg shadow-red-500/20"
               >
                 Re-initialize Session
               </button>
            </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <AnimatePresence mode="wait">
            {loading ? (
                <>
                {Array(8).fill(0).map((_, i) => (
                  <div key={i} className="h-64 rounded-3xl bg-white/5 animate-pulse border border-white/5" />
                ))}
                </>
            ) : (
                <>
                {plants.map((p, i) => (
                  <motion.div
                    key={p.scientific_name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="group bg-black/40 border border-white/5 rounded-3xl p-6 hover:border-primary-500/30 transition-all hover:bg-black/60 backdrop-blur-xl"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="w-12 h-12 bg-primary-500/10 rounded-2xl flex items-center justify-center text-2xl">
                          {p.toxicity?.level_code === 0 ? "🌿" : p.toxicity?.level_code === 1 ? "⚠️" : "🚫"}
                      </div>
                      <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full border ${
                        p.toxicity?.level_code === 0 ? "bg-green-500/10 text-green-400 border-green-500/20" :
                        p.toxicity?.level_code === 1 ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                        "bg-red-500/10 text-red-100 border-red-500/20"
                      }`}>
                        {p.toxicity?.level}
                      </span>
                    </div>

                    <h3 className="text-xl font-bold text-white mb-1 group-hover:text-primary-400 transition-colors capitalize">
                      {p.common_names?.[0] || p.scientific_name}
                    </h3>
                    <p className="text-sm text-gray-500 font-medium italic mb-4">
                      {p.scientific_name}
                    </p>
                    
                    <div className="space-y-2 pt-4 border-t border-white/5">
                        <div className="flex items-center gap-2">
                             <span className="text-xs text-primary-400 font-bold uppercase tracking-widest">Family:</span>
                             <span className="text-xs text-gray-400">{p.family || "N/A"}</span>
                        </div>
                        <div className="flex items-center gap-2">
                             <span className="text-xs text-primary-400 font-bold uppercase tracking-widest">Region:</span>
                             <span className="text-xs text-gray-400 truncate">{p.native_region || "N/A"}</span>
                        </div>
                    </div>
                  </motion.div>
                ))}
                </>
            )}
          </AnimatePresence>
        </div>

        {/* Empty State */}
        {!loading && plants.length === 0 && (
            <div className="text-center py-24 border-2 border-dashed border-white/5 rounded-[40px]">
                <span className="text-5xl mb-4 block">🕵️‍♂️</span>
                <p className="text-gray-500 font-medium">No botanical matches found in our G9 repository.</p>
                <button onClick={() => setSearch("")} className="mt-4 text-primary-400 font-bold hover:underline">Clear Search</button>
            </div>
        )}
      </div>
    </main>
  );
}
