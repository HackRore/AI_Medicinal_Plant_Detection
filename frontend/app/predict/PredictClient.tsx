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
import { APP_VERSION } from "@/lib/constants"

import { getApiBase } from "@/utils/api";

const THINKING_STEPS = [
  { icon: "🔬", text: "Waking inference engine... (first request ~30s)", time: 0 },
  { icon: "🌿", text: "Processing leaf signature...", time: 8000 },
  { icon: "🧬", text: "Cross-checking with Gemini Vision...", time: 20000 },
]

function AIThinkingOverlay({ isVisible }: { isVisible: boolean }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setElapsed(0)
      return
    }
    const startTime = Date.now()
    const interval = setInterval(() => {
      const ms = Date.now() - startTime
      setElapsed(ms)
      
      let step = 0
      if (ms >= 20000) step = 2
      else if (ms >= 8000) step = 1
      
      setCurrentStep(step)
    }, 100)
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
            className="flex items-center gap-3"
          >
            <span className="text-base w-6">{step.icon}</span>
            <span className={`text-xs font-bold flex-1 ${
              i === currentStep ? 'text-white' :
              i < currentStep ? 'text-gray-500 line-through' :
              'text-gray-600'
            }`}>
              {step.text}
            </span>
            {i < currentStep && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-primary-400 text-xs"
              >✓</motion.span>
            )}
            {i === currentStep && (
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                className="text-primary-400 text-xs inline-block w-3 h-3 border-2 border-primary-400 border-t-transparent rounded-full"
              />
            )}
          </motion.div>
        ))}
      </div>
      <div className="mt-5 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-primary-400 rounded-full"
          animate={{ width: `${Math.min((elapsed / 30000) * 100, 100)}%` }}
          transition={{ duration: 0.1 }}
        />
      </div>
      
      {elapsed > 35000 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl"
        >
          <p className="text-[9px] text-amber-400 uppercase tracking-widest text-center">
            Backend is cold-starting on free tier. This only happens once per session.
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}

