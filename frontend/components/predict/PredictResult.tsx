/**
 * PlantoAI: Predict Result Component
 * Scientific Grad-CAM visualization + G9 Medicinal Knowledge Overlay
 */
"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export default function PredictResult({ result, imageUrl }: { result: any; imageUrl: string }) {
  const [heatmap, setHeatmap] = useState(true);
  const { plant, prediction, toxicity, medicinal, gradcam, quality } = result;

  const confColor = prediction.confidence >= 80 ? "#4ade80" // Green-400
                  : prediction.confidence >= 50 ? "#fbbf24" // Amber-400
                  : "#ef4444"; // Red-500

  const toxBg    = toxicity?.level_code === 0 ? "bg-green-500/10 text-green-400 border-green-500/20"
                  : toxicity?.level_code === 1 ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  : "bg-red-500/10 text-red-100 border-red-500/20";

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-2xl mx-auto bg-black/60 backdrop-blur-2xl border border-white/10 rounded-[40px] overflow-hidden shadow-2xl"
    >
      {/* Visual Proof Section */}
      <div className="relative aspect-video w-full group">
        <img 
          src={heatmap && gradcam?.overlay_base64 ? gradcam.overlay_base64 : imageUrl}
          alt="Neural Analysis"
          className="w-full h-full object-cover transition-all duration-700"
        />
        
        {/* Overlays */}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-8">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-black text-white tracking-tighter mb-1 capitalize">
                        {plant.name}
                    </h2>
                    <p className="text-primary-400 font-mono text-xs uppercase tracking-[0.3em]">
                        {plant.scientific_name}
                    </p>
                </div>
                <div className="text-right">
                    <div className="text-4xl font-black mb-1" style={{ color: confColor }}>
                        {prediction.confidence}%
                    </div>
                    <p className="text-gray-400 text-[10px] font-bold uppercase tracking-widest">
                        Neural Confidence
                    </p>
                </div>
            </div>
        </div>

        {/* Grad-CAM Toggle */}
        {gradcam?.overlay_base64 && (
          <button 
            onClick={() => setHeatmap(!heatmap)}
            className="absolute top-6 right-6 px-4 py-2 bg-black/60 hover:bg-black/80 backdrop-blur-md border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-white transition-all active:scale-95"
          >
            {heatmap ? "Show Original" : "Show Grad-CAM Proof"}
          </button>
        )}
      </div>

      {/* Medicinal Insights Grid */}
      <div className="p-8 space-y-8">
        
        {/* Quality & Toxicity Quick Bar */}
        <div className="flex flex-wrap gap-4 items-center">
            <div className={`px-4 py-2 rounded-2xl border text-xs font-black uppercase tracking-widest ${toxBg}`}>
                Toxicity: {toxicity?.level || "Unknown"}
            </div>
            {!quality.passed && (
                <div className="px-4 py-2 bg-amber-500/10 text-amber-500 border border-amber-500/20 rounded-2xl text-[10px] font-bold uppercase animate-pulse">
                    ⚠ Low Confidence Sample
                </div>
            )}
        </div>

        {/* Top 3 Probabilities */}
        <div className="bg-white/5 border border-white/5 rounded-3xl p-6">
            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Neural Alternatives</p>
            <div className="flex gap-6">
                {prediction.top3.slice(1).map((t: any, i: number) => (
                    <div key={i} className="flex flex-col">
                        <span className="text-sm font-bold text-white mb-0.5">{t.name}</span>
                        <div className="h-1 w-12 bg-gray-800 rounded-full overflow-hidden">
                            <div className="h-full bg-primary-500" style={{ width: `${t.confidence}%` }} />
                        </div>
                        <span className="text-[9px] text-gray-500 font-bold mt-1 uppercase">{t.confidence}%</span>
                    </div>
                ))}
            </div>
        </div>

        {/* Detailed Knowledge */}
        <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
                <h4 className="text-xs font-black text-primary-400 uppercase tracking-widest border-b border-white/5 pb-2">Ayurvedic Applications</h4>
                <ul className="space-y-2">
                    {medicinal.ayurvedic_uses.map((use: string, i: number) => (
                        <li key={i} className="flex gap-3 text-sm text-gray-300 leading-relaxed font-medium">
                            <span className="text-primary-500">◈</span> {use}
                        </li>
                    ))}
                </ul>
            </div>

            <div className="space-y-4">
                <h4 className="text-xs font-black text-primary-400 uppercase tracking-widest border-b border-white/5 pb-2">Classical Preparation</h4>
                <p className="text-sm text-gray-300 leading-relaxed font-medium">
                    {medicinal.preparation}
                </p>
                {medicinal.active_compounds?.length > 0 && (
                  <div className="pt-4 mt-4 border-t border-white/5">
                    <p className="text-[10px] font-bold text-gray-500 uppercase mb-2">Active Compounds</p>
                    <div className="flex flex-wrap gap-2">
                        {medicinal.active_compounds.map((c: string, i: number) => (
                            <span key={i} className="text-[10px] px-2 py-1 bg-white/5 rounded-md text-gray-400 font-mono">{c}</span>
                        ))}
                    </div>
                  </div>
                )}
            </div>
        </div>

        {/* Contraindications - Unique G9 Feature */}
        {medicinal.contraindications?.length > 0 && (
            <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-[28px]">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-red-500/20 rounded-xl flex items-center justify-center text-lg">⚠️</div>
                    <h4 className="text-xs font-black text-red-100 uppercase tracking-widest">Clinical Contraindications</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                    {medicinal.contraindications.map((c: string, i: number) => (
                        <span key={i} className="text-xs text-red-200/80 font-medium">
                            • {c}
                        </span>
                    ))}
                </div>
            </div>
        )}

        {/* Description Footer */}
        <div className="pt-8 border-t border-white/5 text-center">
             <p className="text-xs text-gray-500 max-w-lg mx-auto leading-relaxed italic">
                 "{medicinal.description}"
             </p>
             <div className="mt-4 flex items-center justify-center gap-2 text-[10px] font-black text-gray-600 uppercase tracking-widest">
                 <span>{plant.family}</span>
                 <span className="w-1 h-1 bg-gray-600 rounded-full" />
                 <span>Origin: {plant.native_region}</span>
             </div>
        </div>
      </div>
    </motion.div>
  );
}
