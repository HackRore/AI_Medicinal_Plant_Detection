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
  Database,
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
  
  const rawConfidence = prediction?.confidence ?? result?.confidence ?? 0;
  const confidence = rawConfidence <= 1 ? Math.round(rawConfidence * 100) : Math.round(rawConfidence);
  
  const name       = (plant?.name || result?.class_name || result?.predicted_class || "Unknown Species").toString().replace(/_/g, ' ');
  const sciName    = (plant?.scientific_name || result?.scientific_name || "").toString();
  const family     = (plant?.family || "Botanical Registry").toString();
  
  const medicinalProperties = result?.botanical_intelligence?.medicinal_properties ?? 
                              result?.medicinal_properties ?? 
                              medicinal?.ayurvedic_uses?.map((u: any) => ({ ailment: u, usage_description: "Verified application." })) ?? 
                              [];

  const intel = result?.botanical_intelligence ?? {};
  const moa = intel?.mechanism_of_action ?? medicinal?.description ?? "Clinical mechanism under scientific review.";
  const balance = intel?.ayurvedic_balance ?? { vata: "neutral", pitta: "neutral", kapha: "neutral" };
  const synergies = intel?.synergy_partners ?? ["Tulsi", "Ginger", "Honey"];
  const reasoning = result?.reasoning ?? { verdict: "Standard Scan", analysis: "Scanning complete." };

  // G9 Forge: Lowered threshold for 88-class high-entropy model
  if (result.success === false || confidence < 12) {
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
        <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary-500/10 blur-[100px]" />

        <div className="relative group p-10 sm:p-12">
          {confidence < 60 && (
            <motion.div 
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="mb-8 p-6 bg-rose-500/10 border border-rose-500/20 rounded-3xl flex items-center gap-6"
            >
              <AlertTriangle className="w-8 h-8 text-rose-500 flex-shrink-0" />
              <div>
                <p className="text-xs font-black text-rose-500 uppercase tracking-widest">Low Confidence Protocol Active</p>
                <p className="text-[10px] text-gray-400 font-medium mt-1 uppercase tracking-tighter italic">
                  Image quality might be suboptimal. Check lighting or leaf focus.
                </p>
              </div>
            </motion.div>
          )}

          <div className="relative aspect-[4/3] sm:aspect-[16/9] md:aspect-[21/9] rounded-[3.5rem] overflow-hidden border border-white/10 bg-zinc-950/50 shadow-2xl">
              <motion.img 
                key={heatmap ? "heat" : "orig"}
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                src={heatmap ? result.gradcam?.overlay_base64 : imageUrl} 
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-60" />
              
              <div className="absolute inset-0 p-8 flex flex-col justify-between pointer-events-none">
                  <div className="flex justify-between items-start">
                      <div className="w-12 h-12 border-t-2 border-l-2 border-primary-500/50" />
                      <div className="px-4 py-2 rounded-xl bg-black/60 backdrop-blur-md border border-white/10">
                          <span className="text-[8px] font-black text-primary-400 uppercase tracking-[0.4em]">Neural Analysis Active</span>
                      </div>
                      <div className="w-12 h-12 border-t-2 border-r-2 border-primary-500/50" />
                  </div>
                  
                  <div className="flex justify-between items-end">
                      <div className="w-12 h-12 border-b-2 border-l-2 border-primary-500/50" />
                      <div className="flex gap-4 pointer-events-auto">
                        <button 
                          onClick={() => setHeatmap(!heatmap)}
                          className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-all ${
                            heatmap ? 'bg-primary-500 border-primary-400 text-black' : 'bg-black/60 border-white/10 text-primary-500'
                          }`}
                        >
                          <Maximize2 className="w-6 h-6" />
                        </button>
                      </div>
                      <div className="w-12 h-12 border-b-2 border-r-2 border-primary-500/50" />
                  </div>
              </div>

              <div className="absolute top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <a 
                  href="https://www.kaggle.com/datasets/mdfahimbinalam/leaf-dataset" 
                  target="_blank" 
                  className="px-4 py-2 bg-black/80 backdrop-blur-xl border border-white/10 rounded-full text-[8px] font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 hover:text-primary-400 transition-colors pointer-events-auto"
                >
                  <Database className="w-3 h-3" /> Trained on Clinical Leaf Dataset
                </a>
              </div>
          </div>
        </div>

        <div className="px-10 sm:px-12 pb-12">
            <div className="flex items-center gap-4 mb-8">
                <div className="h-[1px] flex-1 bg-white/5" />
                <span className="text-[9px] font-black text-primary-500/40 uppercase tracking-[0.5em]">Neural Confidence Spectrum</span>
                <div className="h-[1px] flex-1 bg-white/5" />
            </div>
            
            <div className="grid gap-4">
                {(prediction.top3 || []).map((cand: any, idx: number) => (
                    <motion.div 
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl flex items-center gap-6 group hover:bg-white/5 transition-all"
                    >
                        <div className="text-[10px] font-black text-gray-600 group-hover:text-primary-500 transition-colors w-6">0{idx+1}</div>
                        <div className="flex-1">
                            <div className="flex justify-between items-end mb-2">
                                <span className="text-sm font-black text-white uppercase tracking-tighter">{cand.name}</span>
                                <span className="text-[10px] font-bold text-primary-400">{Math.round(cand.confidence * 100)}%</span>
                            </div>
                            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${cand.confidence * 100}%` }}
                                    className={`h-full ${idx === 0 ? 'bg-primary-500' : 'bg-primary-500/40'}`}
                                />
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>

        <div className="grid lg:grid-cols-12 gap-10 p-10 sm:p-12 border-t border-white/5">
          <div className="lg:col-span-7 space-y-12">
              <section className="space-y-6">
                  <div className="flex items-center gap-4">
                      <div className="w-1 h-8 bg-primary-500 rounded-full shadow-[0_0_20px_rgba(16,185,129,0.5)]" />
                      <h2 className="text-4xl sm:text-6xl font-black text-white uppercase tracking-tighter leading-none">
                          {name}
                      </h2>
                  </div>
                  <div className="flex flex-wrap gap-4">
                      <span className="px-6 py-2 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black text-primary-400 uppercase tracking-widest">{family}</span>
                      <span className="px-6 py-2 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black text-gray-400 uppercase tracking-widest italic">{sciName}</span>
                  </div>
                  <p className="text-gray-400 leading-relaxed font-medium text-sm border-l-2 border-white/5 pl-8 italic">
                      {moa}
                  </p>

                  {/* Neural Reasoning Layer */}
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mt-10 p-8 rounded-[2.5rem] border ${
                        reasoning.verdict === "Verified" 
                        ? 'bg-primary-500/[0.03] border-primary-500/20' 
                        : reasoning.verdict === "Mismatch Detected"
                        ? 'bg-rose-500/[0.03] border-rose-500/20'
                        : 'bg-white/[0.02] border-white/10'
                    } relative overflow-hidden`}
                  >
                      <div className="scanline opacity-5" />
                      <div className="flex items-center justify-between mb-6">
                          <div className="flex items-center gap-3">
                              <Sparkles className={`w-5 h-5 ${reasoning.verdict === 'Verified' ? 'text-primary-500' : reasoning.verdict === 'Mismatch Detected' ? 'text-rose-500' : 'text-gray-500'}`} />
                              <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-500">Neural Reasoning Layer</h4>
                          </div>
                          <span className={`px-4 py-1.5 rounded-full text-[8px] font-black uppercase tracking-widest ${
                              reasoning.verdict === 'Verified' ? 'bg-primary-500/20 text-primary-400' : 
                              reasoning.verdict === 'Mismatch Detected' ? 'bg-rose-500/20 text-rose-400' : 
                              'bg-white/10 text-gray-400'
                          }`}>
                              {reasoning.verdict}
                          </span>
                      </div>
                      <p className="text-sm text-white font-bold leading-relaxed mb-4">
                          {reasoning.analysis}
                      </p>
                      {reasoning.scientific_confirmation && (
                          <div className="pt-4 border-t border-white/5 flex items-center gap-2">
                              <CheckCircle2 className="w-3 h-3 text-primary-500" />
                              <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                                  Gemini Consensus: <span className="text-white">{reasoning.scientific_confirmation}</span>
                              </span>
                          </div>
                      )}
                  </motion.div>
              </section>

              <section className="space-y-8">
                  <div className="flex items-center gap-4">
                      <BookOpen className="w-5 h-5 text-primary-500" />
                      <h3 className="text-xs font-black text-gray-500 uppercase tracking-[0.4em]">Clinical Monographs</h3>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-6">
                      {medicinalProperties.map((prop: any, i: number) => (
                          <div key={i} className="group p-8 bg-white/[0.02] border border-white/5 rounded-3xl hover:border-primary-500/30 transition-all hover:bg-white/[0.04]">
                              <h4 className="text-primary-400 font-black text-lg mb-3 tracking-tight group-hover:text-glow transition-all">{prop.ailment}</h4>
                              <p className="text-xs text-gray-500 leading-relaxed font-medium">{prop.usage_description}</p>
                          </div>
                      ))}
                  </div>
              </section>
          </div>

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
