'use client'

import { useState, useRef, useCallback, useEffect } from "react"
import Image from "next/image"
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import confetti from "canvas-confetti"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { Camera, Upload, History, Sun, Moon, Zap, AlertCircle } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1"

interface Prediction {
  predicted_class: string
  predicted_class_index: number
  confidence: number
  top_predictions: Array<{ class_name: string; confidence: number }>
  model_version: string
  processing_time_ms?: number
}

export default function PredictPage() {
  const [preview, setPreview] = useState<string | null>(null)
  const [isDark, setIsDark] = useState(false)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [history, setHistory] = useState<Prediction[]>([])
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)


  // Simple theme state (no next-themes needed)
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const queryClient = useQueryClient()

  // History query
  const { data: serverHistory } = useQuery({
    queryKey: ["history"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/history`, { credentials: "include" })
      if (!res.ok) throw new Error("Failed to fetch history")
      return res.json() as Promise<Prediction[]>
    },
    staleTime: 5 * 60 * 1000,
  })

  useEffect(() => {
    if (serverHistory) setHistory(serverHistory)
  }, [serverHistory])

  // Predict mutation
  const predictMutation = useMutation({
    mutationFn: async (file: File): Promise<Prediction> => {
      const formData = new FormData()
      formData.append("file", file)
      const res = await fetch(`${API_BASE}/predict/`, { 
        method: "POST", 
        body: formData 
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || "Prediction failed")
      }
      return res.json()
    },
    onSuccess: (data) => {
      if (data.confidence > 0.85) {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } })
        toast.success(`Identified: ${data.predicted_class}`)
      }
      setPreview(URL.createObjectURL(new Blob([new ArrayBuffer(0)]))) // Reset preview
      queryClient.invalidateQueries({ queryKey: ["history"] })
    },
    onError: (err: any) => toast.error(err.message),
  })

  const handleCapture = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      canvasRef.current.width = videoRef.current.videoWidth
      canvasRef.current.height = videoRef.current.videoHeight
      const ctx = canvasRef.current.getContext("2d")
      ctx?.drawImage(videoRef.current, 0, 0)
      canvasRef.current.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "capture.jpg", { type: "image/jpeg" })
          setPreview(URL.createObjectURL(blob))
          predictMutation.mutate(file)
        }
      })
    }
  }, [predictMutation])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return
    if (files.length === 1) {
      const file = files[0]
      setPreview(URL.createObjectURL(file))
      predictMutation.mutate(file)
    } else {
      toast.info(`Processing ${files.length} photos...`)
      files.forEach((file, i) => {
        setTimeout(() => predictMutation.mutate(file), i * 500)
      })
    }
  }


  useEffect(() => {
    let stream: MediaStream | null = null
    if (isCameraOpen && videoRef.current) {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } } })

        .then((s) => {
          stream = s
          videoRef.current!.srcObject = s
        })
        .catch(toast.error)
    }
    return () => {
      if (stream) stream.getTracks().forEach((track) => track.stop())
    }
  }, [isCameraOpen])

  return (
    <main className="container mx-auto px-4 py-12 min-h-screen space-y-12" aria-label="Neural Botanical Scanner">
      {/* Theme Toggle */}
      <div className="flex justify-end">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label="Toggle dark mode"
          className="focus-ring"
        >
          {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
        </Button>
      </div>

      <header className="text-center">
        <h1 
          className="text-6xl font-black bg-gradient-to-r from-primary to-green-500 bg-clip-text text-transparent mb-4"
          aria-describedby="scanner-desc"
        >
          Neural Scanner
        </h1>
        <p id="scanner-desc" className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Live camera or upload for 92.5% accurate medicinal plant ID.
        </p>
      </header>

      <div className="grid lg:grid-cols-2 gap-12 items-start">
        {/* Input Column */}
        <section aria-labelledby="input-heading" className="space-y-6">
          <h2 id="input-heading" className="sr-only">Capture or Upload</h2>
          
          {/* Camera Modal */}
          {isCameraOpen && (
            <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
              <div className="bg-background rounded-3xl p-8 max-w-md w-full space-y-6 shadow-2xl focus-ring">
                <h3 className="text-2xl font-bold flex items-center gap-2">
                  <Camera size={28} />
                  Live Capture
                </h3>
                <div className="relative">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full h-64 object-cover rounded-2xl"
                    aria-label="Live camera preview"
                  />
                  <canvas ref={canvasRef} className="hidden" />
                </div>
                <div className="flex gap-4 pt-4">
                  <Button 
                    onClick={handleCapture}
                    size="lg" 
                    className="flex-1 gap-2 font-bold"
                    disabled={predictMutation.isPending}
                    aria-label="Capture photo from camera"
                  >
                    <Zap size={20} />
                    SCAN LIVE
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setIsCameraOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Upload/Camera Toggle */}
          <div className="grid grid-cols-2 gap-4">
            <label className="group cursor-pointer focus-ring">
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileSelect}
                className="sr-only"
                disabled={predictMutation.isPending}

              />
              <div className="p-8 rounded-3xl border-2 border-dashed border-muted hover:border-primary data-[disabled]:opacity-50 transition-all text-center focus-ring">
                <Upload size={48} className="mx-auto mb-4 text-muted-foreground group-hover:text-primary" />
                <div className="space-y-1">
                  <p className="font-bold text-lg">Upload Photos</p>
                  <p className="text-sm text-muted-foreground">JPG, PNG up to 10MB (Batch OK)</p>

                </div>
              </div>
            </label>
            <Button
              onClick={() => setIsCameraOpen(true)}
              size="lg"
              variant="outline"
              className="p-8 h-full gap-3 focus-ring"
              disabled={predictMutation.isPending}
            >
              <Camera size={48} />
              <div className="text-left">
                <p className="font-bold text-lg">Live Camera</p>
                <p className="text-sm text-muted-foreground">Use device camera</p>
              </div>
            </Button>
          </div>

          {predictMutation.isPending && (
            <div role="status" aria-live="polite" className="p-8 rounded-3xl bg-muted/50 border animate-pulse">
              <Skeleton className="h-64 w-full rounded-2xl mb-4" />
              <div className="space-y-2">
                <Skeleton className="h-8 w-3/4" />
                <Skeleton className="h-6 w-1/2" />
              </div>
            </div>
          )}

          {preview && !predictMutation.isPending && (
            <div className="relative group">
              <Image
                src={preview}
                alt="Leaf preview for analysis"
                width={400}
                height={300}
                className="w-full h-64 object-cover rounded-3xl shadow-2xl group-hover:scale-105 transition-transform"
              />
            </div>
          )}
        </section>

        {/* Results Column */}
        <section aria-labelledby="results-heading" className="space-y-6">
          <h2 id="results-heading" className="sr-only">Results & History</h2>
          
          {predictMutation.isError && (
            <div role="alert" aria-live="assertive" className="p-8 rounded-3xl border-2 border-destructive bg-destructive/10">
              <div className="flex items-start gap-4">
                <AlertCircle size={32} className="text-destructive mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-bold text-lg mb-2">Scan Failed</h3>
                  <p className="text-muted-foreground mb-4">{predictMutation.error.message}</p>
                  <Button 
                    onClick={() => predictMutation.reset()}
                    variant="outline"
                    size="sm"
                  >
                    Retry
                  </Button>
                </div>
              </div>
            </div>
          )}

          {predictMutation.isSuccess && (
            <article className="p-8 bg-card rounded-3xl shadow-xl border focus-ring" tabIndex={0}>
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h3 className="text-3xl font-black" aria-label={`Identified as ${predictMutation.data.predicted_class}`}>
                    {predictMutation.data.predicted_class.replace(/_/g, " ")}
                  </h3>
                  <p className="text-5xl font-black text-primary mt-2 mb-4">
                    {(predictMutation.data.confidence * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground mb-1">Model</p>
                  <p className="font-mono text-xs bg-muted px-3 py-1 rounded-full">
                    {predictMutation.data.model_version}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="space-y-1">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Top Alternatives</p>
                  <ul className="text-sm">
                    {predictMutation.data.top_predictions.slice(1, 4).map((pred, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{pred.class_name.replace(/_/g, " ")}</span>
                        <span className="font-mono">{(pred.confidence * 100).toFixed(1)}%</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  onClick={() => toast("History updated")}
                  className="flex-1 gap-2"
                >
                  <History size={20} />
                  Save to History
                </Button>
              </div>
            </article>
          )}

          {/* Recent History */}
          <div className="space-y-4">
            <h4 className="font-bold text-lg flex items-center gap-2">
              Recent Scans <span className="text-sm text-muted-foreground">(last 5)</span>
            </h4>
            {history.length === 0 ? (
              <Skeleton className="h-20 w-full rounded-xl" />
            ) : (
              <div className="space-y-3 max-h-48 overflow-y-auto">
                {history.slice(0, 5).map((item, i) => (
                  <div key={i} className="flex gap-4 p-4 bg-muted rounded-xl group hover:bg-accent focus-ring" tabIndex={0}>
                    <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center text-2xl">
                      🍃
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold truncate">{item.predicted_class.replace(/_/g, " ")}</p>
                      <p className="text-sm text-muted-foreground truncate">{item.model_version}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono text-sm">{(item.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}

