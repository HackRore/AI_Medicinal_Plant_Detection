'use client'

import { useState, useRef, useCallback, useEffect } from "react"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import confetti from "canvas-confetti"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/Button"
import { Camera, Upload, History, Leaf, ShieldAlert, Sparkles, Wand2 } from "lucide-react"
import PredictResult from "@/components/predict/PredictResult"
import { DisclaimerBanner } from "@/components/predict/DisclaimerBanner";
import DisclaimerModal from "@/components/predict/DisclaimerModal"
import { Card } from "@/components/ui/Card"
import React from "react"

import { getApiBase } from "@/utils/api";

const THINKING_STEPS = [
  { icon: "🔬", text: "Spectral Boundary Calibration..." },
  { icon: "🌿", text: "Neural Venation Extraction..." },
  { icon: "🧬", text: "Monolithic Cross-Reference (46 Species)..." },
  { icon: "🧪", text: "Clinical Mechanism Synthesis..." },
  { icon: "📚", text: "Ayurvedic Homeostasis Projection..." },
]

function AIThinkingOverlay({ isVisible }: { isVisible: boolean }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setCompletedSteps([])
      return
    }
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        setCompletedSteps(c => [...c, prev])
        return Math.min(prev + 1, THINKING_STEPS.length - 1)
      })
    }, 900)
    return () => clearInterval(interval)
  }, [isVisible])

  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="w-full max-w-md mx-auto mt-8 p-6 rounded-3xl border border-primary-500/20 bg-black/40 backdrop-blur-xl"
    >
      <div className="flex items-center gap-2 mb-5">
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="w-2 h-2 rounded-full bg-primary-400"
        />
        <span className="text-primary-400 text-[10px] font-black tracking-widest uppercase">
          Neural Forge Active
        </span>
      </div>
      <div className="space-y-3">
        {THINKING_STEPS.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: i <= currentStep ? 1 : 0.2, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center gap-3"
          >
            <span className="text-base w-6">{step.icon}</span>
            <span className={`text-xs font-bold flex-1 ${
              i === currentStep ? 'text-white' :
              completedSteps.includes(i) ? 'text-gray-500 line-through' :
              'text-gray-600'
            }`}>
              {step.text}
            </span>
            {completedSteps.includes(i) && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-primary-400 text-xs"
              >✓</motion.span>
            )}
          </motion.div>
        ))}
      </div>
      <div className="mt-5 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-primary-400 rounded-full"
          animate={{ width: `${((currentStep + 1) / THINKING_STEPS.length) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </motion.div>
  )
}

function ColdStartWarning({ isVisible }: { isVisible: boolean }) {
  const [show, setShow] = useState(false);
  
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isVisible) {
      timer = setTimeout(() => setShow(true), 5000); // Show after 5s of waiting
    } else {
      setShow(false);
    }
    return () => clearTimeout(timer);
  }, [isVisible]);

  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-center"
    >
      <p className="text-[10px] font-black text-amber-500 uppercase tracking-widest animate-pulse">
        Neural Engine Cold Start Detected
      </p>
      <p className="text-[9px] text-amber-200/50 uppercase tracking-tighter mt-1">
        Waking up the Render instance... This may take up to 30 seconds.
      </p>
    </motion.div>
  );
}

export default function PredictClient() {
  const [preview, setPreview] = useState<string | null>(null)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [uploadedImages, setUploadedImages] = useState<{file: File, preview: string}[]>([])
  const [localHistory, setLocalHistory] = useState<any[]>([])
  const resultRef = useRef<HTMLDivElement>(null)
  const [activeModule, setActiveModule] = useState<'scanner' | 'symptoms'>('scanner')
  const [symptoms, setSymptoms] = useState("")
  const [useScaleReference, setUseScaleReference] = useState(false)
  const [symptomResults, setSymptomResults] = useState<any>(null)
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [feedbackLoading, setFeedbackLoading] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const API_BASE = getApiBase()

  // Sprint 5: Report Mismatch — Active Learning Feedback Loop
  const reportMismatch = async () => {
    if (!uploadedImages[0]?.file || feedbackSent) return
    setFeedbackLoading(true)
    try {
      const formData = new FormData()
      formData.append("file", uploadedImages[0].file)
      formData.append("predicted_class", predictMutation.data?.plant?.name ?? "unknown")
      formData.append("correct_class", "unknown")
      formData.append("user_note", "User reported mismatch via UI")
      const res = await fetch(`${API_BASE}/api/v1/report-mismatch`, { method: "POST", body: formData })
      if (res.ok) {
        setFeedbackSent(true)
        toast.success("Thanks! This image helps train our AI to be smarter.")
      }
    } catch (e) {
      toast.error("Could not send feedback right now.")
    } finally {
      setFeedbackLoading(false)
    }
  }

  // Predict mutation
  const predictMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append("file", file)
      if (useScaleReference) {
        formData.append("scale_reference", "true")
      }
      
      const res = await fetch(`${API_BASE}/api/v1/predict`, {
        method: "POST",
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || "Prediction failed")
      }
      return res.json()
    },
    onSuccess: async (data: any) => {
      if (data?.success) {
        if ((data?.prediction?.confidence ?? 0) > 80) {
          confetti({ particleCount: 150, spread: 80, origin: { y: 0.7 } })
          toast.success(`Verified: ${data?.plant?.name ?? "Medicinal Plant"}`)
        }
        
        const newEntry = {
          id: Date.now().toString(),
          plant_name: data?.plant?.name ?? "Unknown Species",
          confidence: data?.prediction?.confidence ?? 0,
          thumb: uploadedImages[0]?.preview || preview || '',
          timestamp: Date.now()
        }
        const newHistory = [newEntry, ...localHistory].slice(0, 10)
        setLocalHistory(newHistory)
        localStorage.setItem('plantoai_history', JSON.stringify(newHistory))
      } else {
        toast.error(data?.message ?? "Identification failed")
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'AI engine is currently offline')
    }
  })

  // Symptom Search mutation
  const symptomMutation = useMutation({
    mutationFn: async (symptoms: string) => {
      const res = await fetch(`${API_BASE}/api/v1/symptom-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms })
      })
      if (!res.ok) throw new Error("Search failed")
      return res.json()
    },
    onSuccess: (data) => {
      setSymptomResults(data)
      if (data.error) toast.error(data.error)
      else toast.success("Ayurvedic remedies found!")
    }
  })

  // Auto-scroll to results
  useEffect(() => {
    if (predictMutation.isSuccess && resultRef.current) {
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 300)
    }
  }, [predictMutation.isSuccess])

  // Load local history on mount
  useEffect(() => {
    const saved = localStorage.getItem("plantoai_history")
    if (saved) {
      try {
        setLocalHistory(JSON.parse(saved).slice(0, 10))
      } catch (e) {
        console.error("Failed to load history", e)
      }
    }
  }, [])

  const previewRef = React.useRef<string | null>(null)

  // Memory Safeguard: Revoke object URLs to prevent leaks
  useEffect(() => {
    return () => {
      if (previewRef.current) URL.revokeObjectURL(previewRef.current)
    }
  }, [])

  const updatePreview = (url: string) => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current)
    previewRef.current = url
    setPreview(url)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).slice(0, 1)
    if (files.length === 0) return
    const file = files[0]
    const previewUrl = URL.createObjectURL(file)
    updatePreview(previewUrl)
    setUploadedImages([{file, preview: previewUrl}])
    predictMutation.mutate(file)
  }

  const handleCapture = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      canvasRef.current.width = videoRef.current.videoWidth
      canvasRef.current.height = videoRef.current.videoHeight
      const ctx = canvasRef.current.getContext("2d")
      if (ctx) {
        ctx.drawImage(videoRef.current!, 0, 0)
        canvasRef.current.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" })
            const url = URL.createObjectURL(blob)
            updatePreview(url)
            setUploadedImages([{file, preview: url}])
            predictMutation.mutate(file)
            setIsCameraOpen(false)
          }
        }, 'image/jpeg', 0.9)
      }
    }
  }, [predictMutation])

  useEffect(() => {
    let stream: MediaStream | null = null
    if (isCameraOpen && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(s => {
          stream = s
          if (videoRef.current) videoRef.current.srcObject = s
        })
        .catch(() => {
          toast.error("Camera access denied")
          setIsCameraOpen(false)
        })
    }
    return () => stream?.getTracks().forEach(t => t.stop())
  }, [isCameraOpen])

  return (
    <main className="container mx-auto p-6 pt-32 min-h-screen space-y-24 max-w-7xl relative z-10">
      <DisclaimerBanner />
      <DisclaimerModal />
      
      <header className="text-center space-y-8 mb-20">
        <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-3 px-6 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full mb-4 shadow-[0_0_30px_rgba(16,185,129,0.1)]"
        >
            <div className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-ping" />
            <span className="text-[9px] font-black uppercase tracking-[0.4em] text-primary-400">Spec v2.1 Tactical Neural Lens</span>
        </motion.div>
        
        <h1 className="text-7xl md:text-[8rem] font-black text-white tracking-tighter leading-none uppercase text-glow-white">
          Neural <span className="text-primary-500 text-glow">Scanner</span>
        </h1>
        
        <p className="text-xl text-gray-500 font-medium max-w-2xl mx-auto italic leading-relaxed">
          The world's most precise botanical identification engine. Trained on high-fidelity clinical datasets for superior Ayurvedic accuracy.
        </p>
        
        <div className="flex justify-center gap-8 pt-12">
          <button 
            onClick={() => setActiveModule('scanner')}
            className={`group relative h-20 px-12 rounded-[2rem] font-black uppercase tracking-[0.2em] transition-all overflow-hidden ${
                activeModule === 'scanner' ? 'bg-primary-500 text-black shadow-[0_0_50px_rgba(16,185,129,0.2)]' : 'bg-white/5 text-gray-500 border border-white/10'
            }`}
          >
            {activeModule === 'scanner' && <div className="absolute inset-0 glass-reflection" />}
            Neural Scanner
          </button>
          <button 
            onClick={() => setActiveModule('symptoms')}
            className={`group relative h-20 px-12 rounded-[2rem] font-black uppercase tracking-[0.2em] transition-all overflow-hidden ${
                activeModule === 'symptoms' ? 'bg-primary-500 text-black shadow-[0_0_50px_rgba(16,185,129,0.2)]' : 'bg-white/5 text-gray-500 border border-white/10'
            }`}
          >
            {activeModule === 'symptoms' && <div className="absolute inset-0 glass-reflection" />}
            Symptom Engine
          </button>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {activeModule === 'scanner' ? (
          <motion.div 
            key="scanner-module"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.8, ease: "circOut" }}
            className="space-y-16"
          >
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              <div className="space-y-12">
                <div className="grid md:grid-cols-2 gap-8">
                  <label className="group relative cursor-pointer block p-16 bg-white/[0.02] border-2 border-dashed border-white/10 rounded-[3rem] hover:border-primary-500/50 hover:bg-white/[0.05] transition-all text-center overflow-hidden">
                    <div className="scanline opacity-10" />
                    <input type="file" accept="image/*" onChange={handleFileSelect} className="sr-only" disabled={predictMutation.isPending} />
                    <Upload className="mx-auto h-16 w-16 text-gray-600 group-hover:text-primary-400 mb-8 transition-all group-hover:scale-110" />
                    <p className="font-black text-white uppercase tracking-[0.3em] text-xs">Upload Signature</p>
                  </label>
                  
                  <button 
                    onClick={() => setIsCameraOpen(true)} 
                    className="group relative p-16 bg-white/[0.02] border border-white/10 rounded-[3rem] hover:border-primary-500/50 hover:bg-white/[0.05] transition-all text-center overflow-hidden"
                    disabled={predictMutation.isPending}
                  >
                    <div className="scanline opacity-10" />
                    <Camera className="mx-auto h-16 w-16 text-gray-600 group-hover:text-primary-400 mb-8 transition-all group-hover:scale-110" />
                    <p className="font-black text-white uppercase tracking-[0.3em] text-xs">Neural Lens</p>
                  </button>
                </div>
                
                {/* Sprint 4: Scale Reference Toggle */}
                <div className="flex items-center justify-center gap-4 bg-white/[0.02] border border-white/10 p-4 rounded-3xl">
                  <input 
                    type="checkbox" 
                    id="scaleRefToggle" 
                    checked={useScaleReference} 
                    onChange={(e) => setUseScaleReference(e.target.checked)}
                    className="w-5 h-5 accent-primary-500 bg-black border-white/20 rounded cursor-pointer"
                  />
                  <label htmlFor="scaleRefToggle" className="cursor-pointer text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    Enable 1-Rupee Coin Scale Reference
                  </label>
                </div>

                {!predictMutation.isSuccess && !predictMutation.isPending && localHistory.length > 0 && (
                  <div className="space-y-6 pt-12 border-t border-white/5">
                    <h3 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-3">
                      <History className="h-4 w-4" /> Recent Insights
                    </h3>
                    <div className="grid grid-cols-5 gap-4">
                      {localHistory.map(item => (
                        <div key={item.id} className="aspect-square rounded-2xl overflow-hidden border border-white/10 group cursor-pointer relative">
                          <img src={item.thumb} alt="Scan" className="w-full h-full object-cover transition-transform group-hover:scale-110" />
                          <div className="absolute inset-0 bg-primary-500/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                             <Sparkles className="w-6 h-6 text-white" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div ref={resultRef}>
                 <AIThinkingOverlay isVisible={predictMutation.isPending} />
                 <ColdStartWarning isVisible={predictMutation.isPending} />
                 
                 {predictMutation.isSuccess && (
                    <PredictResult 
                      result={predictMutation.data} 
                      imageUrl={uploadedImages[0]?.preview || preview || ""} 
                    />
                 )}
                 
                 {predictMutation.isSuccess && (
                    <div className="mt-8 space-y-4">
                       {predictMutation.data?.vision_validation && (
                         <div className={`flex items-center gap-3 p-4 rounded-2xl border text-xs font-bold uppercase tracking-wider ${predictMutation.data.vision_validation.matches_prediction ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'}`}>
                           <span>{predictMutation.data.vision_validation.matches_prediction ? '✓' : '⚠'}</span>
                           <span>Gemini: {predictMutation.data.vision_validation.matches_prediction ? 'Confirmed' : 'Flagged'}</span>
                           <span className="ml-auto opacity-60">{Math.round((predictMutation.data.vision_validation.agreement_score ?? 0.5) * 100)}% agreement</span>
                         </div>
                       )}
                       {!feedbackSent ? (
                         <button onClick={reportMismatch} disabled={feedbackLoading}
                           className="w-full py-3 rounded-2xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 text-xs font-bold uppercase tracking-wider transition-all">
                           {feedbackLoading ? 'Sending...' : '⚡ Report Wrong ID — Help Train Our AI'}
                         </button>
                       ) : (
                         <div className="w-full py-3 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-xs font-bold uppercase tracking-wider text-center">✓ Feedback Received!</div>
                       )}
                       <div className="text-center">
                          <Button variant="outline" className="h-16 px-12 rounded-2xl border-white/10 hover:bg-white/5 text-gray-400 font-black uppercase tracking-widest text-[10px]"
                            onClick={() => { predictMutation.reset(); setPreview(null); setUploadedImages([]); setFeedbackSent(false) }}>
                            <Sparkles className="h-4 w-4 mr-2" /> Start New Neural Scan
                          </Button>
                       </div>
                    </div>
                 )}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="symptoms-module" 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-5xl mx-auto space-y-16"
          >
            <div className="glass-card rounded-[3rem] p-12 space-y-10 relative overflow-hidden">
              <div className="scanline opacity-5" />
              <div className="space-y-6">
                <label className="text-[10px] font-black uppercase tracking-[0.5em] text-primary-500/60 ml-4">Initialize Physiological Assessment</label>
                <textarea 
                  value={symptoms} 
                  onChange={e => setSymptoms(e.target.value)}
                  className="w-full h-56 rounded-[2.5rem] bg-white/[0.02] border border-white/10 p-12 focus:border-primary-500/50 outline-none text-2xl text-white placeholder-gray-800 transition-all font-medium shadow-inner"
                  placeholder="Describe symptoms for neural synthesis (e.g. chronic inflammation, digestive imbalance)..."
                />
                <button 
                  onClick={() => symptomMutation.mutate(symptoms)} 
                  disabled={symptomMutation.isPending || symptoms.length < 5}
                  className="group relative w-full h-24 rounded-[2.5rem] bg-primary-500 hover:bg-primary-400 text-black font-black text-xl uppercase tracking-[0.3em] transition-all overflow-hidden shadow-[0_0_60px_rgba(16,185,129,0.2)] active:scale-[0.98]"
                >
                  <div className="absolute inset-0 glass-reflection" />
                  {symptomMutation.isPending ? "Neural Synthesis in Progress..." : "Execute Clinical Analysis"}
                </button>
              </div>
            </div>

            {symptomResults && !symptomResults.error && (
              <div className="space-y-12">
                {/* Results Grid */}
                <div className="grid md:grid-cols-3 gap-8">
                  {(symptomResults?.recommendations ?? []).map((rec: any, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 20, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{ delay: i * 0.12 }}
                      className="glass-card rounded-[2.5rem] group hover:border-primary-500/40 transition-all relative overflow-hidden flex flex-col"
                    >
                      <div className="scanline opacity-10" />
                      {/* Rank badge + top bar */}
                      <div className="h-1 bg-gradient-to-r from-primary-600 to-emerald-400 w-0 group-hover:w-full transition-all duration-500" />
                      <div className="p-8 flex flex-col flex-1 gap-4">
                        <div className="flex items-start justify-between">
                          <span className="text-[9px] font-black text-primary-500/50 uppercase tracking-widest bg-primary-500/10 px-3 py-1 rounded-full">#{rec?.rank ?? i+1}</span>
                          <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase tracking-widest">Verified</span>
                        </div>
                        <div>
                          <h4 className="text-2xl font-black text-white tracking-tighter group-hover:text-primary-400 transition-colors">{rec?.plant || "Medicinal Herb"}</h4>
                          <p className="text-[10px] text-primary-500/60 italic mt-1">{rec?.scientific_name} · {rec?.ayurvedic_name}</p>
                        </div>
                        <p className="text-sm text-gray-400 leading-relaxed">{rec?.why}</p>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/5">
                            <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1">Dosha Effect</p>
                            <p className="text-[11px] text-emerald-400 font-medium">{rec?.dosha_effect}</p>
                          </div>
                          <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/5">
                            <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1">Safety</p>
                            <p className="text-[11px] text-amber-400 font-medium">{rec?.safety?.slice(0, 50)}...</p>
                          </div>
                        </div>
                        <div className="pt-4 border-t border-white/5 space-y-2">
                          <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest">Preparation</p>
                          <p className="text-xs text-gray-400 leading-relaxed">{rec?.preparation}</p>
                        </div>
                        <div className="pt-3 border-t border-white/5">
                          <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1">Dosage</p>
                          <p className="text-xs text-gray-400">{rec?.dosage}</p>
                        </div>
                        <p className="text-[9px] text-gray-700 italic mt-auto pt-3 border-t border-white/5">{rec?.classical_reference}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Lifestyle + Diet cards */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="grid md:grid-cols-2 gap-8">
                  <div className="glass-card p-10 rounded-[2.5rem]">
                    <p className="text-[9px] font-black text-primary-500/60 uppercase tracking-widest mb-3">☀️ Lifestyle Protocol</p>
                    <p className="text-gray-300 text-sm leading-relaxed">{symptomResults.lifestyle_advice}</p>
                  </div>
                  <div className="glass-card p-10 rounded-[2.5rem]">
                    <p className="text-[9px] font-black text-teal-500/60 uppercase tracking-widest mb-3">🌙 Dietary Guidance</p>
                    <p className="text-gray-300 text-sm leading-relaxed">{symptomResults.diet_tip}</p>
                  </div>
                </motion.div>

                {/* Medical Disclaimer */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="p-6 rounded-3xl bg-amber-500/5 border border-amber-500/20 flex gap-4">
                  <span className="text-2xl shrink-0">⚠️</span>
                  <div>
                    <p className="text-[9px] font-black text-amber-500 uppercase tracking-widest mb-1">Medical Disclaimer</p>
                    <p className="text-xs text-gray-500 leading-relaxed">{symptomResults.warning}</p>
                  </div>
                </motion.div>
              </div>
            )}
            {symptomResults?.error && (
              <div className="text-center p-12 glass-card rounded-[2.5rem]">
                <p className="text-amber-400 font-bold">{symptomResults.error}</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Camera Modal */}
      <AnimatePresence>
        {isCameraOpen && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/95 z-[100] flex items-center justify-center p-6 backdrop-blur-md"
            >
              <div className="bg-zinc-900 border border-white/10 rounded-[60px] max-w-xl w-full overflow-hidden shadow-2xl">
                <div className="p-10 border-b border-white/5 flex justify-between items-center">
                  <h3 className="text-xl font-black text-white flex gap-3 items-center uppercase tracking-widest">
                    <Camera className="h-6 h-6 text-primary-400" /> Neural Lens
                  </h3>
                </div>
                <div className="p-8 relative">
                  <div className="scanner-line" />
                  <video ref={videoRef} autoPlay playsInline className="w-full rounded-[40px] aspect-[4/3] object-cover scale-x-[-1]" />
                  <canvas ref={canvasRef} className="hidden" />
                </div>
                <div className="p-10 flex gap-6">
                  <Button className="flex-1 h-20 rounded-[30px] bg-primary-500 text-black font-black text-lg uppercase tracking-widest" onClick={handleCapture}>Capture</Button>
                  <Button variant="outline" className="flex-1 h-20 rounded-[30px] border-white/10 text-white font-black uppercase tracking-widest text-xs" onClick={() => setIsCameraOpen(false)}>Abort</Button>
                </div>
              </div>
            </motion.div>
        )}
      </AnimatePresence>
    </main>
  )
}
