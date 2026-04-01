'use client'

import { useState, useRef, useCallback, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import confetti from "canvas-confetti"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { Progress } from "@/components/ui/progress"
import { Camera, Upload, History, Sun, Moon, Zap, AlertCircle, ThumbsUp, ThumbsDown, Copy, Leaf, ShieldAlert } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"

interface Prediction {
  predicted_class: string
  predicted_class_index: number
  confidence: number
  top_predictions: Array<{ class_name: string; confidence: number }>
  model_version: string
  processing_time_ms?: number
  demo_mode?: boolean
  plant_details?: {
    id: number
    species_name: string
    common_name: string
    description: string
  }
  gradcam_base64?: string
  is_toxic: boolean
  caution: string
  medicinal_info?: {
    uses: string
    prep: string
    caution: string
  }
  ai_debate?: {
    cnn_prediction: string
    cnn_confidence: number
    gemini_prediction: string
    agreement: boolean
    explanation: string
  }
}

interface LocalHistoryItem {
  id: string
  prediction: Prediction
  thumb: string
  timestamp: number
}

const DataBadge = ({ label, icon: Icon, active }: { label: string, icon: any, active: boolean }) => (
  <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border transition-all ${
    active 
      ? 'bg-emerald-50 border-emerald-200 text-emerald-700 opacity-100 shadow-sm' 
      : 'bg-gray-50 border-gray-100 text-gray-400 opacity-40'
  }`}>
    <Icon className={`h-3.5 w-3.5 ${active ? 'animate-pulse' : ''}`} />
    <span className="text-[10px] font-bold uppercase tracking-tight">{label}</span>
  </div>
)

const SafetyBadge = ({isToxic, caution}: {isToxic: boolean, caution: string}) => (
  <div style={{
    padding: '12px 16px',
    borderRadius: '10px',
    background: isToxic ? '#FCEBEB' : caution ? '#FAEEDA' : '#EAF3DE',
    borderLeft: `4px solid ${isToxic ? '#E24B4A' : caution ? '#EF9F27' : '#639922'}`,
    marginTop: '12px'
  }}>
    <strong style={{color: isToxic ? '#A32D2D' : caution ? '#854F0B' : '#3B6D11'}}>
      {isToxic ? 'TOXIC — Do not consume' : caution ? 'Use with caution' : 'Safe medicinal plant'}
    </strong>
    {caution && <p style={{margin:'4px 0 0', fontSize:'13px'}}>{caution}</p>}
  </div>
)

const THINKING_STEPS = [
  { icon: "🔬", text: "Detecting leaf edges and boundaries..." },
  { icon: "🌿", text: "Analyzing venation patterns and texture..." },
  { icon: "🧬", text: "Comparing against 81 medicinal species..." },
  { icon: "🤖", text: "Cross-verifying with Gemini Vision AI..." },
  { icon: "📚", text: "Generating Ayurvedic knowledge profile..." },
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
      className="w-full max-w-md mx-auto mt-8 p-6 rounded-2xl border border-green-500/20 bg-black/40 backdrop-blur"
    >
      <div className="flex items-center gap-2 mb-5">
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="w-2 h-2 rounded-full bg-green-400"
        />
        <span className="text-green-400 text-xs font-mono font-medium tracking-widest uppercase">
          AI Processing
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
            <span className={`text-sm font-mono flex-1 ${
              i === currentStep ? 'text-green-300' :
              completedSteps.includes(i) ? 'text-gray-400 line-through' :
              'text-gray-600'
            }`}>
              {step.text}
            </span>
            {completedSteps.includes(i) && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-green-400 text-xs"
              >✓</motion.span>
            )}
            {i === currentStep && (
              <motion.div
                animate={{ opacity: [1, 0] }}
                transition={{ repeat: Infinity, duration: 0.8 }}
                className="w-1 h-3 bg-green-400"
              />
            )}
          </motion.div>
        ))}
      </div>
      <div className="mt-5 h-1 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-green-400 rounded-full"
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
  const [localHistory, setLocalHistory] = useState<LocalHistoryItem[]>([])
  const [isLoadingMedicinal, setIsLoadingMedicinal] = useState(false)
  const [selectedPlantDetails, setSelectedPlantDetails] = useState<any>(null)
  const [activeTab, setActiveTab] = useState('identity')
  const [activeModule, setActiveModule] = useState<'scanner' | 'symptoms'>('scanner')
  const [symptoms, setSymptoms] = useState("")
  const [symptomResults, setSymptomResults] = useState<any>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const queryClient = useQueryClient()

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
      else toast.success("Remedies found!")
    }
  })

  const TOXIC_PLANTS = [
    "datura", "oleander", "belladonna", "aconite", "hemlock"
  ]

  // Load local history on mount
  useEffect(() => {
    const saved = localStorage.getItem("plantoai_history")
    if (saved) {
      try {
        setLocalHistory(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to load history", e)
      }
    }
  }, [])

  // Predict mutation
  const predictMutation = useMutation({
    mutationFn: async (file: File): Promise<Prediction> => {
      const formData = new FormData()
      formData.append("file", file)
      
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
    onSuccess: async (data: Prediction) => {
      const plantClass = data.predicted_class || "Unknown";
      if (data.confidence > 0.85) {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } })
        toast.success(`Detected: ${plantClass.replace(/_/g, ' ')}`)
      }

      const newEntry: LocalHistoryItem = {
        id: Date.now().toString(),
        prediction: data,
        thumb: uploadedImages[0]?.preview || preview || '',
        timestamp: Date.now()
      }
      const newHistory = [newEntry, ...localHistory].slice(0, 10)
      setLocalHistory(newHistory)
      localStorage.setItem('plantoai_history', JSON.stringify(newHistory))

      if (data.plant_details?.id) {
        setIsLoadingMedicinal(true)
        try {
          const res = await fetch(`${API_BASE}/api/v1/plants/${data.plant_details.id}`)
          if (res.ok) {
            setSelectedPlantDetails(await res.json())
          }
        } catch (e) {
          toast.warning('Medicinal info temporarily unavailable')
        } finally {
          setIsLoadingMedicinal(false)
        }
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'Prediction failed')
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
          videoRef.current!.srcObject = s
        })
        .catch(() => {
          toast.error("Camera access denied")
          setIsCameraOpen(false)
        })
    }
    return () => stream?.getTracks().forEach(t => t.stop())
  }, [isCameraOpen])

  return (
    <main className="container mx-auto p-6 min-h-screen space-y-8 max-w-6xl">
      <header className="text-center py-12">
        <h1 className="text-6xl font-black bg-gradient-to-r from-emerald-600 to-green-500 bg-clip-text text-transparent mb-6 drop-shadow-lg">
          PlantoAI
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          AI-powered medicinal plant detection & Ayurvedic Physician
        </p>
        
        <div className="flex justify-center gap-4 mt-12">
          <Button 
            onClick={() => setActiveModule('scanner')}
            variant={activeModule === 'scanner' ? 'default' : 'outline'}
            className="rounded-2xl px-8 h-12 font-bold uppercase tracking-widest"
          >
            Neural Scanner
          </Button>
          <Button 
            onClick={() => setActiveModule('symptoms')}
            variant={activeModule === 'symptoms' ? 'default' : 'outline'}
            className="rounded-2xl px-8 h-12 font-bold uppercase tracking-widest"
          >
            Symptom Search
          </Button>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {activeModule === 'scanner' ? (
          <motion.div 
            key="scanner-module"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid lg:grid-cols-2 gap-12 items-start"
          >
            <div className="space-y-6">
              {!predictMutation.isSuccess && (
                <div className="grid md:grid-cols-2 gap-6">
                  <label className="group cursor-pointer block p-8 border-2 border-dashed border-muted rounded-3xl hover:border-primary transition-all text-center">
                    <input type="file" accept="image/*" onChange={handleFileSelect} className="sr-only" disabled={predictMutation.isPending} />
                    <Upload className="mx-auto h-12 w-12 text-muted-foreground group-hover:text-primary mb-4" />
                    <p className="font-bold text-lg">Upload Images</p>
                  </label>
                  <Button onClick={() => setIsCameraOpen(true)} size="lg" variant="outline" className="h-full p-8 gap-3" disabled={predictMutation.isPending}>
                    <Camera className="h-12 w-12" />
                    <p className="font-bold text-lg text-left">Live Camera</p>
                  </Button>
                </div>
              )}

              {predictMutation.isSuccess && (
                <Button 
                  variant="outline" 
                  className="w-full h-16 rounded-2xl border-emerald-200 text-emerald-800 font-bold"
                  onClick={() => {
                    predictMutation.reset()
                    setPreview(null)
                    setUploadedImages([])
                  }}
                >
                  Start New Scan
                </Button>
              )}

              {!predictMutation.isSuccess && !predictMutation.isPending && localHistory.length > 0 && (
                <div className="pt-8 text-white">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <History className="h-5 w-5" />
                    Recent Scans
                  </h3>
                  <div className="grid grid-cols-5 gap-4">
                    {localHistory.map(item => (
                      <button key={item.id} className="aspect-square rounded-xl overflow-hidden border hover:border-emerald-500 transition-all">
                        <img src={item.thumb} alt="Scan" className="w-full h-full object-cover" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <AIThinkingOverlay isVisible={predictMutation.isPending} />

              {predictMutation.isSuccess && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
                  <div className="grid lg:grid-cols-2 gap-8 items-stretch">
                    <div className="relative rounded-3xl overflow-hidden bg-black aspect-square shadow-2xl border border-white/5">
                      <img src={preview || ''} className="w-full h-full object-cover" alt="Uploaded plant" />
                    </div>
                    <div className="relative rounded-3xl overflow-hidden bg-black aspect-square shadow-2xl border border-white/5">
                      {predictMutation.data.gradcam_base64 && (
                        <img src={`data:image/jpeg;base64,${predictMutation.data.gradcam_base64}`} className="w-full h-full object-cover" alt="Neural focus" />
                      )}
                    </div>
                  </div>

                  <Card className="border-none bg-white/5 backdrop-blur-xl rounded-[2.5rem]">
                    <CardContent className="p-8 space-y-8">
                      <div className="grid md:grid-cols-2 gap-12 text-white">
                        <div className="space-y-6">
                          <header className="flex justify-between items-end">
                            <div>
                              <p className="text-[10px] uppercase text-gray-500 font-bold tracking-widest leading-none mb-1">Primary Match</p>
                              <h3 className="text-2xl font-black text-white">{(predictMutation.data.predicted_class || "Detection").replace(/_/g, " ")}</h3>
                            </div>
                            <span className="text-2xl font-black text-emerald-400">
                              {predictMutation.data.confidence > 1 ? (predictMutation.data.confidence).toFixed(1) : (predictMutation.data.confidence * 100).toFixed(1)}%
                            </span>
                          </header>
                          <div className="h-4 bg-white/5 rounded-full overflow-hidden border border-white/5">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${predictMutation.data.confidence * 100}%` }}
                              className="h-full bg-gradient-to-r from-emerald-600 to-green-400"
                            />
                          </div>
                        </div>
                        <div className="space-y-6">
                           <p className="text-[10px] uppercase text-gray-500 font-bold tracking-widest">Neural Variance</p>
                           <div className="space-y-4">
                             {predictMutation.data.top_predictions?.slice(0, 3).map((p: any, i: number) => (
                               <div key={i} className="flex justify-between text-xs font-bold px-1">
                                 <span>{p.class_name.replace(/_/g, " ")}</span>
                                 <span className="text-gray-500 font-mono">{(p.confidence * 100).toFixed(1)}%</span>
                               </div>
                             ))}
                           </div>
                        </div>
                      </div>

                      <SafetyBadge isToxic={predictMutation.data.is_toxic} caution={predictMutation.data.caution} />

                      {predictMutation.data.ai_debate && (
                        <div className="space-y-4 pt-8 border-t border-white/5 text-white">
                          <div className="flex justify-between items-center mb-6">
                            <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Triple Intelligence Ensemble</p>
                            <div className="flex gap-1">
                              {['Native', 'Benchmark', 'Global'].map((s, i) => (
                                <span key={i} className="text-[8px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold uppercase">{s}</span>
                              ))}
                            </div>
                          </div>
                          <div className="space-y-4">
                            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="flex gap-3">
                              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">🧠</div>
                              <div className="bg-white/5 p-4 rounded-2xl rounded-tl-none border border-white/5 text-sm">
                                <span className="block text-emerald-400 font-bold uppercase text-[10px] mb-1">CNN Auditor (Indian Medicinal)</span>
                                I identify this as {(predictMutation.data.predicted_class || "Unknown").replace(/_/g, ' ')} with {(predictMutation.data.confidence * 100).toFixed(1)}% confidence.
                              </div>
                            </motion.div>
                            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1 }} className="flex gap-3 flex-row-reverse">
                              <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30">👁️</div>
                              <div className="bg-white/5 p-4 rounded-2xl rounded-tr-none border border-white/5 text-sm text-right">
                                <span className="block text-blue-400 font-bold uppercase text-[10px] mb-1">Vision AI Expert (PlantVillage / Global)</span>
                                Multi-dataset verification shows {(predictMutation.data.ai_debate?.gemini_prediction || "uncertain results").replace(/_/g, ' ')}.
                              </div>
                            </motion.div>
                            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.5 }} className={`p-4 rounded-2xl border text-sm ${predictMutation.data.ai_debate.agreement ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-amber-500/10 border-amber-500/20'}`}>
                              <p className="font-bold flex items-center gap-2 mb-1 uppercase text-xs">
                                {predictMutation.data.ai_debate.agreement ? <ThumbsUp className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                                Verdict: {predictMutation.data.ai_debate.agreement ? 'Triple Consensus Matched' : 'Inconclusive Conflict'}
                              </p>
                              <p className="italic opacity-80">"{predictMutation.data.ai_debate.explanation}"</p>
                            </motion.div>
                          </div>
                        </div>
                      )}

                      <div className="pt-6 flex gap-4">
                        <Button className="flex-1 h-14 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold" onClick={() => toast.success("Copied!")}>
                          <Copy className="h-5 w-5 mr-2" /> Share Result
                        </Button>
                        {predictMutation.data.plant_details && (
                          <Link href={`/plants/${predictMutation.data.plant_details.id}`} className="flex-1">
                            <Button variant="outline" className="w-full h-14 rounded-xl border-white/10 hover:bg-white/5 text-white font-bold">
                              <Leaf className="h-5 w-5 mr-2" /> Details
                            </Button>
                          </Link>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div key="symptoms-module" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-8">
            <Card className="p-8 bg-zinc-900 border-zinc-800 text-white rounded-[2rem]">
              <div className="space-y-4">
                <label className="text-xs font-black uppercase tracking-widest text-gray-400">Describe Symptoms</label>
                <textarea 
                  value={symptoms} 
                  onChange={e => setSymptoms(e.target.value)}
                  className="w-full h-40 rounded-2xl bg-white/5 border border-white/10 p-6 focus:border-emerald-500 outline-none text-lg"
                  placeholder="e.g. chronic cough, indigestion..."
                />
                <Button 
                  onClick={() => symptomMutation.mutate(symptoms)} 
                  disabled={symptomMutation.isPending || symptoms.length < 3}
                  className="w-full h-16 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold uppercase"
                >
                  {symptomMutation.isPending ? "Consulting texts..." : "Get Consultation"}
                </Button>
              </div>
            </Card>

            {symptomResults && (
              <div className="grid md:grid-cols-3 gap-6">
                {symptomResults.recommendations?.map((rec: any, i: number) => (
                  <Card key={i} className="p-6 bg-zinc-900 border-zinc-800 text-white rounded-3xl">
                    <h4 className="text-xl font-bold text-emerald-400 mb-2">{rec.plant}</h4>
                    <p className="text-sm opacity-80 mb-4">{rec.why}</p>
                    <div className="pt-4 border-t border-white/5 text-[10px] font-bold uppercase text-emerald-500 tracking-widest">
                      Prep: {rec.preparation}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {isCameraOpen && (
        <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-white/10 rounded-[3rem] max-w-lg w-full overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-xl font-bold text-white flex gap-2 items-center"><Camera className="h-5 w-5" /> Live Scanner</h3>
            </div>
            <div className="p-4">
              <video ref={videoRef} autoPlay playsInline className="w-full rounded-2xl aspect-[4/3] object-cover" />
              <canvas ref={canvasRef} className="hidden" />
            </div>
            <div className="p-6 flex gap-4">
              <Button className="flex-1 h-16 rounded-2xl bg-emerald-600 font-bold text-white" onClick={handleCapture}>Capture</Button>
              <Button variant="outline" className="flex-1 h-16 rounded-2xl border-white/10 text-white" onClick={() => setIsCameraOpen(false)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
