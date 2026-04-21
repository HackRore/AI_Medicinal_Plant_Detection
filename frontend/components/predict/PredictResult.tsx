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
  Globe
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
  const toxColor  = ["text-emerald-400", "text-amber-400", "text-rose-400", "text-slate-400"][toxCode] ?? "text-slate-400";
  const toxBg     = ["bg-emerald-500/10", "bg-amber-500/10", "bg-rose-500/10", "bg-slate-500/10"][toxCode] ?? "bg-slate-500/10";
  const toxBorder = ["border-emerald-500/20", "border-amber-500/20", "border-rose-500/20", "border-slate-500/20"][toxCode] ?? "border-slate-500/20";

  if (result.success === false) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-center space-y-3"
      >
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
        <h3 className="text-rose-100 font-bold text-lg">Botanical Guardrail Triggered</h3>
        <p className="text-rose-200/70 text-sm leading-relaxed">
          {result?.message ?? "The G9 Neural Engine could not verify this as a medicinal species with high confidence."}
        </p>
        <button className="px-4 py-2 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-semibold rounded-lg transition-colors">
          Retry with better lighting
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[#0f172a]/80 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl overflow-y-auto max-h-[85vh] scrollbar-hide"
    >
      {/* 1. Analysis Hero Area */}
      <div className="relative group aspect-video sm:aspect-square md:aspect-video lg:max-h-80 overflow-hidden">
        <motion.img 
          key={heatmap ? "heat" : "orig"}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          src={heatmap && gradcam?.overlay_base64 ? gradcam.overlay_base64 : imageUrl}
          className="w-100 h-100 object-cover"
          alt="Analysis target"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0f172a] via-transparent to-transparent opacity-80" />
        
        {/* Top Controls */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
          <div className={`px-3 py-1.5 rounded-full backdrop-blur-md bg-black/40 border border-white/10 flex items-center gap-2 ${confColor}`}>
            <ShieldCheck className="w-4 h-4" />
            <span className="text-xs font-bold tracking-tight">{confidence}% {confLabel}</span>
          </div>
          
          {gradcam?.overlay_base64 && (
            <button 
              onClick={() => setHeatmap(!heatmap)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/20 hover:bg-indigo-500/40 border border-indigo-500/30 text-indigo-200 text-xs font-semibold transition-all group active:scale-95"
            >
              <Maximize2 className="w-3.5 h-3.5" />
              {heatmap ? "Base Image" : "Neural Heatmap"}
            </button>
          )}
        </div>

        {/* Bottom Title */}
        <div className="absolute bottom-6 left-6">
          <motion.h2 
            initial={{ x: -10, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-3xl font-black text-white tracking-tight"
          >
            {name}
          </motion.h2>
          <div className="flex items-center gap-2 mt-1">
             <span className="text-indigo-400 italic text-sm font-medium">{sciName}</span>
             <span className="text-white/20">•</span>
             <span className="text-slate-400 text-xs uppercase tracking-widest">{family}</span>
          </div>
        </div>
      </div>

      {/* 2. Quality Alert (If needed) */}
      <AnimatePresence>
        {!quality.passed && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-amber-500/10 border-b border-amber-500/20 px-6 py-3 flex items-center gap-3"
          >
            <Info className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="text-[11px] text-amber-200/80 leading-tight">
              <b>Analysis Alert:</b> {quality.message}
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. Toxicity Badge */}
      <div className={`mx-6 mt-6 p-4 rounded-2xl border ${toxBorder} ${toxBg} flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <AlertTriangle className={`w-5 h-5 ${toxColor}`} />
          <div>
            <p className={`text-[10px] uppercase tracking-wider font-bold opacity-60 ${toxColor}`}>Toxicity Index</p>
            <p className={`text-sm font-bold capitalize ${toxColor}`}>
              {(toxLevel ?? "unknown").replace("_", " ")} Safety Status
            </p>
          </div>
        </div>
        <div className="text-[11px] text-slate-400 max-w-[50%] text-right leading-tight">
          {toxicity.notes || "Consult a certified Ayurvedic professional before any internal use."}
        </div>
      </div>

      {/* 4. Actionable Intelligence Tabs */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column: Traditional Uses */}
        <div className="space-y-6">
          <section>
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              <h3 className="text-xs uppercase tracking-[0.2em] font-black text-slate-500">Ayurvedic Monograph</h3>
            </div>
            <ul className="space-y-3">
              {uses.map((use: string, i: number) => (
                <motion.li 
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 * i }}
                  key={i} 
                  className="flex items-start gap-3 p-3 bg-white/5 rounded-xl border border-white/5 hover:border-indigo-500/30 transition-colors group"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500/50 mt-1.5 shrink-0 group-hover:scale-150 transition-transform" />
                  <span className="text-sm text-slate-200 leading-relaxed italic">{use}</span>
                </motion.li>
              ))}
            </ul>
          </section>
        </div>

        {/* Right Column: Labs & Prep */}
        <div className="space-y-6">
          <section className="bg-indigo-500/5 p-5 rounded-2xl border border-indigo-500/10">
            <div className="flex items-center gap-2 mb-3 text-indigo-400">
              <Droplets className="w-4 h-4" />
              <h4 className="text-[10px] uppercase font-bold tracking-widest">Preparation Protocol</h4>
            </div>
            <p className="text-sm text-indigo-100/80 leading-relaxed mb-4">
              {prep || "Specific preparation methods pending clinical audit."}
            </p>
            
            <div className="flex items-center gap-2 mt-6 mb-2 text-indigo-400">
              <FlaskConical className="w-4 h-4" />
              <h4 className="text-[10px] uppercase font-bold tracking-widest">Active Phytochemicals</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {compounds.map((c: string, i: number) => (
                <span key={i} className="px-2 py-1 bg-indigo-500/20 rounded-md text-[10px] font-mono text-indigo-300 border border-indigo-500/20">
                  {c}
                </span>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* 5. Clinical Safety & Origin */}
      <div className="mx-6 mb-6 p-5 bg-black/20 rounded-2xl border border-white/5 space-y-4">
        {desc && (
           <p className="text-xs text-slate-400 leading-relaxed italic border-l-2 border-indigo-500/30 pl-4">
             {desc}
           </p>
        )}
        
        <div className="flex flex-wrap gap-4 text-[10px] font-bold text-slate-500 tracking-wider">
          <span className="flex items-center gap-1.5"><Globe className="w-3 h-3 text-emerald-500" /> {region || "NATIVE: UNKNOWN"}</span>
          {contra.length > 0 && (
            <span className="flex items-center gap-1.5 text-rose-400 uppercase">
              <AlertTriangle className="w-3 h-3" /> {contra.length} Contraindications
            </span>
          )}
        </div>
      </div>

      {/* 6. Active Learning & Improvement Loop */}
      <div className="p-6 bg-indigo-600/10 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div>
          <h4 className="text-xs font-bold text-white flex items-center gap-2">
            AI Evolution Feedback
          </h4>
          <p className="text-[10px] text-slate-500 mt-1">Is this identification accurate? Your feedback trains reality.</p>
        </div>
        
        <div className="flex items-center gap-3">
          {feedbackSent ? (
            <motion.div 
               initial={{ scale: 0.8 }} 
               animate={{ scale: 1 }} 
               className="flex items-center gap-2 text-emerald-400 font-bold text-xs"
            >
              <CheckCircle2 className="w-4 h-4" /> Contributing to model...
            </motion.div>
          ) : (
            <>
              <button 
                onClick={() => setFeedbackSent(true)}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-400 text-xs font-bold border border-emerald-500/30 transition-all hover:-translate-y-0.5"
              >
                <CheckCircle2 className="w-4 h-4" /> Accurate
              </button>
              <button 
                onClick={() => setFeedbackSent(true)}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/40 text-rose-400 text-xs font-bold border border-rose-500/30 transition-all hover:-translate-y-0.5"
              >
                <XCircle className="w-4 h-4" /> Correction Needed
              </button>
            </>
          )}
        </div>
      </div>

      {/* 7. References (Small/Subtle) */}
      {refs.length > 0 && (
        <div className="p-4 bg-black/40 text-[9px] text-slate-600 font-mono tracking-tight flex items-start gap-3">
          <ExternalLink className="w-3 h-3 shrink-0" />
          <div className="space-y-1">
            <span className="opacity-50 uppercase font-black tracking-[0.2em] block mb-1">Citations & Monographs</span>
            {refs.map((r:string, i:number) => <div key={i}>{r}</div>)}
          </div>
        </div>
      )}
    </motion.div>
  );
}
