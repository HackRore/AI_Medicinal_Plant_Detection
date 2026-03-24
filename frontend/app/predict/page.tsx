'use client'

import { useState, useRef, useCallback, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import confetti from "canvas-confetti"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { Progress } from "@/components/ui/progress"
import { Camera, Upload, History, Sun, Moon, Zap, AlertCircle, ThumbsUp, ThumbsDown, Copy, Leaf } from "lucide-react"
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
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const queryClient = useQueryClient()

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
        
        const res = await fetch(`${API_BASE}/api/v1/predict/`, {
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
          AI-powered medicinal plant detection with toxicity warnings and detailed Ayurvedic information
        </p>
      </header>

      <div className="grid lg:grid-cols-2 gap-12 items-start">
        {/* Input Panel */}
        <div className="space-y-6">
          {/* Upload & Camera Controls */}
          <div className="grid md:grid-cols-2 gap-6">
            <label className="group cursor-pointer block p-8 border-2 border-dashed border-muted rounded-3xl hover:border-primary transition-all text-center focus-within:ring-4 ring-primary/20">
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileSelect}
                className="sr-only"
                disabled={predictMutation.isPending}
              />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground group-hover:text-primary mb-4" />
              <div className="space-y-1">
                <p className="font-bold text-lg">Upload Images</p>
                <p className="text-sm text-muted-foreground">JPG/PNG (max 3, 10MB each)</p>
              </div>
            </label>

            <Button
              onClick={() => setIsCameraOpen(true)}
              size="lg"
              variant="outline"
              className="h-full p-8 gap-3"
              disabled={predictMutation.isPending}
            >
              <Camera className="h-12 w-12" />
              <div className="text-left">
                <p className="font-bold text-lg">Live Camera</p>
                <p className="text-sm text-muted-foreground">Instant scan</p>
              </div>
            </Button>
          </div>

          {/* Image Previews */}
          {uploadedImages.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {uploadedImages.map((img, i) => (
                <div key={i} className="group relative rounded-2xl overflow-hidden shadow-lg border">
                  <Image
                    src={img.preview}
                    alt={`Preview ${i+1}`}
                    width={300}
                    height={200}
                    className="w-full h-40 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <button
                    onClick={() => setUploadedImages(prev => prev.filter((_, idx) => idx !== i))}
                    className="absolute top-2 right-2 bg-destructive text-destructive-foreground rounded-full p-1.5 shadow-lg opacity-0 group-hover:opacity-100 transition-all hover:scale-110"
                    title="Remove"
                  >
                    <AlertCircle className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Loading State */}
          {predictMutation.isPending && (
            <Card className="p-8 animate-pulse">
              <div className="space-y-4">
                <div className="h-64 bg-muted rounded-2xl" />
                <div className="flex items-center gap-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
                  <div className="flex-1 space-y-2">
                    <div className="h-6 bg-muted rounded-full w-3/4" />
                    <div className="h-4 bg-muted rounded-full w-1/2" />
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {/* Error State */}
          {predictMutation.isError && (
            <Card className="border-destructive bg-destructive/5">
              <CardContent className="p-8">
                <div className="flex items-start gap-4">
                  <AlertCircle className="h-10 w-10 text-destructive mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-bold text-xl mb-2 text-destructive-foreground">
                      Analysis Failed
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      {predictMutation.error?.message || 'Unknown error'}
                    </p>
                    <Button onClick={() => predictMutation.reset()} variant="outline" size="sm">
                      Try Again
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Success State */}
          {predictMutation.isSuccess && (
            <div className="space-y-6">
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
                      <span className="text-sm font-bold text-emerald-800">Neural Confidence</span>
                      <span className="text-3xl font-black text-emerald-600">
                        {(predictMutation.data.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={predictMutation.data.confidence * 100} className="h-4 bg-emerald-100/50" />
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
            </div>
          )}

          {/* History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Detection History (Last 10)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {localHistory.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  No detections yet. Upload your first plant image!
                </p>
              ) : (
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {localHistory.map((item) => (
                    <div key={item.id} className="flex gap-4 p-4 hover:bg-accent rounded-xl group transition-all cursor-pointer" onClick={() => {
                      // Re-show this prediction
                    }}>
                      <div className="w-20 h-20 flex-shrink-0 rounded-xl overflow-hidden shadow-md">
                        <Image 
                          src={item.thumb} 
                          alt="Plant thumbnail"
                          width={80}
                          height={80}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-lg truncate">
                          {item.prediction.predicted_class.replace(/_/g, " ")}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right flex flex-col items-end gap-1 min-w-[80px]">
                        <div className="font-mono text-sm font-bold text-primary">
                          {(item.prediction.confidence * 100).toFixed(0)}%
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="h-8 px-3 text-xs h-fit"
                          onClick={(e) => {
                            e.stopPropagation()
                            navigator.clipboard.writeText(item.prediction.predicted_class)
                            toast.success("Copied plant name!")
                          }}
                        >
                          Copy
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Camera Modal */}
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
