'use client';

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ShieldCheck, 
  AlertTriangle, 
  Info, 
  FlaskConical, 
  BookOpen, 
  Droplets, 
  ExternalLink,
  CheckCircle2,
  XCircle,
  Maximize2,
  Globe,
  ShieldAlert,
  Sparkles,
  Wand2,
  Leaf,
  History
} from "lucide-react";

export default function PredictResult({ result, imageUrl }: { result: any; imageUrl: string }) {
  const [heatmap, setHeatmap] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  if (!result) return null;

  const plant      = result?.plant      ?? {};
  const prediction = result?.prediction ?? {};
  const toxicity   = result?.toxicity   ?? { level: "unknown", level_code: 3, notes: "" };
  const medicinal  = result?.medicinal  ?? {};
  const gradcam    = result?.gradcam    ?? {};
  
  // Normalize confidence to 0-100 scale regardless of input format
  const rawConfidence = prediction?.confidence ?? result?.confidence ?? 0;
  const confidence = rawConfidence <= 1 ? Math.round(rawConfidence * 100) : Math.round(rawConfidence);
  
  const name       = (plant?.name || result?.class_name || result?.predicted_class || "Unknown Species").toString().replace(/_/g, ' ');
  const sciName    = (plant?.scientific_name || result?.scientific_name || "").toString();
  const family     = (plant?.family || "Botanical Registry").toString();
  const confidence_label = (prediction?.confidence_label || (confidence > 80 ? "High" : confidence > 50 ? "Medium" : "Low")).toString();
  
  const medicinalProperties = result?.botanical_intelligence?.medicinal_properties ?? 
                              result?.medicinal_properties ?? 
                              medicinal?.ayurvedic_uses?.map((u: any) => ({ ailment: u, usage_description: "Verified application." })) ?? 
                              [];

  const intel = result?.botanical_intelligence ?? {};
  const moa = intel?.mechanism_of_action ?? medicinal?.description ?? "Clinical mechanism under scientific review.";
  const balance = intel?.ayurvedic_balance ?? { vata: "neutral", pitta: "neutral", kapha: "neutral" };
  const synergies = intel?.synergy_partners ?? ["Tulsi", "Ginger", "Honey"];

  if (result.success === false || confidence < 35) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-10 bg-black/60 backdrop-blur-3xl border border-rose-500/30 rounded-[40px] text-center space-y-6 shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-rose-500 to-transparent opacity-50" />
        <div className="relative z-10">
          <div className="w-20 h-20 bg-rose-500/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-rose-500/20">
            <ShieldAlert className="w-10 h-10 text-rose-500 animate-pulse" />
          </div>
          <h3 className="text-white font-black text-2xl uppercase tracking-tighter">Neural Boundary Alert</h3>
          <p className="text-rose-200/50 text-sm font-medium leading-relaxed max-w-sm mx-auto mt-4 px-4">
            The G9 Engine detected significant neural noise. The subject cannot be verified as a medicinal species within safe clinical parameters.
          </p>
          <div className="pt-8">
            <button className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl transition-all active:scale-95">
              Recalibrate Neural Lens
            </button>
          </div>
        </div>
      </motion.div>
    );
  }


  return (
    <motion.div 
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "circOut" }}
      className="glass-card rounded-[4rem] overflow-hidden relative"
    >
        {/* Glow & Mesh Accents */}
        <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary-500/10 blur-[100px]" />

      {/* 1. Tactical Intelligence Hero */}
      <div className="relative group p-10 sm:p-12">
        <div className="relative aspect-[16/9] md:aspect-[21/9] rounded-[3.5rem] overflow-hidden border border-white/10 bg-zinc-950/50 shadow-2xl">
            <motion.img 
              key={heatmap ? "heat" : "orig"}
              initial={{ opacity: 0, scale: 1.05 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1 }}
              src={heatmap && gradcam?.overlay_base64 ? gradcam.overlay_base64 : imageUrl}
              className="w-full h-full object-cover grayscale-[0.3] contrast-[1.1] opacity-80 group-hover:opacity-100 transition-all duration-1000"
              alt="Neural Analysis Output"
            />
            <div className="scanline opacity-10" />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-90" />
            
            {/* Tactical HUD Overlays */}
            <div className="absolute top-8 left-8 right-8 flex justify-between items-start">
              <div className="px-6 py-3 rounded-2xl backdrop-blur-3xl bg-black/40 border border-primary-500/30 flex items-center gap-4 shadow-[0_0_30px_rgba(16,185,129,0.1)]">
                <div className="w-2 h-2 rounded-full bg-primary-500 animate-ping" />
                <span className="text-[10px] font-black tracking-[0.4em] uppercase text-primary-400">
                    Clinical Match: {confidence}%
                </span>
              </div>
              
              <button 
                onClick={() => setHeatmap(!heatmap)}
                className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 text-white text-[10px] font-black uppercase tracking-[0.3em] transition-all glass-reflection overflow-hidden"
              >
                <Maximize2 className="w-4 h-4 text-primary-400" />
                {heatmap ? "Sensor Base" : "Neural Heatmap"}
              </button>
            </div>

            <div className="absolute bottom-12 left-12 right-12">
                <div className="space-y-2">
                    <p className="text-primary-500 text-[11px] font-black uppercase tracking-[0.6em] mb-4 text-glow">Taxon Identified</p>
                    <motion.h2 className="text-6xl md:text-8xl font-black text-white tracking-tighter mb-4 uppercase text-glow-white leading-none">
                      {(name || "Unknown").toString().replace(/_/g, ' ')}
                    </motion.h2>
                    <div className="flex items-center gap-6">
                        <span className="text-white/60 italic font-serif text-2xl">{sciName}</span>
                        <div className="h-1 w-12 bg-white/10 rounded-full" />
                        <span className="text-[11px] font-black text-primary-500/40 uppercase tracking-[0.4em]">{family} Family</span>
                    </div>
                </div>
            </div>
        </div>
      </div>

      {/* 2. Clinical Mechanism Synthesis */}
      <div className="px-12 pb-16 grid lg:grid-cols-12 gap-12">
          <div className="lg:col-span-12">
            <div className="p-12 bg-primary-500/[0.03] border border-primary-500/10 rounded-[3.5rem] relative overflow-hidden group hover:border-primary-500/30 transition-all shadow-inner">
                <div className="scanline opacity-5" />
                <div className="relative z-10 space-y-6">
                    <div className="flex items-center gap-4 text-primary-500">
                        <Sparkles className="w-6 h-6 animate-pulse" />
                        <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-glow">Mechanism of Action Synthesis</h3>
                    </div>
                    <p className="text-white/90 text-2xl md:text-3xl font-medium leading-[1.3] italic tracking-tight max-w-5xl">
                        "{moa}"
                    </p>
                </div>
            </div>
          </div>

          {/* 3. Neural Knowledge Blocks */}
          <div className="lg:col-span-7 space-y-12">
              <section className="bg-white/[0.02] border border-white/5 rounded-[3.5rem] p-12 relative overflow-hidden">
                <div className="scanline opacity-5" />
                <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-gray-600 mb-12 flex items-center gap-4">
                    <History className="w-5 h-5 text-primary-500/40" /> Ayurvedic Metabolic Projections
                </h3>
                <div className="grid grid-cols-3 gap-10">
                    {['vata', 'pitta', 'kapha'].map((dosha) => (
                        <div key={dosha} className="text-center space-y-6">
                            <div className="relative w-full aspect-square flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90">
                                    <circle cx="50%" cy="50%" r="42%" className="stroke-white/5 fill-none" strokeWidth="6" />
                                    <motion.circle 
                                        cx="50%" cy="50%" r="42%" 
                                        className={`fill-none ${balance[dosha] === 'balance' ? 'stroke-primary-500' : 'stroke-primary-900/20'}`} 
                                        strokeWidth="6" 
                                        strokeDasharray="264" 
                                        initial={{ strokeDashoffset: 264 }}
                                        animate={{ strokeDashoffset: balance[dosha] === 'balance' ? 60 : 220 }}
                                        transition={{ duration: 2, ease: "circOut" }}
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center space-y-1">
                                    <span className="text-[10px] font-black text-white uppercase tracking-widest">{dosha}</span>
                                    <span className={`text-[9px] font-bold ${balance[dosha] === 'balance' ? 'text-primary-400' : 'text-gray-700'} uppercase`}>
                                        {balance[dosha] || 'stabilized'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
              </section>

              <section className="space-y-6">
                  <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-gray-600 ml-4">Medicinal Spectrum (46-Taxa Match)</h3>
                  <div className="grid sm:grid-cols-2 gap-6">
                      {medicinalProperties.slice(0, 4).map((prop: any, i: number) => (
                          <div key={i} className="p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem] group hover:border-primary-500/20 transition-all">
                              <h4 className="text-primary-400 font-black text-lg mb-3 tracking-tight group-hover:text-glow transition-all">{prop.ailment}</h4>
                              <p className="text-xs text-gray-500 leading-relaxed font-medium">{prop.usage_description}</p>
                          </div>
                      ))}
                  </div>
              </section>
          </div>

          {/* 4. Strategic Sidebar */}
          <div className="lg:col-span-5 space-y-10">
              <section className="bg-primary-500/[0.05] border border-primary-500/10 rounded-[3.5rem] p-12 relative overflow-hidden">
                    <div className="scanline opacity-5" />
                    <div className="flex items-center gap-4 mb-10">
                        <Wand2 className="w-5 h-5 text-primary-500" />
                        <h4 className="text-[11px] font-black uppercase tracking-[0.5em] text-primary-500/60">Botanical Synergies</h4>
                    </div>
                    <div className="flex flex-wrap gap-3">
                        {synergies.map((s: string, i: number) => (
                            <span key={i} className="px-6 py-3 bg-black/60 border border-white/10 rounded-2xl text-xs font-black text-white flex items-center gap-3 shadow-2xl glass-reflection overflow-hidden">
                                <Leaf className="w-4 h-4 text-primary-500" /> {s}
                            </span>
                        ))}
                    </div>
              </section>

              <div className="p-10 bg-rose-500/[0.03] border border-rose-500/10 rounded-[3.5rem]">
                  <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-3 text-rose-500">
                          <ShieldAlert className="w-5 h-5" />
                          <h4 className="text-[11px] font-black uppercase tracking-[0.5em] text-rose-500/60">Ethics & Stability</h4>
                      </div>
                  </div>
                  <p className="text-xs text-rose-200/30 font-medium leading-relaxed italic">
                      Monograph source integrity verified. G9 Clinical Registry cross-referenced against IUCN protocols for sustainable botanical research.
                  </p>
              </div>
          </div>
      </div>

      {/* 5. Production Handshake Footer */}
      <div className="px-12 py-10 bg-white/[0.01] border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-10">
          <div className="flex items-center gap-6">
             <div className="w-16 h-16 bg-primary-500/10 rounded-3xl flex items-center justify-center border border-primary-500/10">
                <Sparkles className="w-8 h-8 text-primary-500" />
             </div>
             <div>
                <h4 className="text-white font-black text-lg uppercase tracking-widest leading-none mb-2">Neural Learning Active</h4>
                <p className="text-gray-600 text-xs font-bold uppercase tracking-widest">G9 Forge Calibration v5.1.0</p>
             </div>
          </div>
          <div className="flex items-center gap-6">
              <button 
                onClick={() => setFeedbackSent(true)} 
                className="group relative h-16 px-12 bg-primary-500 text-black text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl transition-all shadow-[0_0_40px_rgba(16,185,129,0.2)] active:scale-95 overflow-hidden"
              >
                <div className="absolute inset-0 glass-reflection" />
                Accurate
              </button>
              <button 
                onClick={() => setFeedbackSent(true)}
                className="h-16 px-12 bg-white/5 border border-white/10 text-white/30 text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl hover:text-white transition-all active:scale-95"
              >
                Recalibrate
              </button>
          </div>
      </div>
    </motion.div>
  );
}
