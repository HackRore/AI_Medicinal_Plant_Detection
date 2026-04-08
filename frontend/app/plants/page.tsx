'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Leaf, Info, Zap } from 'lucide-react'

export default function PlantsPage() {
    const [plants, setPlants] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [search, setSearch] = useState('')

    useEffect(() => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/plants`)
            .then(r => { if (!r.ok) throw new Error("Backend offline"); return r.json(); })
            .then(d => { setPlants(d.plants ?? d); setLoading(false); })
            .catch(() => {
                setError("AI engine is starting up — please wait 30 seconds and refresh.");
                setLoading(false);
            });
    }, []);

    const filtered = (Array.isArray(plants) ? plants : []).filter(p => {
        if (!p) return false;
        const s = (search || "").toLowerCase();
        return (
            (p.name?.toString().toLowerCase() || "").includes(s) ||
            (p.medicinal_uses?.toString().toLowerCase() || "").includes(s) ||
            (p.scientific_name?.toString().toLowerCase() || "").includes(s) ||
            (p.ayurvedic_name?.toString().toLowerCase() || "").includes(s)
        );
    })

    if (loading) return (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "1rem", padding: "2rem" }}>
            {Array(12).fill(0).map((_, i) => (
                <div key={i} style={{ height: 180, background: "#1a1f2e", borderRadius: 12, animation: "pulse 1.5s infinite" }} />
            ))}
        </div>
    );

    if (error) return (
        <div style={{ padding: "2rem", textAlign: "center", color: "#f59e0b" }}>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
        </div>
    );

    return (
        <main className="min-h-screen bg-[#050805] text-white selection:bg-emerald-500/30">
            <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12"
                >
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <div className="h-1 w-12 bg-emerald-500 rounded-full" />
                            <span className="text-emerald-500 font-mono text-xs font-bold uppercase tracking-[0.2em]">Botanical Intelligence</span>
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-4 italic">
                            LEAF<span className="text-emerald-500 not-italic">DB</span>
                        </h1>
                        <p className="text-gray-400 max-w-xl text-lg leading-relaxed">
                            A curated repository of <span className="text-white font-medium">{plants.length} medicinal species</span>, synchronized with our CNN neural network.
                        </p>
                    </div>

                    <div className="relative group w-full md:w-96">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-emerald-500/50 group-focus-within:text-emerald-400 transition-colors" />
                        <input
                            type="text"
                            placeholder="Search symptoms, names..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-emerald-500/50 focus:bg-white/[0.08] transition-all text-sm font-medium placeholder:text-gray-600"
                        />
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
                    {filtered.map((plant, i) => (
                        <motion.div
                            key={plant.id || i}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.03 }}
                            className="group relative bg-white/[0.02] border border-white/5 rounded-[2rem] p-6 hover:bg-white/[0.05] hover:border-emerald-500/30 transition-all duration-500 flex flex-col justify-between"
                        >
                            <div className="absolute top-4 right-4 text-emerald-500/20 group-hover:text-emerald-500/40 transition-colors">
                                <Leaf className="h-8 w-8 -rotate-12" />
                            </div>

                            <div>
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 bg-emerald-500/10 text-emerald-500 rounded-lg border border-emerald-500/20">
                                        {plant.family || 'PlantoAI'}
                                    </span>
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">
                                    {plant.name}
                                </h3>
                                <p className="text-emerald-500/60 font-mono text-[11px] mb-4 italic truncate">
                                    {plant.scientific_name || 'Species unidentified'}
                                </p>
                                <p className="text-gray-400 text-xs leading-relaxed line-clamp-3 mb-6">
                                    {plant.medicinal_uses || plant.description || 'Rich history of medicinal use in traditional Ayurvedic texts.'}
                                </p>
                            </div>

                            <button className="w-full py-3 rounded-xl bg-white/5 border border-white/10 group-hover:bg-emerald-600 group-hover:border-emerald-500 transition-all duration-300 text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 group-hover:text-white text-gray-400">
                                <Info className="h-3 w-3" />
                                View Neural Data
                            </button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </main>
    )
}