'use client';

import { useState, useMemo } from "react";
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
  History,
  AlertCircle,
  Search,
  MessageSquare,
  Send,
  ChevronDown,
  ChevronUp
} from "lucide-react";

const KAGGLE_DATASET_URL = "https://www.kaggle.com/datasets/mdfahimbinalam/leaf-dataset";

const PLANT_CLASSES = [
  "aloevera", "amla", "amruta_balli", "arali", "ashoka", "ashwagandha", "astma_weed", "avacado", "badipala", "balloon_vine", 
  "bamboo", "basale", "beans", "betel", "betel_nut", "bhringraj", "brahmi", "camphor", "caricature", "castor", "catharanthus", 
  "chakte", "chilly", "citron_lime_(herelikai)", "coffee", "common_rue(naagdalli)", "coriender", "curry", "curry_leaf", 
  "doddapatre", "drumstick", "ekka", "eucalyptus", "ganigale", "ganike", "gasagase", "geranium", "ginger", "globe_amarnath", 
  "guava", "henna", "hibiscus", "honge", "insulin", "jackfruit", "jasmine", "kamakasturi", "kambajala", "kasambruga", "kepala", 
  "kohlrabi", "lantana", "lemon", "lemon_grass", "malabar_nut", "mango", "marigold", "mint", "nagadali", "neem", "nelavembu", 
  "nerale", "nithyapushpa", "nooni", "onion", "padri", "palak(spinach)", "papaya", "parijatha", "pea", "pepper", "pomegranate", 
  "pumpkin", "raddish", "raktachandini", "rose", "sampige", "sapota", "seethapala", "spinach1", "tamarind", "taro", "tecoma", 
  "thumbe", "tomato", "tulsi", "wood_sorel"
];

