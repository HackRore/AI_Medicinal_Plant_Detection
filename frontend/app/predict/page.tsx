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
  alternatives?: Array<{ class_name: string; confidence: number }>
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

  // Predict mutation with timeout and error handling
  const predictMutation = useMutation({
    mutationFn: async (file: File): Promise<Prediction> => {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60s timeout

      try {
        const formData = new FormData()
        formData.append("file", file)
        
        const res = await fetch(`${API_BASE}/api/v1/predict`, {
          method: "POST",
          body: formData,
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        if (!res.ok) {
          if (res.status === 0) throw new Error("Server unavailable. Please check if backend is running.")
          const err = await res.json().catch(() => ({}))
          throw new Error(err.detail || "Prediction failed")
        }
        return res.json()
      } catch (err: any) {
        clearTimeout(timeoutId)
        if (err.name === "AbortError") throw new Error("Request timeout (60s). Please try a smaller image or check connection.")
        if (!navigator.onLine) throw new Error("No internet connection. Please check your network.")
        throw err
      }
    },
    onSuccess: async (data: Prediction) => {
      // Confetti for high confidence
      if (data.confidence > 0.85) {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } })
        toast.success(`Detected: ${data.predicted_class.replace(/_/g, ' ')}`)
      }

      // Save to localStorage (last 10)
      const newEntry: LocalHistoryItem = {
        id: Date.now().toString(),
        prediction: data,
        thumb: uploadedImages[0]?.preview || preview || '',
        timestamp: Date.now()
      }
      const newHistory = [newEntry, ...localHistory].slice(0, 10)
      setLocalHistory(newHistory)
      localStorage.setItem('plantoai_history', JSON.stringify(newHistory))

      // Fetch medicinal details if available
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

      // Reset UI (Handled by manual reset now)
      // setUploadedImages([])
      // setPreview(null)
    },
    onError: (error: any) => {
      console.error('Prediction error:', error)
      toast.error(error.message || 'Prediction failed')
    },
    retry: 1,
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).slice(0, 3) // Max 3 images
    if (files.length === 0) return

    // Validate images
    const validImages = files.filter(file => {
      const isValidType = file.type.startsWith('image/')
      const isValidSize = file.size < 10 * 1024 * 1024 // 10MB
      if (!isValidType) toast.error(`Invalid file type: ${file.name}`)
      if (!isValidSize) toast.error(`File too large: ${file.name}`)
      return isValidType && isValidSize
    })

    if (validImages.length === 0) return

    const imagePreviews = validImages.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }))
    setUploadedImages(imagePreviews)
    
    // Predict first image
    predictMutation.mutate(imagePreviews[0].file)
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
            setPreview(URL.createObjectURL(blob))
            predictMutation.mutate(file)
          }
        }, 'image/jpeg', 0.9)
      }
    }
  }, [predictMutation])

  // Camera setup
  useEffect(() => {
    let stream: MediaStream | null = null
    if (isCameraOpen && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: { ideal: "environment" } } 
      }).then((s) => {
        stream = s
        videoRef.current!.srcObject = s
      }).catch((err) => {
        toast.error('Camera access denied')
        setIsCameraOpen(false)
      })
    }
    return () => {
      if (stream) stream.getTracks().forEach(track => track.stop())
    }
  }, [isCameraOpen])
  return (
    <main className="container mx-auto p-6 min-h-screen space-y-8 max-w-6xl">
      {/* Header */}
      <header className="text-center py-12">
        <h1 className="text-6xl font-black bg-gradient-to-r from-emerald-600 to-green-500 bg-clip-text text-transparent mb-6 drop-shadow-lg">
          PlantoAI
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          AI-powered medicinal plant detection & Ayurvedic Physician
        </p>
        
        {/* MODULE SWITCHER */}
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
            {/* Input Panel */}
            <div className="space-y-6">
              {!predictMutation.isSuccess && (
                <div className="grid md:grid-cols-2 gap-6">
                  <label className="group cursor-pointer block p-8 border-2 border-dashed border-muted rounded-3xl hover:border-primary transition-all text-center">
                    <input type="file" accept="image/*" multiple onChange={handleFileSelect} className="sr-only" disabled={predictMutation.isPending} />
                    <Upload className="mx-auto h-12 w-12 text-muted-foreground group-hover:text-primary mb-4" />
                    <p className="font-bold text-lg">Upload Images</p>
                  </label>
                  <Button onClick={() => setIsCameraOpen(true)} size="lg" variant="outline" className="h-full p-8 gap-3" disabled={predictMutation.isPending}>
                    <Camera className="h-12 w-12" />
                    <p className="font-bold text-lg text-left">Live Camera</p>
                  </Button>
                </div>
              )}

              {!predictMutation.isSuccess && !predictMutation.isPending && localHistory.length > 0 && (
                <div className="pt-8">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <History className="h-5 w-5" />
                    Recent Scans
                  </h3>
                  <div className="grid grid-cols-5 gap-4">
                    {localHistory.map(item => (
                      <button 
                        key={item.id}
                        onClick={() => {
                          // In a real app we'd load this history item
                          toast.info("Loading history item...")
                        }}
                        className="aspect-square rounded-xl overflow-hidden border hover:border-emerald-500 transition-all"
                      >
                        <img src={item.thumb} alt="Scan" className="w-full h-full object-cover" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Reset Button (Only when success) */}
              {predictMutation.isSuccess && (
                <Button 
                  variant="outline" 
                  className="w-full h-16 rounded-2xl border-emerald-200 text-emerald-800 font-bold"
                  onClick={() => {
                    predictMutation.reset()
                    setPreview(null)
                  }}
                >
                  Start New Scan
                </Button>
              )}
            </div>

            {/* Results Panel */}
            <div className="space-y-6">
              <AIThinkingOverlay isVisible={predictMutation.isPending} />

              {predictMutation.isSuccess && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-6"
                >
                  {/* Toxicity Warning if applicable */}
                  {TOXIC_PLANTS.some(toxic => 
                    predictMutation.data.predicted_class.toLowerCase().includes(toxic)
                  ) && (
                    <Card className="border-destructive bg-destructive/5">
                      <CardContent className="p-6">
                        <div className="flex items-start gap-4">
                          <AlertCircle className="h-10 w-10 text-destructive mt-1 flex-shrink-0" />
                          <div>
                            <h3 className="font-bold text-xl text-destructive mb-2">⚠️ TOXIC PLANT</h3>
                            <p className="text-destructive-foreground">Potentially poisonous. Handle with extreme care.</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Main Result Card */}
                  <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-50 shadow-2xl overflow-hidden">
                    <CardHeader className="relative">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-full uppercase tracking-tighter">
                              AI Identification
                            </span>
                          </div>
                          <CardTitle className="text-4xl font-black text-emerald-950">
                            {predictMutation.data.predicted_class.replace(/_/g, " ")}
                          </CardTitle>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mb-1">Confidence</p>
                          <div className="text-2xl font-black text-emerald-600">{(predictMutation.data.confidence * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <Progress value={predictMutation.data.confidence * 100} className="h-4 bg-gray-100/50" />
                      
                      {predictMutation.data.gradcam_base64 && (
                        <motion.div
                          initial={{ opacity: 0, y: 16 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mt-4 rounded-2xl border border-green-500/20 overflow-hidden bg-black/30 p-4"
                        >
                          <p className="text-xs font-mono text-green-400 uppercase tracking-widest mb-3">
                            Explainable AI — Grad-CAM Attention Map
                          </p>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <p className="text-xs text-gray-400 mb-1">Your Photo</p>
                              <img src={preview || (uploadedImages.length > 0 ? uploadedImages[0].preview : '')} className="w-full rounded-xl object-cover aspect-square border border-white/10" />
                            </div>
                            <div>
                              <p className="text-xs text-gray-400 mb-1">AI Attention</p>
                              <img
                                src={`data:image/jpeg;base64,${predictMutation.data.gradcam_base64}`}
                                className="w-full rounded-xl object-cover aspect-square border border-emerald-500/30"
                              />
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-3 text-center italic">
                            Warm areas (red/yellow) show features the AI used to identify this plant
                          </p>
                        </motion.div>
                      )}

                      {predictMutation.data.top_predictions && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.3 }}
                          className="mt-4 p-4 rounded-2xl border border-white/10 bg-black/30"
                        >
                          <p className="text-xs font-mono text-gray-400 uppercase tracking-widest mb-4">
                            AI Confidence Analysis
                          </p>
                          {predictMutation.data.top_predictions.map((p: any, i: number) => (
                            <div key={i} className="mb-3 last:mb-0">
                              <div className="flex justify-between items-center mb-1">
                                <span className={`text-sm ${i === 0 ? 'text-green-400 font-medium' : 'text-gray-400'}`}>
                                  {p.plant}
                                </span>
                                <span className={`text-sm font-mono ${i === 0 ? 'text-green-400' : 'text-gray-500'}`}>
                                  {p.confidence}%
                                </span>
                              </div>
                              <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${p.confidence}%` }}
                                  transition={{ duration: 0.8, delay: i * 0.15, ease: "easeOut" }}
                                  className={`h-full rounded-full ${
                                    i === 0 ? 'bg-green-400' :
                                    i === 1 ? 'bg-yellow-500' : 'bg-gray-600'
                                  }`}
                                />
                              </div>
                            </div>
                          ))}
                        </motion.div>
                      )}

                      <SafetyBadge isToxic={predictMutation.data.is_toxic} caution={predictMutation.data.caution} />

                      <div className="grid grid-cols-2 gap-4">
                        <Button className="w-full gap-2" onClick={() => {
                          navigator.clipboard.writeText(predictMutation.data.predicted_class)
                          toast.success("Name copied")
                        }}>
                          <Copy className="h-4 w-4" /> Copy
                        </Button>
                        {predictMutation.data.plant_details && (
                          <Link href={`/plants/${predictMutation.data.plant_details.id}`} className="w-full">
                            <Button variant="outline" className="w-full border-emerald-200 text-emerald-800">
                              <Leaf className="h-4 w-4" /> Profile
                            </Button>
                          </Link>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Feedback */}
                  <Card className="border-orange-100 bg-orange-50/30">
                    <CardContent className="p-4 flex items-center justify-between">
                      <span className="text-sm font-medium text-orange-800">Accurate?</span>
                      <div className="flex gap-2">
                        <Button size="sm" variant="ghost" className="text-emerald-700 hover:bg-emerald-100" onClick={() => toast.success("Verified!")}>
                          <ThumbsUp className="h-4 w-4 mr-2" /> Yes
                        </Button>
                        <Button size="sm" variant="ghost" className="text-red-700 hover:bg-red-100" onClick={() => toast.error("Reported")}>
                          <ThumbsDown className="h-4 w-4 mr-2" /> No
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="symptoms-module"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto space-y-12"
          >
            <Card className="p-8 space-y-6 shadow-2xl border-emerald-100">
              <div className="space-y-2">
                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground">Patient Symptoms</label>
                <textarea 
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Describe your symptoms e.g. fever, headache, joint pain..."
                  className="w-full h-40 rounded-2xl bg-muted/30 border border-muted p-6 text-[var(--text)] focus:outline-none focus:border-emerald-500 transition-all text-lg"
                />
              </div>
              <Button 
                onClick={() => symptomMutation.mutate(symptoms)}
                disabled={symptomMutation.isPending || symptoms.length < 3}
                className="w-full h-20 rounded-2xl bg-emerald-600 text-white font-black uppercase tracking-widest text-lg shadow-xl hover:translate-y-[-2px] transition-all"
              >
                {symptomMutation.isPending ? "Consulting Ayurvedic AI..." : "Get Physician Consultation"}
              </Button>
            </Card>

            {symptomMutation.isPending && (
                <div className="flex flex-col items-center gap-4 py-12">
                    <div className="w-12 h-12 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin" />
                    <p className="font-serif italic text-muted-foreground text-xl">Analyzing classical texts...</p>
                </div>
            )}

            {symptomResults && !symptomResults.error && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid md:grid-cols-3 gap-6">
                {symptomResults.recommendations?.map((rec: any, i: number) => (
                  <Card key={i} className="p-6 border-emerald-100 hover:shadow-xl transition-all h-full flex flex-col">
                    <div className="space-y-1 mb-6">
                      <h4 className="text-2xl font-serif font-bold text-emerald-800">{rec.plant}</h4>
                      <p className="text-[10px] italic text-muted-foreground">{rec.scientific_name}</p>
                    </div>
                    <div className="space-y-4 flex-1">
                      <div>
                        <p className="text-[10px] font-black uppercase text-muted-foreground tracking-widest mb-1">Why</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{rec.why}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-black uppercase text-muted-foreground tracking-widest mb-1">Preparation</p>
                        <p className="text-sm text-emerald-800 font-medium">{rec.preparation}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-emerald-50">
                        <div>
                          <p className="text-[9px] font-black uppercase text-muted-foreground tracking-widest">Dosha</p>
                          <p className="text-xs font-bold text-orange-700">{rec.dosha_effect}</p>
                        </div>
                        <div>
                          <p className="text-[9px] font-black uppercase text-muted-foreground tracking-widest">Reference</p>
                          <p className="text-[9px] text-muted-foreground italic truncate" title={rec.classical_reference}>{rec.classical_reference}</p>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </motion.div>
            )}

            {symptomResults && !symptomResults.error && (
                <Card className="p-8 border-yellow-100 bg-yellow-50/50">
                    <h5 className="font-serif italic text-2xl text-emerald-900 mb-4">Physician's Closing Advice</h5>
                    <p className="text-lg text-emerald-800 leading-relaxed mb-8">{symptomResults.lifestyle_advice}</p>
                    <div className="p-4 rounded-xl bg-orange-100 text-orange-900 flex items-start gap-3">
                        <ShieldAlert className="h-6 w-6 shrink-0" />
                        <p className="text-sm font-medium">{symptomResults.warning}</p>
                    </div>
                </Card>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Camera UI */}
      {isCameraOpen && (
        <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4" role="dialog">
          <div className="bg-background rounded-3xl max-w-md w-full max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold flex items-center gap-2">
                <Camera className="h-7 w-7" />
                Live Plant Scanner
              </h3>
            </div>
            <div className="p-4">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full rounded-2xl aspect-video object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />
            </div>
            <div className="p-6 border-t bg-muted/50">
              <div className="flex gap-3">
                <Button 
                  className="flex-1" 
                  size="lg"
                  onClick={handleCapture}
                  disabled={predictMutation.isPending}
                >
                  <Zap className="h-5 w-5 mr-2" />
                  Analyze Plant
                </Button>
                <Button 
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsCameraOpen(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
