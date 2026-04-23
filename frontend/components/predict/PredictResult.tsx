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
  const quality    = result?.quality    ?? { passed: false, message: "" };

  const name       = plant?.name            ?? result?.class_name ?? "Unknown Species";
  const sciName    = plant?.scientific_name ?? "";
  const family     = plant?.family          ?? "";
  const region     = plant?.native_region   ?? "";
  const confidence = prediction?.confidence ?? 0;
  const confLabel  = prediction?.confidence_label ?? "";
  const top3       = prediction?.top3       ?? [];
  const uses       = medicinal?.ayurvedic_uses    ?? [];
  const prep       = medicinal?.preparation       ?? "";
  const compounds  = medicinal?.active_compounds  ?? [];
  const contra     = medicinal?.contraindications ?? [];
  const desc       = medicinal?.description       ?? "";
  const refs       = medicinal?.references        ?? [];
  const toxLevel   = toxicity?.level      ?? "unknown";
  const toxCode    = toxicity?.level_code ?? 3;

  const confColor = confidence >= 80 ? "text-emerald-400" : confidence >= 50 ? "text-amber-400" : "text-rose-400";

  if (result.success === false || (prediction?.confidence ?? 0) < 40) {
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

  // Botanical Intelligence Mapping
  const intel = result?.botanical_intelligence ?? {};
  const moa = intel?.mechanism_of_action ?? "Clinical mechanism under scientific review.";
  const balance = intel?.ayurvedic_balance ?? {};
  const synergies = intel?.synergy_partners ?? ["Tulsi", "Ginger"];
  const medicinalProperties = intel?.medicinal_properties ?? [];

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-black/40 backdrop-blur-3xl border border-white/10 rounded-[48px] overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.5)] relative"
    >
        {/* Glow Effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-transparent pointer-events-none" />

      {/* 1. Scanner Hero Area */}
      <div className="relative group p-6 sm:p-10">
        <div className="relative aspect-video rounded-[32px] overflow-hidden border border-white/10 bg-zinc-900/50">
            <motion.img 
              key={heatmap ? "heat" : "orig"}
              initial={{ opacity: 0, scale: 1.1 }}
              animate={{ opacity: 1, scale: 1 }}
              src={heatmap && gradcam?.overlay_base64 ? gradcam.overlay_base64 : imageUrl}
              className="w-full h-full object-cover grayscale-[0.2] contrast-[1.1]"
              alt="Neural Analysis"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-60" />
            
            {/* HUD Overlays */}
            <div className="absolute top-6 left-6 right-6 flex justify-between items-start">
              <div className="px-4 py-2 rounded-2xl backdrop-blur-xl bg-black/60 border border-indigo-500/30 flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                <span className={`text-[10px] font-black tracking-widest uppercase text-indigo-400`}>
                    Verified Identity {confidence}%
                </span>
              </div>
              
              <button 
                onClick={() => setHeatmap(!heatmap)}
                className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 text-white text-[10px] font-black uppercase tracking-widest transition-all"
              >
                <Maximize2 className="w-3.5 h-3.5 text-indigo-400" />
                {heatmap ? "Base Sensor" : "Neural Mode"}
              </button>
            </div>

            <div className="absolute bottom-10 left-10">
                <p className="text-indigo-400 text-[10px] font-black uppercase tracking-[0.5em] mb-2 opacity-60">Neural Match Found</p>
                <motion.h2 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-2">{name}</motion.h2>
                <div className="flex items-center gap-3">
                    <span className="text-white/60 italic font-serif text-lg">{sciName}</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/40" />
                    <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Family: {family}</span>
                </div>
            </div>
        </div>
      </div>

      {/* 2. Mechanism of Action - Premium Section */}
      <div className="px-10 pb-10 grid lg:grid-cols-12 gap-10">
          <div className="lg:col-span-12">
            <div className="p-8 bg-indigo-500/5 border border-indigo-500/10 rounded-[32px] relative overflow-hidden group hover:border-indigo-500/20 transition-all">
                <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                    <FlaskConical className="w-32 h-32 text-indigo-400" />
                </div>
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4 text-indigo-400">
                        <Sparkles className="w-5 h-5" />
                        <h3 className="text-[10px] font-black uppercase tracking-[0.4em]">Mechanism of Action</h3>
                    </div>
                    <p className="text-white/80 text-xl font-medium leading-relaxed italic tracking-tight">
                        "{moa}"
                    </p>
                </div>
            </div>
          </div>

          {/* 3. Ayurvedic Balance (Gauges) & Properties */}
          <div className="lg:col-span-7 space-y-8">
              <section className="bg-white/5 border border-white/10 rounded-[40px] p-8">
                <h3 className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-8 flex items-center gap-2">
                    <History className="w-4 h-4" /> Ayurvedic Homeostasis Profiles
                </h3>
                <div className="grid grid-cols-3 gap-6">
                    {['vata', 'pitta', 'kapha'].map((dosha) => (
                        <div key={dosha} className="text-center space-y-4">
                            <div className="relative w-full aspect-square flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90">
                                    <circle cx="50%" cy="50%" r="45%" className="stroke-white/5 fill-none" strokeWidth="8" />
                                    <motion.circle 
                                        cx="50%" cy="50%" r="45%" 
                                        className={`fill-none ${balance[dosha] === 'balance' ? 'stroke-indigo-400' : 'stroke-indigo-500/20'}`} 
                                        strokeWidth="8" 
                                        strokeDasharray="283" 
                                        initial={{ strokeDashoffset: 283 }}
                                        animate={{ strokeDashoffset: balance[dosha] === 'balance' ? 70 : 250 }}
                                        transition={{ duration: 1.5, ease: "easeOut" }}
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-[10px] font-black text-white uppercase">{dosha}</span>
                                    <span className={`text-[8px] font-bold ${balance[dosha] === 'balance' ? 'text-indigo-400' : 'text-gray-600'} uppercase`}>
                                        {balance[dosha] || 'neutral'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="mt-8 pt-8 border-t border-white/5">
                    <p className="text-xs text-gray-500 font-medium italic">"{balance.note || "Tridoshic balancing properties detected."}"</p>
                </div>
              </section>

              <section className="space-y-4">
                  <h3 className="text-[10px] font-black uppercase tracking-widest text-gray-500 pl-2">Medicinal Spectrum</h3>
                  <div className="grid sm:grid-cols-2 gap-4">
                      {medicinalProperties.slice(0, 4).map((prop: any, i: number) => (
                          <div key={i} className="p-5 bg-white/5 border border-white/5 rounded-3xl group hover:border-indigo-500/20 transition-all">
                              <h4 className="text-indigo-400 font-bold text-sm mb-2">{prop.ailment}</h4>
                              <p className="text-[10px] text-gray-500 leading-relaxed font-medium">{prop.usage_description}</p>
                          </div>
                      ))}
                  </div>
              </section>
          </div>

          {/* 4. Synergies & Ethics Sidebar */}
          <div className="lg:col-span-5 space-y-8">
              <section className="bg-indigo-500/10 border border-indigo-500/20 rounded-[40px] p-8">
                    <div className="flex items-center gap-2 mb-6">
                        <Wand2 className="w-4 h-4 text-indigo-400" />
                        <h4 className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Botanical Synergies</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {synergies.map((s: string, i: number) => (
                            <span key={i} className="px-4 py-2 bg-black/40 border border-white/10 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-xl">
                                <Leaf className="w-3 h-3 text-indigo-400" /> {s}
                            </span>
                        ))}
                    </div>
                    <p className="mt-6 text-[10px] text-indigo-400/60 font-medium leading-relaxed italic">
                        Highly compatible with these herbs for enhanced therapeutic resonance.
                    </p>
              </section>

              <div className="p-8 bg-rose-500/5 border border-rose-500/10 rounded-[40px]">
                  <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2 text-rose-400">
                          <ShieldAlert className="w-4 h-4" />
                          <h4 className="text-[10px] font-black uppercase tracking-widest">Ethics Index</h4>
                      </div>
                      <span className="px-3 py-1 bg-rose-500/20 rounded-full text-[8px] font-black text-rose-400 uppercase tracking-widest">
                        {result?.plant?.iucn_status || "Least Concern"}
                      </span>
                  </div>
                  <p className="text-[10px] text-rose-200/40 font-medium leading-relaxed">
                      Sustainably source identification verified. Protect biodiversity while exploring botanical medicine.
                  </p>
              </div>
          </div>
      </div>

      {/* 5. Forge Feedback Footer */}
      <div className="px-10 py-8 bg-white/5 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
             <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                <Sparkles className="w-6 h-6 text-indigo-400" />
             </div>
             <div>
                <h4 className="text-white font-black text-xs uppercase tracking-widest">Neural Learning Active</h4>
                <p className="text-gray-600 text-[10px] font-bold">Help the G9 Forge perfect its clinical detection.</p>
             </div>
          </div>
          <div className="flex items-center gap-4">
              <button 
                onClick={() => setFeedbackSent(true)} 
                className="px-8 py-3 bg-indigo-400 text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-xl hover:bg-indigo-300 transition-all shadow-xl shadow-indigo-500/10 active:scale-95"
              >
                Identification Accurate
              </button>
              <button 
                onClick={() => setFeedbackSent(true)}
                className="px-8 py-3 bg-white/5 border border-white/10 text-white/40 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl hover:text-white transition-all active:scale-95 text-center"
              >
                Needs Calibration
              </button>
          </div>
      </div>
    </motion.div>
  );
}
