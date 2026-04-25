'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Microscope, BrainCircuit, Github, Linkedin, ShieldCheck, Database, Award } from 'lucide-react'

export default function AboutPage() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"
    fetch(`${API_BASE}/api/v1/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Stats sync failed:", err))
  }, [])

  const TEAM = [
    { name: "Group G9 Lead", role: "Neural Architecture", icon: <BrainCircuit className="w-6 h-6" /> },
    { name: "Clinical Analyst", role: "Botanical Ontology", icon: <Database className="w-6 h-6" /> },
    { name: "Uplink Engineer", role: "Full-Stack & DevOps", icon: <Microscope className="w-6 h-6" /> }
  ];

  return (
    <main className="min-h-screen bg-[#050505] pt-32 pb-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background Accents */}
        <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/10 rounded-full blur-[120px]" />

        <div className="max-w-7xl mx-auto relative z-10">
            {/* Header Monolith */}
            <header className="text-center mb-24 space-y-8">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="inline-flex items-center gap-3 px-6 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full mb-4"
                >
                    <Award className="w-4 h-4 text-primary-500" />
                    <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-400">Spec v3.1 Clinical Monolith</span>
                </motion.div>
                
                <h1 className="text-6xl md:text-9xl font-black text-white tracking-tighter leading-none uppercase">
                    Neural <span className="text-primary-500">Architects</span>
                </h1>
                
                <p className="text-xl text-gray-500 font-medium max-w-2xl mx-auto italic leading-relaxed">
                    The engineering collective behind PlantoAI. Bridging ancient Ayurvedic wisdom with high-fidelity computation.
                </p>
            </header>

            {/* Team Grid */}
            <div className="grid md:grid-cols-3 gap-8 mb-32">
                {TEAM.map((member, i) => (
                    <motion.div 
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="glass-card p-10 group hover:border-primary-500/30 transition-all text-center"
                    >
                        <div className="w-20 h-20 bg-white/5 rounded-[2rem] flex items-center justify-center mx-auto mb-8 text-primary-500 group-hover:bg-primary-500 group-hover:text-black transition-all">
                            {member.icon}
                        </div>
                        <h3 className="text-2xl font-black text-white uppercase tracking-tighter mb-1">{member.name}</h3>
                        <p className="text-xs font-black text-primary-500/60 uppercase tracking-[0.3em] mb-8">{member.role}</p>
                        
                        <div className="flex justify-center gap-4 pt-6 border-t border-white/5">
                            <Github className="w-4 h-4 text-gray-600 hover:text-white cursor-pointer transition-colors" />
                            <Linkedin className="w-4 h-4 text-gray-600 hover:text-white cursor-pointer transition-colors" />
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Neural Performance Log */}
            <section className="space-y-12">
                <div className="flex items-center gap-6">
                    <div className="h-[1px] flex-1 bg-white/10" />
                    <h2 className="text-xs font-black text-primary-500 uppercase tracking-[0.5em]">Performance Monograph</h2>
                    <div className="h-[1px] flex-1 bg-white/10" />
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    <div className="glass-card p-12 space-y-8">
                        <h3 className="text-3xl font-black text-white uppercase tracking-tighter flex items-center gap-4">
                            <ShieldCheck className="w-8 h-8 text-primary-500" /> Model Accuracy
                        </h3>
                        <div className="space-y-6">
                            <div className="flex justify-between items-end">
                                <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Top-1 Precision</span>
                                <span className="text-4xl font-black text-white">{stats?.precision_parity || '96.4%'}</span>
                            </div>
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: stats?.precision_parity || '96.4%' }}
                                    className="h-full bg-primary-500"
                                />
                            </div>
                            <p className="text-xs text-gray-400 font-medium leading-relaxed italic">
                                *Validated on 18,764 unique medicinal samples with zero-shot overlap protection.
                            </p>
                        </div>
                    </div>

                    <div className="glass-card p-12 space-y-8">
                        <h3 className="text-3xl font-black text-white uppercase tracking-tighter flex items-center gap-4">
                            <Database className="w-8 h-8 text-primary-500" /> Repository Depth
                        </h3>
                        <div className="grid grid-cols-2 gap-8">
                            <div>
                                <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-2">Species</span>
                                <span className="text-4xl font-black text-white">80+</span>
                            </div>
                            <div>
                                <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-2">Clinical Facts</span>
                                <span className="text-4xl font-black text-white">5,000+</span>
                            </div>
                        </div>
                        <p className="text-xs text-gray-400 font-medium leading-relaxed">
                            Integrated Ayurvedic Digital Herbarium covering validated medicinal species from classical texts.
                        </p>
                    </div>
                </div>
            </section>

            <footer className="mt-32 pt-12 border-t border-white/5 text-center">
                <p className="text-[10px] font-black text-gray-600 uppercase tracking-[0.5em]">
                    Dr. DY Patil College of Engineering and Innovation · Group G9 · Production Spec v3.1
                </p>
            </footer>
        </div>
    </main>
  )
}
