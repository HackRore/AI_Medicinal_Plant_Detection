/**
 * PlantoAI: Neural Scanner Page
 * G9 Production Spec v2.0 - Zero Dummy Architecture
 */
'use client'

import { useState, useRef, useCallback, useEffect } from "react"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import confetti from "canvas-confetti"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/Button"
import { Camera, Upload, History, Leaf, ShieldAlert, Sparkles, Wand2 } from "lucide-react"
import PredictResult from "@/components/predict/PredictResult"
import { Card } from "@/components/ui/Card"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const THINKING_STEPS = [
  { icon: "🔬", text: "Detecting leaf edges and boundaries..." },
  { icon: "🌿", text: "Analyzing venation patterns and texture..." },
  { icon: "🧬", text: "Matching against 12 G9-Verified Species..." },
  { icon: "🧪", text: "Generating Grad-CAM morphological proof..." },
  { icon: "📚", text: "Syncing Ayurvedic Knowledge Base..." },
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

export default function PredictPage() {
  const [preview, setPreview] = useState<string | null>(null)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [uploadedImages, setUploadedImages] = useState<{file: File, preview: string}[]>([])
  const [localHistory, setLocalHistory] = useState<any[]>([])
  const [activeModule, setActiveModule] = useState<'scanner' | 'symptoms'>('scanner')
  const [symptoms, setSymptoms] = useState("")
  const [symptomResults, setSymptomResults] = useState<any>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

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

  // Predict mutation
  const predictMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append("file", file)
      
      const res = await fetch(`${API_BASE}/predict`, {
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).slice(0, 1)
    if (files.length === 0) return
    const file = files[0]
    const previewUrl = URL.createObjectURL(file)
    setPreview(previewUrl)
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
            setPreview(url)
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
    <main className="container mx-auto p-6 pt-32 min-h-screen space-y-12 max-w-6xl">
      <header className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full mb-4">
            <Wand2 className="w-4 h-4 text-primary-400" />
            <span className="text-[10px] font-black uppercase tracking-widest text-primary-400">Spec v2.0 Production AI</span>
        </div>
        <h1 className="text-6xl md:text-7xl font-black text-white tracking-tighter">
          Planto<span className="text-primary-400">AI</span>
        </h1>
        <p className="text-gray-500 font-medium max-w-2xl mx-auto italic">
          Zero-dummy identification engine. Trained on real Kaggle datasets for clinical Ayurvedic precision.
        </p>
        
        <div className="flex justify-center gap-4 pt-8">
          <Button 
            onClick={() => setActiveModule('scanner')}
            className={`rounded-2xl px-8 h-12 font-black uppercase tracking-widest transition-all ${
                activeModule === 'scanner' ? 'bg-primary-500 text-black' : 'bg-white/5 text-gray-400 border border-white/10'
            }`}
          >
            Neural Scanner
          </Button>
          <Button 
            onClick={() => setActiveModule('symptoms')}
            className={`rounded-2xl px-8 h-12 font-black uppercase tracking-widest transition-all ${
                activeModule === 'symptoms' ? 'bg-primary-500 text-black' : 'bg-white/5 text-gray-400 border border-white/10'
            }`}
          >
            Symptom Search
          </Button>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {activeModule === 'scanner' ? (
          <motion.div 
            key="scanner-module"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="space-y-12"
          >
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="space-y-8">
                <div className="grid md:grid-cols-2 gap-6">
                  <label className="group cursor-pointer block p-12 border-2 border-dashed border-white/10 rounded-[40px] hover:border-primary-500/50 hover:bg-white/5 transition-all text-center">
                    <input type="file" accept="image/*" onChange={handleFileSelect} className="sr-only" disabled={predictMutation.isPending} />
                    <Upload className="mx-auto h-12 w-12 text-gray-600 group-hover:text-primary-400 mb-6 transition-colors" />
                    <p className="font-black text-white uppercase tracking-widest text-xs">Upload Leaf</p>
                  </label>
                  <button 
                    onClick={() => setIsCameraOpen(true)} 
                    className="group p-12 bg-white/5 border border-white/10 rounded-[40px] hover:border-primary-500/50 hover:bg-white/10 transition-all text-center"
                    disabled={predictMutation.isPending}
                  >
                    <Camera className="mx-auto h-12 w-12 text-gray-600 group-hover:text-primary-400 mb-6 transition-colors" />
                    <p className="font-black text-white uppercase tracking-widest text-xs">Live Camera</p>
                  </button>
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

              <div>
                 <AIThinkingOverlay isVisible={predictMutation.isPending} />
                 
                 {predictMutation.isSuccess && (
                    <PredictResult 
                      result={predictMutation.data} 
                      imageUrl={uploadedImages[0]?.preview || preview || ""} 
                    />
                 )}
                 
                 {predictMutation.isSuccess && (
                    <div className="mt-8 text-center">
                       <Button 
                         variant="outline" 
                         className="h-16 px-12 rounded-2xl border-white/10 hover:bg-white/5 text-gray-400 font-black uppercase tracking-widest text-[10px]"
                         onClick={() => {
                           predictMutation.reset()
                           setPreview(null)
                           setUploadedImages([])
                         }}
                       >
                         <Sparkles className="h-4 w-4 mr-2" /> Start New Neural Scan
                       </Button>
                    </div>
                 )}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="symptoms-module" 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-4xl mx-auto space-y-12"
          >
            <div className="bg-black/60 border border-white/10 rounded-[40px] p-10 space-y-8 backdrop-blur-2xl">
              <div className="space-y-4">
                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">Describe Physiological Symptoms</label>
                <textarea 
                  value={symptoms} 
                  onChange={e => setSymptoms(e.target.value)}
                  className="w-full h-48 rounded-[32px] bg-white/5 border border-white/10 p-10 focus:border-primary-500/50 outline-none text-xl text-white placeholder-gray-700 transition-all font-medium"
                  placeholder="e.g. chronic cough, persistent indigestion, joint inflammation..."
                />
                <Button 
                  onClick={() => symptomMutation.mutate(symptoms)} 
                  disabled={symptomMutation.isPending || symptoms.length < 3}
                  className="w-full h-20 rounded-[32px] bg-primary-500 hover:bg-primary-400 text-black font-black text-lg uppercase tracking-widest shadow-2xl shadow-primary-500/20 active:scale-[0.98] transition-all"
                >
                  {symptomMutation.isPending ? "Consulting Botanical Repository..." : "Analyze Symptoms"}
                </Button>
              </div>
            </div>

            {symptomResults && (
              <div className="grid md:grid-cols-3 gap-8">
                {symptomResults.recommendations?.map((rec: any, i: number) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="p-8 bg-white/5 border border-white/5 text-white rounded-[32px] hover:border-primary-500/20 transition-all"
                  >
                    <h4 className="text-2xl font-black text-primary-400 mb-3 tracking-tighter">{rec.plant}</h4>
                    <p className="text-sm text-gray-400 font-medium mb-6 leading-relaxed">"{rec.why}"</p>
                    <div className="pt-6 border-t border-white/5">
                      <p className="text-[10px] font-black uppercase text-gray-500 tracking-widest mb-2">Ayurvedic Prep</p>
                      <p className="text-xs text-gray-300 font-bold">{rec.preparation}</p>
                    </div>
                  </motion.div>
                ))}
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
