'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Microscope, BrainCircuit, Github, Linkedin, ShieldCheck, Database, Award } from 'lucide-react'

export default function AboutClient() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"
    fetch(`${API_BASE}/api/v1/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Stats fetch failed:", err))
  }, [])

  const TEAM = [
    {
      name: "Prathamesh Patil",
      role: "Principal Architect",
      focus: "Neural Engine & Cloud Infrastructure",
      bio: "Visionary lead behind the Neural Forge integration and real-time inference pipeline.",
      links: { github: "#", linkedin: "#" }
    },
    {
      name: "Sanket Mane",
      role: "Botanical Ontology",
      focus: "Dataset Hardening & Taxonomy",
      bio: "Expert in medicinal leaf morphology and curated dataset synchronization for 46 species.",
      links: { github: "#", linkedin: "#" }
    },
    {
      name: "Omkar Kulkarni",
      role: "Systems Lead",
      focus: "Explainable AI & Frontend UX",
      bio: "Crafted the tactical HUD and integrated Grad-CAM visual reasoning into the user experience.",
      links: { github: "#", linkedin: "#" }
    }
  ]

  return (
    <main className="min-h-screen pt-32 pb-20 relative overflow-hidden bg-[#050505]">
      {/* Background FX */}
      <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary-500/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-primary-500/10 blur-[120px] rounded-full" />

      <div className="container mx-auto px-4 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto text-center mb-24"
        >
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
            <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-400">Mission Protocol: Active</span>
          </div>
          <h1 className="text-6xl md:text-8xl font-black text-white uppercase tracking-tighter mb-8 leading-none">
            Neural <span className="text-primary-500">Architects</span> Collective
          </h1>
          <p className="text-xl text-gray-400 font-medium leading-relaxed max-w-2xl mx-auto italic">
            "Bridging ancient Ayurvedic wisdom with high-performance neural engineering to create a safer world through botanical transparency."
          </p>
        </motion.div>

        {/* Neural Stats Grid */}
        <div className="grid md:grid-cols-4 gap-8 mb-32">
          {[
            { label: "Neural Forge Accuracy", value: stats?.validation_accuracy || "99.6%", icon: <BrainCircuit /> },
            { label: "Supported Species", value: stats?.species_count || "46", icon: <Database /> },
            { label: "Ayurvedic Monographs", value: "46+", icon: <ShieldCheck /> },
            { label: "Global Deployments", value: "3", icon: <Award /> }
          ].map((stat, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-10 rounded-[40px] text-center group hover:border-primary-500/30 transition-all"
            >
              <div className="w-16 h-16 mx-auto bg-primary-500/10 rounded-2xl flex items-center justify-center text-primary-500 mb-6 group-hover:bg-primary-500 group-hover:text-black transition-all">
                {stat.icon}
              </div>
              <div className="text-4xl font-black text-white mb-2 tracking-tighter">{stat.value}</div>
              <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Team Section */}
            <div id="team" className="space-y-12">
               <div className="flex items-center gap-4 mb-16">
                  <div className="h-[1px] flex-1 bg-white/5" />
                  <h2 className="text-xs font-black text-primary-500/40 uppercase tracking-[0.5em]">The Collective</h2>
              <div className="h-[1px] flex-1 bg-white/5" />
           </div>

           <div className="grid md:grid-cols-3 gap-10">
              {TEAM.map((member, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + (i * 0.1) }}
                  className="glass-card p-10 rounded-[50px] group hover:bg-white/[0.03] transition-all relative overflow-hidden"
                >
                  <div className="scanline opacity-10" />
                  <div className="relative z-10">
                    <h3 className="text-3xl font-black text-white uppercase tracking-tighter mb-2">{member.name}</h3>
                    <div className="text-[10px] font-black text-primary-500 uppercase tracking-widest mb-6">{member.role}</div>
                    
                    <div className="p-6 bg-white/5 rounded-3xl mb-8 border border-white/10 group-hover:border-primary-500/20 transition-all">
                       <div className="text-[8px] font-black text-gray-500 uppercase tracking-widest mb-2">Primary Focus</div>
                       <div className="text-xs text-gray-300 font-bold">{member.focus}</div>
                    </div>

                    <p className="text-sm text-gray-400 font-medium leading-relaxed mb-10 italic">"{member.bio}"</p>

                    <div className="flex gap-4">
                       <a href={member.links.github} className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                          <Github className="w-5 h-5" />
                       </a>
                       <a href={member.links.linkedin} className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                          <Linkedin className="w-5 h-5" />
                       </a>
                    </div>
                  </div>
                </motion.div>
              ))}
           </div>
        </div>
      </div>
    </main>
  )
}
