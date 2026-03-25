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

      // Reset UI
      setUploadedImages([])
      setPreview(null)
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
<<<<<<< HEAD
              {/* Confidence Progress */}
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-2">
                    <Progress value={predictMutation.data.confidence * 100} className="h-3" />
                    <p className="text-sm text-center font-mono">
                      {(predictMutation.data.confidence * 100).toFixed(1)}% confidence
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Demo Mode Banner */}
              {predictMutation.data.demo_mode && (
                <Card className="border-yellow-200 bg-yellow-50">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <AlertCircle className="h-6 w-6 text-yellow-600" />
                      <div>
                        <h4 className="font-bold text-lg text-yellow-800">Demo Mode Active</h4>
                        <p className="text-sm text-yellow-700">Full AI model training in progress. Production ready.</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Toxicity Warning */}
              {TOXIC_PLANTS.some(toxic => 
                predictMutation.data.predicted_class.toLowerCase().includes(toxic)
              ) && (
                <Card className="border-destructive bg-destructive/5">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <AlertCircle className="h-10 w-10 text-destructive mt-1 flex-shrink-0" />
                      <div>
                        <h3 className="font-bold text-xl text-destructive mb-2">⚠️ TOXIC PLANT DETECTED</h3>
                        <p className="text-destructive-foreground">
                          This plant is potentially poisonous. Do not ingest without expert medical supervision.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Main Prediction Result */}
              <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-50 shadow-2xl overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 -rotate-45 translate-x-16 -translate-y-16" />
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
                      <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mb-1">Model Version</p>
                      <div className="font-mono text-xs bg-emerald-100/50 text-emerald-800 px-3 py-1 rounded-full border border-emerald-200">
                        {predictMutation.data.model_version}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="relative space-y-8">
                  {/* Confidence Highlight */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-6 border border-white shadow-inner">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-emerald-800">Neural Confidence</span>
                        <div className="flex items-center gap-2 mt-1">
                            <span className={`h-2 w-2 rounded-full ${
                                predictMutation.data.confidence > 0.9 ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 
                                predictMutation.data.confidence > 0.7 ? 'bg-amber-500' : 'bg-red-500'
                            }`} />
                            <span className="text-[10px] font-bold text-gray-500 uppercase">
                                {predictMutation.data.confidence > 0.9 ? 'Optimal precision' : 
                                 predictMutation.data.confidence > 0.7 ? 'Moderate certainty' : 'Low certainty'}
                            </span>
                        </div>
                      </div>
                      <span className={`text-3xl font-black ${
                        predictMutation.data.confidence > 0.9 ? 'text-emerald-600' : 
                        predictMutation.data.confidence > 0.7 ? 'text-amber-600' : 'text-red-600'
                      }`}>
                        {(predictMutation.data.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                        value={predictMutation.data.confidence * 100} 
                        className={`h-4 bg-gray-100/50 [&>div]:transition-all [&>div]:duration-1000 ${
                            predictMutation.data.confidence > 0.9 ? '[&>div]:bg-emerald-500' : 
                            predictMutation.data.confidence > 0.7 ? '[&>div]:bg-amber-500' : '[&>div]:bg-red-500'
                        }`} 
                    />
                    
                    {/* Analysis Authenticity Badges */}
                    <div className="mt-6 pt-6 border-t border-white/40 flex flex-wrap gap-2">
                        <DataBadge 
                            label="Species Verified" 
                            icon={Leaf} 
                            active={!!predictMutation.data.predicted_class} 
                        />
                        <DataBadge 
                            label="Neural Mapped" 
                            icon={Zap} 
                            active={!!predictMutation.data.gradcam_base64} 
                        />
                        <DataBadge 
                            label="Safety Scanned" 
                            icon={AlertCircle} 
                            active={true} 
                        />
                        {predictMutation.data.processing_time_ms && (
                            <div className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/5 text-[10px] font-mono text-gray-500">
                                <span className="font-bold">LATENCY:</span>
                                {predictMutation.data.processing_time_ms.toFixed(0)}ms
                            </div>
                        )}
                    </div>
                  </div>

                  {/* Grad-CAM Neural Insight */}
                  {predictMutation.data.gradcam_base64 && (
                    <div className="space-y-4">
                        <div className="flex items-center gap-2">
                            <Zap className="h-4 w-4 text-emerald-500 fill-emerald-500" />
                            <h3 className="font-bold text-emerald-900">Neural Attention Map</h3>
                        </div>
                        <div className="relative group rounded-2xl overflow-hidden border-2 border-emerald-200/50 bg-black/5 p-1">
                            <img
                            src={`data:image/jpeg;base64,${predictMutation.data.gradcam_base64}`}
                            alt="Grad-CAM Heatmap"
                            className="w-full h-auto rounded-xl shadow-2xl transition-transform duration-700 group-hover:scale-105"
                            />
                            <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-md text-white px-4 py-2 rounded-xl text-[10px] font-medium leading-tight opacity-0 group-hover:opacity-100 transition-opacity">
                                The heat gradient highlights regions (red) that the AI focused on to authenticate this species.
                            </div>
                        </div>
                    </div>
                  )}

                  <div className="grid md:grid-cols-2 gap-4">
                    <Card className="bg-white/40 border-none shadow-none">
                      <CardContent className="p-4">
                        <h4 className="font-bold text-emerald-800 mb-3 text-[10px] uppercase tracking-widest">Top Alternatives</h4>
                        <ul className="space-y-2">
                          {predictMutation.data.top_predictions.slice(1, 4).map((pred, i) => (
                            <li key={i} className="flex justify-between items-center text-xs">
                              <span className="text-gray-600 font-medium">{pred.class_name.replace(/_/g, " ")}</span>
                              <span className="font-mono font-black text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                                {(pred.confidence * 100).toFixed(0)}%
                              </span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    <div className="flex flex-col gap-3">
                        <Button className="w-full gap-2 shadow-emerald-200 shadow-xl" onClick={() => {
                        navigator.clipboard.writeText(predictMutation.data.predicted_class)
                        toast.success("Plant name copied!")
                        }}>
                        <Copy className="h-4 w-4" />
                        Copy Identification
                        </Button>
                        {predictMutation.data.plant_details && (
                        <Link href={`/plants/${predictMutation.data.plant_details.id}`}>
                            <Button variant="outline" className="w-full gap-2 border-emerald-200 text-emerald-800 hover:bg-emerald-50">
                                <Leaf className="h-4 w-4" />
                                Medicinal Profile
                            </Button>
                        </Link>
                        )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <SafetyBadge isToxic={predictMutation.data.is_toxic} caution={predictMutation.data.caution} />

              {predictMutation.data.medicinal_info && (
                <div style={{
                  background:'#f1f8e9', border:'1px solid #aed581',
                  borderRadius:'10px', padding:'16px', marginTop:'12px'
                }}>
                  <h3 style={{margin:'0 0 12px', color:'#2e7d32'}} className="font-bold text-lg">
                    Ayurvedic Information
                  </h3>
                  <p className="text-sm mb-2"><strong>Uses:</strong> {predictMutation.data.medicinal_info.uses}</p>
                  <p className="text-sm mb-2"><strong>Preparation:</strong> {predictMutation.data.medicinal_info.prep}</p>
                  <p className="text-sm"><strong>Caution:</strong> {predictMutation.data.medicinal_info.caution}</p>
                </div>
              )}

              {(predictMutation.data.alternatives?.length ?? 0) > 0 && (
                <div style={{marginTop:'12px'}}>
                  <p style={{fontSize:'13px', color:'#666', marginBottom:'8px'}}>
                    AI also considered:
                  </p>
                  {predictMutation.data.alternatives?.slice(1,4).map((alt: any, i: number) => (
                    <div key={i} style={{
                      display:'flex', justifyContent:'space-between',
                      padding:'6px 10px', background:'#f5f5f5',
                      borderRadius:'6px', marginBottom:'4px', fontSize:'13px'
                    }}>
                      <span>{alt.class_name.replace(/_/g, " ")}</span>
                      <span style={{color:'#888'}}>{(alt.confidence * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Medicinal Information */}
              {isLoadingMedicinal ? (
                <Card>
                  <CardContent className="p-8">
                    <div className="space-y-4">
                      <Skeleton className="h-6 w-1/2" />
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : selectedPlantDetails && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Leaf className="h-6 w-6 text-emerald-600" />
                      Medicinal Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose prose-sm max-w-none [&>div]:mb-4 [&>h5]:font-semibold [&>h5]:text-lg [&>h5]:mb-2 [&>h5]:border-b [&>h5]:pb-2">
                      <p className="text-muted-foreground mb-6 leading-relaxed">
                        {selectedPlantDetails.description?.substring(0, 250)}...
                      </p>
                      {selectedPlantDetails.medicinal_properties?.slice(0, 3).map((prop: any, i: number) => (
                        <div key={i} className="bg-muted/50 p-4 rounded-xl border-l-4 border-emerald-400">
                          <h5>{prop.ailment}</h5>
                          <p className="text-sm text-muted-foreground mt-2">{prop.usage_description}</p>
                        </div>
                      ))}
                    </div>
                    <Link href={`/plants/${selectedPlantDetails.id}`} className="w-full mt-6 block">
  <Button variant="outline" className="w-full">
    Full Medicinal Profile →
  </Button>
</Link>
                  </CardContent>
                </Card>
              )}

              {/* Feedback */}
              <Card className="border-orange-200 bg-orange-50">
                <CardContent className="p-6">
                  <h4 className="font-semibold text-orange-800 mb-4 flex items-center gap-2">
                    Was this identification accurate?
                  </h4>
                  <div className="flex gap-3">
                    <Button 
                      variant="outline" 
                      className="flex-1 gap-2 h-12"
                      onClick={() => {
                        localStorage.setItem(`feedback_${predictMutation.data.predicted_class}_${Date.now()}`, 'wrong')
                        toast.success("Thank you for the feedback! This helps improve our AI.")
                      }}
                    >
                      <ThumbsDown className="h-4 w-4" />
                      Wrong result
                    </Button>
                    <Button 
                      className="flex-1 gap-2 h-12 bg-emerald-500 hover:bg-emerald-600"
                      onClick={() => toast.success("Great! Marked as correct.")}
                    >
                      <ThumbsUp className="h-4 w-4" />
                      Correct
                    </Button>
                  </div>
                </CardContent>
              </Card>
=======
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
>>>>>>> 381b452bb68fcd83567a866ff7e8e5eb92cbb57c
            </div>

            {/* Results Panel */}
            <div className="space-y-6">
              {predictMutation.isPending && <Card className="p-8 animate-pulse"><div className="h-64 bg-muted rounded-2xl" /></Card>}
              {predictMutation.isSuccess && (
                <div className="space-y-6">
                  <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-50 shadow-2xl overflow-hidden p-6">
                    <h3 className="text-4xl font-black text-emerald-950 mb-4">{predictMutation.data.predicted_class.replace(/_/g, " ")}</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center bg-white/60 p-4 rounded-2xl border">
                            <span className="font-bold text-emerald-800">Confidence</span>
                            <span className="text-2xl font-black text-emerald-600">{(predictMutation.data.confidence * 100).toFixed(1)}%</span>
                        </div>
                        {predictMutation.data.gradcam_base64 && (
                            <div className="rounded-2xl overflow-hidden border-2 border-emerald-200">
                                <img src={`data:image/jpeg;base64,${predictMutation.data.gradcam_base64}`} alt="Heatmap" className="w-full" />
                            </div>
                        )}
                        <SafetyBadge isToxic={predictMutation.data.is_toxic} caution={predictMutation.data.caution} />
                    </div>
                  </Card>
                </div>
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