export default function PredictClient() {
  const [preview, setPreview] = useState<string | null>(null)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [uploadedImages, setUploadedImages] = useState<{file: File | null, preview: string}[]>([])
  const [remoteUrl, setRemoteUrl] = useState("")
  const [localHistory, setLocalHistory] = useState<any[]>([])
  const resultRef = useRef<HTMLDivElement>(null)
  const [activeModule, setActiveModule] = useState<'scanner' | 'symptoms'>('scanner')
  const [symptoms, setSymptoms] = useState("")
  const [useScaleReference, setUseScaleReference] = useState(false)
  const [symptomResults, setSymptomResults] = useState<any>(null)
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [feedbackLoading, setFeedbackLoading] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const API_BASE = getApiBase()

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("plantoai_onboarded")) {
      setShowOnboarding(true)
    }
  }, [])

  const dismissOnboarding = () => {
    localStorage.setItem("plantoai_onboarded", "true")
    setShowOnboarding(false)
  }

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
    mutationFn: async ({ file, url }: { file?: File, url?: string }) => {
      const formData = new FormData()
      if (file) formData.append("file", file)
      if (url) formData.append("url", url)
      if (useScaleReference) formData.append("scale_reference", "true")
      
      const endpoint = url ? `${API_BASE}/api/v1/predict-url` : `${API_BASE}/api/v1/predict`
      const res = await fetch(endpoint, {
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
    predictMutation.mutate({ file })
  }

  const handleUrlSubmit = () => {
    if (!remoteUrl) return
    updatePreview(remoteUrl)
    setUploadedImages([{file: null, preview: remoteUrl}])
    predictMutation.mutate({ url: remoteUrl })
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
            predictMutation.mutate({ file })
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
      
      <header className="text-center space-y-10 mb-24 relative z-20">
        <motion.div 
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className="inline-flex items-center gap-4 px-8 py-3 bg-black/40 backdrop-blur-xl border border-primary-500/30 rounded-full mb-4 shadow-[0_0_50px_rgba(16,185,129,0.15)] overflow-hidden relative group"
        >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-500/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-[1.5s]" />
            <div className="w-2 h-2 rounded-full bg-primary-500 shadow-[0_0_10px_rgba(16,185,129,1)] animate-ping" />
            <span className="text-[10px] font-black uppercase tracking-[0.5em] text-primary-400 drop-shadow-md">Spec {APP_VERSION} Tactical Neural Lens</span>
        </motion.div>
        
        <h1 className="text-7xl md:text-[9rem] font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500 tracking-tighter leading-[0.8] uppercase drop-shadow-[0_0_40px_rgba(255,255,255,0.1)]">
          Neural <br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-teal-600 drop-shadow-[0_0_80px_rgba(16,185,129,0.3)]">Scanner</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-400 font-medium max-w-3xl mx-auto italic leading-relaxed">
          Initialize the world's most precise botanical identification engine. Upload the bio-signature for immediate Ayurvedic decoding.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center gap-6 pt-16 relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent -z-10" />
          <button 
            onClick={() => setActiveModule('scanner')}
            className={`group relative h-20 md:h-24 px-12 md:px-16 rounded-[2.5rem] font-black uppercase tracking-[0.3em] transition-all overflow-hidden ${
                activeModule === 'scanner' ? 'bg-white text-black shadow-[0_0_80px_rgba(255,255,255,0.2)] scale-105' : 'bg-black/50 backdrop-blur-xl text-gray-500 border border-white/10 hover:border-white/30'
            }`}
          >
            {activeModule === 'scanner' && <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />}
            Target Acq
          </button>
          <button 
            onClick={() => setActiveModule('symptoms')}
            className={`group relative h-20 md:h-24 px-12 md:px-16 rounded-[2.5rem] font-black uppercase tracking-[0.3em] transition-all overflow-hidden ${
                activeModule === 'symptoms' ? 'bg-white text-black shadow-[0_0_80px_rgba(255,255,255,0.2)] scale-105' : 'bg-black/50 backdrop-blur-xl text-gray-500 border border-white/10 hover:border-white/30'
            }`}
          >
            {activeModule === 'symptoms' && <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />}
            Symptoms
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
                
                {showOnboarding && (
                  <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-primary-500/10 border border-primary-500/30 rounded-[2.5rem] relative"
                  >
                    <button 
                      onClick={dismissOnboarding}
                      className="absolute top-6 right-6 text-[10px] font-black uppercase tracking-widest text-primary-500 hover:text-white transition-colors"
                    >
                      Got it
                    </button>
                    <h3 className="text-sm font-black text-white uppercase tracking-widest mb-3">Welcome to Neural Scanner</h3>
                    <ul className="text-xs text-gray-400 space-y-2 list-disc pl-4 font-medium leading-relaxed">
                      <li><span className="text-white">Supported:</span> 46 medicinal species (Neem, Tulsi, Aloe Vera, Ashwagandha...)</li>
                      <li><span className="text-white">For best results:</span> single leaf, plain background, good lighting, photo taken straight-on</li>
                      <li><span className="text-white">Not supported:</span> flowers, fruit, whole plants, or non-Indian species</li>
                    </ul>
                  </motion.div>
                )}

                <div className="grid md:grid-cols-2 gap-8 relative">
                  {/* Tactical Crosshairs */}
                  <div className="absolute -inset-8 border border-white/[0.03] rounded-[4rem] pointer-events-none" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-primary-500/30 flex items-center justify-center pointer-events-none">
                     <div className="w-full h-[1px] bg-current" />
                     <div className="w-[1px] h-full bg-current absolute" />
                  </div>

                  <label className="group relative cursor-pointer block h-80 bg-black/40 backdrop-blur-2xl border border-white/10 rounded-[3rem] hover:border-primary-500/60 hover:bg-primary-900/10 transition-all text-center overflow-hidden shadow-[0_0_0_rgba(16,185,129,0)] hover:shadow-[0_0_60px_rgba(16,185,129,0.15)] flex flex-col items-center justify-center transform-gpu hover:-translate-y-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-primary-500 to-transparent translate-y-[-100%] group-hover:translate-y-[4000%] transition-transform duration-[3s] ease-in-out" />
                    <input type="file" accept="image/*" onChange={handleFileSelect} className="sr-only" disabled={predictMutation.isPending} />
                    
                    <div className="relative">
                        <div className="absolute inset-0 bg-primary-500/20 blur-2xl rounded-full scale-0 group-hover:scale-150 transition-transform duration-700" />
                        <Upload className="relative z-10 h-20 w-20 text-gray-500 group-hover:text-primary-400 mb-8 transition-all duration-500 group-hover:scale-110" />
                    </div>
                    
                    <p className="font-black text-white uppercase tracking-[0.4em] text-xs relative z-10">Inject Image Data</p>
                    <p className="font-bold text-gray-600 uppercase tracking-widest text-[9px] mt-3 relative z-10">High Res Signature Required</p>
                  </label>
                  
                  <button 
                    onClick={() => setIsCameraOpen(true)} 
                    className="group relative h-80 bg-black/40 backdrop-blur-2xl border border-white/10 rounded-[3rem] hover:border-teal-500/60 hover:bg-teal-900/10 transition-all text-center overflow-hidden shadow-[0_0_0_rgba(20,184,166,0)] hover:shadow-[0_0_60px_rgba(20,184,166,0.15)] flex flex-col items-center justify-center transform-gpu hover:-translate-y-2"
                    disabled={predictMutation.isPending}
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                    <div className="absolute bottom-0 left-0 w-[2px] h-full bg-gradient-to-b from-transparent via-teal-500 to-transparent translate-x-[-100%] group-hover:translate-x-[4000%] transition-transform duration-[3s] ease-in-out" />
                    
                    <div className="relative">
                        <div className="absolute inset-0 bg-teal-500/20 blur-2xl rounded-full scale-0 group-hover:scale-150 transition-transform duration-700" />
                        <Camera className="relative z-10 h-20 w-20 text-gray-500 group-hover:text-teal-400 mb-8 transition-all duration-500 group-hover:scale-110" />
                    </div>

                    <p className="font-black text-white uppercase tracking-[0.4em] text-xs relative z-10">Live Scanner</p>
                    <p className="font-bold text-gray-600 uppercase tracking-widest text-[9px] mt-3 relative z-10">Engage Optical Sensors</p>
                  </button>
                </div>

                {/* Neural Remote Scan - URL Feature */}
                <div className="glass-card p-6 rounded-[2.5rem] border border-white/5 bg-white/[0.01]">
                   <p className="text-[9px] font-black text-primary-500/60 uppercase tracking-[0.4em] mb-4 ml-2">Neural Remote Scan</p>
                   <div className="flex gap-4">
                      <input 
                        type="text" 
                        value={remoteUrl}
                        onChange={(e) => setRemoteUrl(e.target.value)}
                        placeholder="Paste image URL (e.g. from iNaturalist)..."
                        className="flex-1 bg-black/40 border border-white/10 rounded-2xl px-6 text-sm text-white placeholder-gray-700 focus:border-primary-500/50 outline-none"
                      />
                      <Button 
                        onClick={handleUrlSubmit}
                        disabled={!remoteUrl || predictMutation.isPending}
                        className="h-14 px-8 rounded-2xl bg-white text-black font-black uppercase tracking-widest text-[10px]"
                      >
                         Execute
                      </Button>
                   </div>
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

                {/* Sample Leaf Images */}
                <div className="glass-card p-6 rounded-[2.5rem] border border-white/5 bg-white/[0.01]">
                   <p className="text-[9px] font-black text-primary-500/60 uppercase tracking-[0.4em] mb-4 ml-2">Try a sample</p>
                   <div className="flex gap-4">
                      {['neem.jpg', 'tulsi.jpg', 'aloe.jpg'].map(sample => (
                          <button
                            key={sample}
                            disabled={predictMutation.isPending}
                            onClick={() => {
                              toast.info(`Loading ${sample}...`);
                              fetch(`/samples/${sample}`)
                                .then(res => res.blob())
                                .then(blob => {
                                   const file = new File([blob], sample, { type: "image/jpeg" });
                                   setUploadedImages([{ file, preview: URL.createObjectURL(blob) }]);
                                   predictMutation.mutate({ file });
                                })
                                .catch(err => toast.error("Failed to load sample image"));
                            }}
                            className="flex-1 py-4 bg-black/40 border border-white/10 hover:border-primary-500/50 rounded-2xl text-[10px] text-gray-400 hover:text-white font-black uppercase tracking-widest transition-all"
                          >
                            {sample.replace('.jpg', '')}
                          </button>
                      ))}
                   </div>
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
                 
                 {/* Smart Rejection Panel: Not a leaf or poor image quality */}
                 {predictMutation.isSuccess && !predictMutation.data?.success && predictMutation.data?.error && (
                    <div className="space-y-6 p-8 rounded-[2.5rem] bg-amber-500/5 border border-amber-500/20">
                       <div className="flex items-start gap-4">
                         <span className="text-4xl shrink-0">{predictMutation.data.error === 'Not a Plant Leaf' ? '🌿' : '📷'}</span>
                         <div>
                           <h3 className="text-xl font-black text-amber-400 uppercase tracking-wider mb-2">{predictMutation.data.error}</h3>
                           <p className="text-gray-300 text-sm leading-relaxed">{predictMutation.data.message}</p>
                           {predictMutation.data.what_ai_sees && (
                             <p className="text-gray-500 text-xs mt-2 italic">Our AI sees: "{predictMutation.data.what_ai_sees}"</p>
                           )}
                         </div>
                       </div>
                       {predictMutation.data.user_guidance && (
                         <div className="p-4 rounded-2xl bg-primary-500/10 border border-primary-500/20">
                           <p className="text-[9px] font-black text-primary-500 uppercase tracking-widest mb-1">Tip</p>
                           <p className="text-primary-300 text-sm">{predictMutation.data.user_guidance}</p>
                         </div>
                       )}
                       {predictMutation.data.tips && (
                         <div className="space-y-2">
                           <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest">How to take a better photo</p>
                           {predictMutation.data.tips.map((tip: string, i: number) => (
                             <div key={i} className="flex items-start gap-3 text-xs text-gray-400">
                               <span className="text-primary-500 font-black shrink-0">{i + 1}.</span>
                               <span>{tip}</span>
                             </div>
                           ))}
                         </div>
                       )}
                       <button
                         onClick={() => { predictMutation.reset(); setPreview(null); setUploadedImages([]) }}
                         className="w-full py-4 rounded-2xl bg-primary-500 hover:bg-primary-400 text-black font-black uppercase tracking-wider text-sm transition-all"
                       >
                         Try Again with a Better Photo
                       </button>
                    </div>
                 )}

                 {predictMutation.isSuccess && predictMutation.data?.success && (
                    <PredictResult 
                      result={predictMutation.data} 
                      imageUrl={uploadedImages[0]?.preview || preview || ""} 
                    />
                 )}
                 
                 {predictMutation.isSuccess && predictMutation.data?.success && (
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
                
                {/* Example Chips */}
                <div className="flex flex-wrap gap-3 mb-4 ml-4">
                  {[
                    "I have joint pain and swelling",
                    "Fever with digestive issues",
                    "Skin rash and itching",
                    "Chronic fatigue and low immunity"
                  ].map((chip, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSymptoms(chip)}
                      className="px-4 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-primary-500/10 hover:text-primary-400 hover:border-primary-500/30 text-[10px] text-gray-400 transition-all uppercase tracking-widest"
                    >
                      {chip}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <textarea 
                    value={symptoms} 
                    onChange={e => setSymptoms(e.target.value)}
                    className="w-full h-56 rounded-[2.5rem] bg-white/[0.02] border border-white/10 p-12 focus:border-primary-500/50 outline-none text-2xl text-white placeholder-gray-800 transition-all font-medium shadow-inner"
                    placeholder="Describe your symptoms in detail, e.g. 'I have joint inflammation and digestive problems...'"
                  />
                  <div className={`absolute bottom-6 right-8 text-xs font-bold uppercase tracking-widest ${symptoms.length < 30 ? 'text-amber-500' : 'text-emerald-400'}`}>
                    {symptoms.length} / 30 min chars
                  </div>
                </div>
                
                <button 
                  onClick={() => symptomMutation.mutate(symptoms)} 
                  disabled={symptomMutation.isPending || symptoms.length < 30}
                  className="group relative w-full h-24 rounded-[2.5rem] bg-primary-500 hover:bg-primary-400 text-black font-black text-xl uppercase tracking-[0.3em] transition-all overflow-hidden shadow-[0_0_60px_rgba(16,185,129,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
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
