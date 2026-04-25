'use client'

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import Image from "next/image"
import { toast } from "sonner"
import { Upload } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com") + "/api/v1"

export default function ExplainPage() {
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const explainMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append("file", file)
      const res = await fetch(`${API_BASE}/explain/combined`, { 
        method: "POST", 
        body: formData 
      })
      if (!res.ok) throw new Error("Explain failed")
      return res.json()
    },
    onSuccess: (data) => {
      setResult(data)
      toast.success("Explanation generated!")
    },
    onError: (err: any) => toast.error(err.message),
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFileName(file.name)
      setImagePreview(URL.createObjectURL(file))
      setLoading(true)
      explainMutation.mutate(file)
    }
  }

  return (
    <div className="container mx-auto px-4 py-12 space-y-8">
      <div className="text-center">
        <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
          Explain My Prediction
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Upload leaf for Grad-CAM + LIME analysis showing why model chose that plant.
        </p>
      </div>

      {/* Upload */}
      <div className="max-w-2xl mx-auto">
        <label className="block w-full cursor-pointer focus-ring p-8 border-2 border-dashed border-muted rounded-3xl hover:border-primary transition-colors text-center">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="sr-only"
          />
          <Upload className="w-16 h-16 mx-auto mb-4 opacity-75" />
          <p className="font-bold text-lg mb-1">Upload Leaf for Analysis</p>
          <p className="text-sm text-muted-foreground">JPG/PNG - Get Grad-CAM heatmap</p>
        </label>
      </div>

      {/* Preview */}
      {imagePreview && (
        <div className="max-w-2xl mx-auto">
          <Image
            src={imagePreview}
            alt="Preview"
            width={512}
            height={512}
            className="w-full rounded-3xl shadow-xl mx-auto"
          />
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="max-w-4xl mx-auto space-y-4">
          <Skeleton className="h-96 w-full rounded-3xl" />
          <div className="space-y-2">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-3/4" />
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Prediction */}
          <div className="bg-card p-8 rounded-3xl shadow-xl border">
            <h2 className="text-3xl font-bold mb-6">Prediction</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <p className="text-5xl font-black text-primary mb-2">
                  {(result?.prediction?.predicted_class || "Unknown Species").toString().replace(/_/g, " ")}
                </p>
                <p className="text-3xl font-bold text-green-500">
                  {((result?.prediction?.confidence ?? 0) * 100).toFixed(1)}% Confidence
                </p>
              </div>
              <div className="space-y-4">
                <p className="font-mono text-sm bg-muted px-4 py-2 rounded-lg">
                  Model: {result?.model_version ?? "Ensemble"}
                </p>
                <Button variant="outline" onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}>
                  Copy JSON
                </Button>
              </div>
            </div>
          </div>

          {/* Grad-CAM */}
          {result?.gradcam && (
            <div className="bg-gradient-to-r from-orange-500/10 to-pink-500/10 p-8 rounded-3xl border border-orange-200">
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-2">
                🎯 Grad-CAM Heatmap
                <span className="text-sm bg-orange-200 px-3 py-1 rounded-full font-mono">Model Attention</span>
              </h2>
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div>
                  <img src={result?.gradcam?.heatmap ?? ""} alt="Grad-CAM" className="w-full rounded-2xl shadow-2xl max-h-96 object-contain" />
                </div>
                <div className="space-y-4">
                  <p className="text-muted-foreground">
                    {result?.gradcam?.explanation ?? "Generating scientific local attention markers..."}
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-orange-50 p-4 rounded-xl">
                      <p className="font-bold text-orange-800">Bright Red</p>
                      <p className="text-orange-600">High Importance</p>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-xl">
                      <p className="font-bold text-blue-800">Blue</p>
                      <p className="text-blue-600">Low Importance</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* LIME */}
          {result?.lime && (
            <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 p-8 rounded-3xl border border-green-200">
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-2">
                🔍 LIME Explanation
                <span className="text-sm bg-green-200 px-3 py-1 rounded-full font-mono">Local Features</span>
              </h2>
              <div className="grid md:grid-cols-2 gap-8">
                <img src={result?.lime?.feature_map ?? ""} alt="LIME" className="w-full rounded-2xl shadow-2xl" />
                <div className="space-y-4">
                  <p className="text-muted-foreground">
                    {result?.lime?.explanation ?? "Synthesizing secondary verification map..."}
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-50 p-4 rounded-xl">
                      <p className="font-bold text-green-800">Green Regions</p>
                      <p className="text-green-600">Support Prediction</p>
                    </div>
                    <div className="bg-red-50 p-4 rounded-xl">
                      <p className="font-bold text-red-800">Red Regions</p>
                      <p className="text-red-600">Oppose Prediction</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Reasoning */}
          {result?.botanical_reasoning && (
            <div className="bg-gradient-to-r from-indigo-500/10 p-8 rounded-3xl border border-indigo-200">
              <h2 className="text-3xl font-bold mb-6">🧠 Botanical Reasoning</h2>
              <p className="text-lg leading-relaxed prose prose-indigo max-w-none">
                {result?.botanical_reasoning ?? "Generating scientific rationale..."}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