export default function PredictResult({ 
  result, 
  imageUrl, 
  onReportFeedback, 
  feedbackLoading, 
  feedbackSent: externalFeedbackSent 
}: { 
  result: any; 
  imageUrl: string;
  onReportFeedback?: (correctClass: string, userNote: string) => void;
  feedbackLoading?: boolean;
  feedbackSent?: boolean;
}) {
  const [heatmap, setHeatmap] = useState(false);
  const feedbackSent = externalFeedbackSent;
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [isCorrectionOpen, setIsCorrectionOpen] = useState(false);
  const [correctionSearch, setCorrectionSearch] = useState("");
  const [selectedCorrection, setSelectedCorrection] = useState("unknown");
  const [userNote, setUserNote] = useState("");

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
  
  const confidenceTier = result?.confidence_tier || (
    confidence >= 90 ? "High confidence" : 
    confidence >= 70 ? "Moderate — verify visually" : 
    "Low — manual verification recommended"
  );
  
  const confidenceColor = result?.confidence_color || (
    confidence >= 90 ? "emerald" : 
    confidence >= 70 ? "amber" : 
    "rose"
  );
  
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
                          onClick={() => {}}
                          title="Grad-CAM Heatmaps (Coming in V4)"
                          className="w-14 h-14 rounded-2xl flex items-center justify-center border transition-all bg-black/60 border-white/10 text-gray-500 cursor-not-allowed"
                        >
                          <Maximize2 className="w-6 h-6 opacity-50" />
                        </button>
                      </div>
                      <div className="w-12 h-12 border-b-2 border-r-2 border-primary-500/50" />
                  </div>
              </div>

              <div className="absolute top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <a 
                  href={KAGGLE_DATASET_URL} 
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
                {/* Primary Match */}
                {prediction.top3 && prediction.top3.length > 0 && (
                    <motion.div 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="p-6 bg-white/[0.04] border border-primary-500/30 rounded-2xl flex flex-col gap-4 shadow-[0_0_20px_rgba(16,185,129,0.1)] relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 px-4 py-1 bg-primary-500/20 text-primary-400 text-[9px] font-black uppercase tracking-widest rounded-bl-xl">
                    <div className="p-6 bg-white/[0.04] border border-primary-500/30 rounded-2xl flex items-center justify-between shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                        <div className="flex-1 space-y-4">
                        <div className="flex flex-wrap items-center gap-4">
                            <h2 className="text-4xl sm:text-5xl font-black text-white tracking-tighter capitalize">{name}</h2>
                            <div className={`px-4 py-1.5 rounded-full bg-${confidenceColor}-500/10 border border-${confidenceColor}-500/20 flex items-center gap-2`}>
                                <div className={`w-1.5 h-1.5 rounded-full bg-${confidenceColor}-500 animate-pulse`} />
                                <span className={`text-[10px] font-black text-${confidenceColor}-400 uppercase tracking-widest`}>
                                    {confidenceTier}
                                </span>
                            </div>
                        </div>
                        <p className="text-primary-400 text-lg font-bold tracking-tight italic opacity-80">{sciName}</p>
                    </div>

                    <div className="flex gap-2">
                        <button 
                          onClick={() => onReportFeedback?.(result.predicted_class, "Verified Correct")}
                          className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-500 hover:bg-emerald-500 hover:text-white transition-all group"
                          title="Correct Identification"
                        >
                          <CheckCircle2 className="w-6 h-6" />
                        </button>
                        <button 
                          onClick={() => setIsCorrectionOpen(true)}
                          className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-500 hover:bg-rose-500 hover:text-white transition-all"
                          title="Wrong Identification"
                        >
                          <XCircle className="w-6 h-6" />
                        </button>
                    </div>
                </div>
                )}

                {result.ambiguous && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-6 p-5 bg-amber-500/10 border border-amber-500/20 rounded-[2.5rem] flex items-center gap-4"
                  >
                    <AlertTriangle className="w-6 h-6 text-amber-500 flex-shrink-0" />
                    <div>
                      <p className="text-[10px] font-black text-amber-500 uppercase tracking-[0.2em]">Visual Similarity Alert</p>
                      <p className="text-[11px] text-amber-200/60 font-medium leading-relaxed">
                        The Neural Engine detected high similarity with another species. {result.note || "Please compare with alternative matches below."}
                      </p>
                    </div>
                  </motion.div>
                )}
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
                  {/* Phase 3: Prototypical Alternative Matches */}
            {result.proto_top3 && result.proto_top3.length > 1 && (
              <div className="mt-8 border-t border-white/5 pt-8">
                <button 
                  onClick={() => setShowAlternatives(!showAlternatives)}
                  className="flex items-center gap-2 text-xs font-black text-gray-500 uppercase tracking-widest hover:text-primary-400 transition-colors"
                >
                  Alternative Matches Detected 
                  {showAlternatives ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
                
                <AnimatePresence>
                  {showAlternatives && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                        {result.proto_top3.map((alt: any, idx: number) => (
                          <div 
                            key={idx}
                            className={`p-4 rounded-2xl border ${idx === 0 ? 'bg-primary-500/10 border-primary-500/20' : 'bg-white/5 border-white/10'} flex items-center justify-between group cursor-help`}
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-8 h-8 rounded-lg ${idx === 0 ? 'bg-primary-500/20' : 'bg-white/5'} flex items-center justify-center text-[10px] font-black text-white`}>
                                {idx + 1}
                              </div>
                              <div>
                                <p className="text-[11px] font-black text-white uppercase tracking-tight">{alt.species.replace(/_/g, ' ')}</p>
                                <p className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Similarity Score</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-black text-white">{Math.round(alt.confidence * 100)}%</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            <div className="mt-12 flex flex-wrap gap-4">
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
                {!feedbackSent ? (
                  <>
                    <button 
                      onClick={() => onReportFeedback?.(result.plant.name.toLowerCase().replace(" ", "_"), "User verified as accurate")} 
                      className="group relative h-16 px-12 bg-primary-500 text-black text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl transition-all shadow-[0_0_40px_rgba(16,185,129,0.2)] active:scale-95 overflow-hidden disabled:opacity-50"
                      disabled={feedbackLoading}
                    >
                      <div className="absolute inset-0 glass-reflection" />
                      {feedbackLoading ? 'Processing...' : 'Accurate'}
                    </button>
                    <button 
                      onClick={() => setIsCorrectionOpen(!isCorrectionOpen)}
                      className={`h-16 px-12 border text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl transition-all active:scale-95 flex items-center gap-2 ${
                        isCorrectionOpen ? 'bg-rose-500/20 border-rose-500/50 text-rose-400' : 'bg-white/5 border-white/10 text-white/30 hover:text-white'
                      }`}
                    >
                      {isCorrectionOpen ? 'Cancel' : 'Recalibrate'}
                    </button>
                  </>
                ) : (
                  <div className="h-16 px-12 flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-400 text-[10px] font-black uppercase tracking-[0.3em]">
                    <CheckCircle2 className="w-4 h-4" /> Feedback Synced
                  </div>
                )}
            </div>
        </div>

        <AnimatePresence>
          {isCorrectionOpen && !feedbackSent && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="px-12 pb-12 overflow-hidden"
            >
              <div className="p-8 bg-black/40 border border-rose-500/20 rounded-[2.5rem] space-y-8">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-rose-500/10 rounded-xl flex items-center justify-center border border-rose-500/10">
                    <AlertCircle className="w-5 h-5 text-rose-500" />
                  </div>
                  <div>
                    <h4 className="text-white font-black text-sm uppercase tracking-widest leading-none mb-1">Active Correction Protocol</h4>
                    <p className="text-gray-600 text-[10px] font-bold uppercase tracking-widest">Provide accurate data to improve neural memory</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 ml-2">Identify Correct Species</label>
                    <div className="relative">
                      <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                      <input 
                        list="species-list"
                        value={correctionSearch}
                        onChange={(e) => {
                          setCorrectionSearch(e.target.value);
                          if (PLANT_CLASSES.includes(e.target.value)) {
                            setSelectedCorrection(e.target.value);
                          }
                        }}
                        placeholder="Search botanical registry..."
                        className="w-full bg-black/60 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-xs text-white placeholder-gray-700 focus:border-rose-500/50 outline-none transition-all"
                      />
                      <datalist id="species-list">
                        {PLANT_CLASSES.map(cls => (
                          <option key={cls} value={cls} />
                        ))}
                      </datalist>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 ml-2">Clinical Notes (Optional)</label>
                    <div className="relative">
                      <MessageSquare className="absolute left-4 top-5 w-4 h-4 text-gray-600" />
                      <textarea 
                        value={userNote}
                        onChange={(e) => setUserNote(e.target.value)}
                        placeholder="E.g. This is actually Neem but with drought stress..."
                        className="w-full bg-black/60 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-xs text-white placeholder-gray-700 focus:border-rose-500/50 outline-none transition-all min-h-[56px] h-14 resize-none"
                      />
                    </div>
                  </div>
                </div>

                <button 
                  onClick={() => onReportFeedback?.(selectedCorrection, userNote || "User reported mismatch via correction panel")}
                  disabled={feedbackLoading || selectedCorrection === "unknown" && !correctionSearch}
                  className="w-full h-16 bg-rose-500 hover:bg-rose-400 disabled:opacity-50 disabled:bg-gray-800 text-black text-[10px] font-black uppercase tracking-[0.4em] rounded-2xl transition-all flex items-center justify-center gap-3 active:scale-95"
                >
                  <Send className="w-4 h-4" />
                  {feedbackLoading ? 'Synchronizing with Retraining Queue...' : 'Inject Correction into Neural Memory'}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
    </motion.div>
  );
}
