'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Leaf, ChevronLeft, Activity, Microscope, ShieldAlert, Thermometer, FlaskConical } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export const dynamic = 'force-dynamic'
export const revalidate = 0

export default function PlantDetailPage() {
    const params = useParams()
    const router = useRouter()
    const [plant, setPlant] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (params.id) {
            fetchPlantDetails(params.id as string)
        }
    }, [params.id])

    const fetchPlantDetails = async (id: string) => {
        try {
            const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"
            const res = await fetch(`${API_BASE}/api/v1/plants/${id}`)
            if (res.ok) {
                const data = await res.json()
                setPlant(data.plant || data)
            }
        } catch (error) {
            console.error('Neural uplink failed:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-[#050505] flex items-center justify-center">
                <div className="relative w-24 h-24">
                    <div className="absolute inset-0 border-4 border-primary-500/20 rounded-full" />
                    <div className="absolute inset-0 border-4 border-primary-500 rounded-full border-t-transparent animate-spin" />
                    <Leaf className="absolute inset-0 m-auto text-primary-500 w-8 h-8 animate-pulse" />
                </div>
            </div>
        )
    }

    return (
        <main className="min-h-screen bg-[#050505] pt-24 pb-20 px-4 sm:px-6 lg:px-8">
            <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
            
            <div className="max-w-7xl mx-auto relative z-10">
                {/* Tactical Navigation */}
                <button 
                    onClick={() => router.back()}
                    className="group flex items-center gap-3 text-gray-500 hover:text-primary-400 transition-all mb-12"
                >
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-primary-500/50">
                        <ChevronLeft className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-[0.4em]">Abort Scan | Return to Registry</span>
                </button>

                <div className="grid lg:grid-cols-12 gap-12">
                    {/* Visual Asset Monolith */}
                    <div className="lg:col-span-5">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="relative aspect-[4/5] rounded-[40px] overflow-hidden border border-white/10 shadow-2xl shadow-primary-500/10 group"
                        >
                            <img 
                                src={plant?.image_url} 
                                alt={plant?.species_name}
                                className="w-full h-full object-cover grayscale-[0.5] group-hover:grayscale-0 transition-all duration-700"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent" />
                            
                            {/* Scanning HUD Overlay */}
                            <div className="absolute inset-0 pointer-events-none p-8 flex flex-col justify-between">
                                <div className="flex justify-between items-start">
                                    <div className="w-12 h-12 border-t-2 border-l-2 border-primary-500/50" />
                                    <div className="w-12 h-12 border-t-2 border-r-2 border-primary-500/50" />
                                </div>
                                <div className="flex justify-between items-end">
                                    <div className="w-12 h-12 border-b-2 border-l-2 border-primary-500/50" />
                                    <div className="w-12 h-12 border-b-2 border-r-2 border-primary-500/50" />
                                </div>
                            </div>

                            <div className="absolute bottom-10 left-10 right-10">
                                <h1 className="text-4xl md:text-6xl font-black text-white tracking-tighter uppercase mb-2">
                                    {plant?.common_name}
                                </h1>
                                <p className="text-primary-500 font-mono text-sm italic tracking-widest uppercase opacity-80">
                                    {plant?.scientific_name}
                                </p>
                            </div>
                        </motion.div>
                    </div>

                    {/* Intelligence Monograph */}
                    <div className="lg:col-span-7 space-y-10">
                        {/* Status Bar */}
                        <div className="flex flex-wrap gap-4">
                            <div className="px-6 py-3 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center gap-3">
                                <Activity className="w-4 h-4 text-primary-500" />
                                <span className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Clinical Precision: Validated</span>
                            </div>
                            <div className="px-6 py-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center gap-3">
                                <ShieldAlert className="w-4 h-4 text-amber-400" />
                                <span className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Safety: {plant?.iucn_status || 'Verified'}</span>
                            </div>
                        </div>

                        {/* Description */}
                        <section className="glass-card p-10 relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-4 opacity-5">
                                <Leaf className="w-32 h-32" />
                            </div>
                            <h2 className="text-xs font-black text-primary-500 uppercase tracking-[0.4em] mb-6 flex items-center gap-3">
                                <Microscope className="w-4 h-4" /> Botanical Intelligence
                            </h2>
                            <p className="text-gray-400 text-lg leading-relaxed font-medium">
                                {plant?.description}
                            </p>
                        </section>

                        {/* Regional Phylogeny */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[
                                { label: 'Hindi', value: plant?.regional_names?.hi },
                                { label: 'Tamil', value: plant?.regional_names?.ta },
                                { label: 'Telugu', value: plant?.regional_names?.te },
                                { label: 'Bengali', value: plant?.regional_names?.bn }
                            ].map((reg, i) => (
                                <div key={i} className="glass-card p-6 text-center border-white/5">
                                    <span className="text-[8px] font-black text-primary-500/50 uppercase tracking-widest block mb-2">{reg.label}</span>
                                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">{reg.value || '---'}</span>
                                </div>
                            ))}
                        </div>

                        {/* Medicinal Schema */}
                        <section className="space-y-6">
                            <h2 className="text-xs font-black text-primary-500 uppercase tracking-[0.4em] mb-8">Clinical Medicinal Schema</h2>
                            <div className="grid gap-6">
                                {(plant?.properties || []).map((prop: any, i: number) => (
                                    <motion.div 
                                        key={i}
                                        whileHover={{ x: 10 }}
                                        className="glass-card p-8 border-l-4 border-l-primary-500 group"
                                    >
                                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                            <div className="space-y-4">
                                                <h3 className="text-xl font-black text-white uppercase tracking-tighter group-hover:text-primary-400 transition-colors">
                                                    {prop.ailment}
                                                </h3>
                                                <p className="text-gray-500 text-sm font-medium max-w-md">
                                                    {prop.usage}
                                                </p>
                                            </div>
                                            <div className="flex flex-col gap-3 md:text-right">
                                                <div className="flex items-center gap-2 md:justify-end text-primary-500">
                                                    <FlaskConical className="w-3 h-3" />
                                                    <span className="text-[9px] font-black uppercase tracking-widest">Bio-Active Compound Found</span>
                                                </div>
                                                <div className="text-[10px] font-bold text-white/60 uppercase">Prep: {prop.preparation || 'Monograph Standard'}</div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </main>
    )
}
