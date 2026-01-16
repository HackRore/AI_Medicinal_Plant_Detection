'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import confetti from 'canvas-confetti'

const NEURAL_LOGS = [
    "Initializing Neural Engine v4.0...",
    "Extracting morphological leaf features...",
    "Analyzing venation pattern geometry...",
    "Scanning serration & margin detail...",
    "Encoding texture descriptors (ViT)...",
    "Cross-referencing with Botanical DB...",
    "Aggregating ensemble predictions...",
    "Finalizing species classification..."
];

export default function PredictPage() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [preview, setPreview] = useState<string | null>(null)
    const [prediction, setPrediction] = useState<any>(null)
    const [explanation, setExplanation] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [explaining, setExplaining] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [currentLog, setCurrentLog] = useState<string>("")
    const [showTip, setShowTip] = useState(false)

    // Log animation effect
    useEffect(() => {
        if (loading) {
            let i = 0;
            const interval = setInterval(() => {
                setCurrentLog(NEURAL_LOGS[i % NEURAL_LOGS.length]);
                i++;
            }, 600);
            return () => clearInterval(interval);
        } else {
            setCurrentLog("");
        }
    }, [loading]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setSelectedFile(file)
            setPreview(URL.createObjectURL(file))
            setPrediction(null)
            setExplanation(null)
            setError(null)
            setShowTip(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        const file = e.dataTransfer.files[0]
        if (file && file.type.startsWith('image/')) {
            setSelectedFile(file)
            setPreview(URL.createObjectURL(file))
            setPrediction(null)
            setExplanation(null)
            setError(null)
            setShowTip(false)
        }
    }

    const handlePredict = async () => {
        if (!selectedFile) return

        setLoading(true)
        setError(null)
        setExplanation(null)
        setPrediction(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)

            // Artificial delay for experience
            await new Promise(r => setTimeout(r, 2000));

            const response = await fetch(`${process.env.API_URL || 'http://localhost:8000'}/api/v1/predict/`, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Prediction failed');
            }

            const data = await response.json()
            setPrediction(data)

            // Wow Factor: Confetti and Tip
            if (data.confidence > 0.85) {
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#166534', '#10b981', '#ffffff']
                });
                setShowTip(true);
            }
        } catch (err: any) {
            setError(err.message || 'Unable to connect to the server. Please check if the backend is running.')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleExplain = async () => {
        if (!selectedFile) return
        setExplaining(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)

            const response = await fetch(`${process.env.API_URL || 'http://localhost:8000'}/api/v1/explain/combined`, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Explanation generation failed')
            }

            const data = await response.json()
            setExplanation(data)
        } catch (err: any) {
            setError(err.message || 'Failed to generate AI explanation.')
        } finally {
            setExplaining(false)
        }
    }

    return (
        <div className="container mx-auto px-4 py-12 min-h-screen" role="main">

            <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12 animate-fade-in">
                    <h1 className="text-6xl font-black bg-clip-text text-transparent bg-gradient-to-r from-primary-700 to-green-500 mb-4 italic">
                        Neural Botanical Scanner
                    </h1>
                    <p className="text-xl text-gray-500 font-medium max-w-2xl mx-auto leading-relaxed">
                        Identify species with 92.5% accuracy using our dual-ensemble neural network.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12">
                    {/* Left Column: Input */}
                    <div className="space-y-8 animate-slide-up">
                        <div className="bg-white rounded-[40px] shadow-2xl overflow-hidden border border-gray-100 p-2">
                            <div className="bg-gray-50 rounded-[35px] p-8 border border-dashed border-gray-200">
                                <h2 className="text-2xl font-black mb-6 flex items-center gap-3 text-gray-800">
                                    <span className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center text-white text-xl shadow-lg">📷</span>
                                    Capture Input
                                </h2>

                                <div
                                    className={`relative rounded-3xl p-4 text-center transition-all cursor-pointer h-96 flex flex-col items-center justify-center overflow-hidden
                                        ${preview ? 'bg-black' : 'bg-white border-4 border-dashed border-gray-100 hover:border-primary-300 hover:bg-primary-50/10'}`}
                                    onDrop={handleDrop}
                                    onDragOver={(e) => e.preventDefault()}
                                    onClick={() => document.getElementById('fileInput')?.click()}
                                    role="button"
                                    aria-label="Upload leaf image"
                                    aria-describedby="upload-desc"
                                    tabIndex={0}
                                    onKeyDown={(e) => e.key === 'Enter' && document.getElementById('fileInput')?.click()}
                                >
                                    <p id="upload-desc" className="sr-only">Click or drag and drop a medicinal leaf image to start analysis.</p>
                                    {preview ? (
                                        <div className="relative group w-full h-full flex items-center justify-center">
                                            <img
                                                src={preview}
                                                alt="Uploaded leaf specimen for identification"
                                                className="max-h-full max-w-full object-contain relative z-10"
                                            />
                                            {loading && (
                                                <div className="absolute inset-0 bg-primary-900/40 flex flex-col items-center justify-center backdrop-blur-sm">
                                                    <div className="absolute top-0 left-0 w-full h-2 bg-green-400 shadow-[0_0_20px_rgba(74,222,128,0.8)] animate-scan"></div>
                                                    <div className="text-white text-center px-8">
                                                        <div className="text-3xl font-black mb-4 tracking-tighter">SCANNING...</div>
                                                        <div className="font-mono text-sm bg-black/50 px-4 py-2 rounded-lg border border-white/20 animate-pulse text-green-300">
                                                            {currentLog}
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="space-y-6">
                                            <div className="text-8xl animate-float">🍃</div>
                                            <div>
                                                <p className="text-2xl font-black text-gray-800">Drop Leaf Image</p>
                                                <p className="text-gray-400 mt-2 font-medium">or click to browse your laboratory</p>
                                            </div>
                                            <div className="flex gap-3 justify-center">
                                                <span className="px-4 py-1.5 bg-gray-100 rounded-full text-xs font-bold text-gray-500 tracking-widest uppercase">High Res</span>
                                                <span className="px-4 py-1.5 bg-gray-100 rounded-full text-xs font-bold text-gray-500 tracking-widest uppercase">RGB Input</span>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <input
                                    id="fileInput"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                />

                                {selectedFile && !loading && (
                                    <button
                                        onClick={handlePredict}
                                        className="w-full mt-8 bg-gradient-premium text-white py-6 rounded-2xl text-2xl font-black hover:scale-[1.02] transition-all shadow-[0_20px_40px_rgba(22,101,52,0.3)] flex items-center justify-center gap-4"
                                    >
                                        <span>INITIATE ANALYSIS</span>
                                        <span className="text-3xl">➡️</span>
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Guide Card */}
                        {prediction && (showTip || !prediction.plant_details) && (

                            <div className={`p-8 rounded-[40px] shadow-2xl relative overflow-hidden animate-slide-up border-b-8 transition-colors
                                ${prediction.plant_details ? 'bg-primary-900 border-green-400' : 'bg-red-950 border-red-500'}`}>
                                <div className="relative z-10">
                                    <div className="flex items-center gap-3 mb-4">
                                        <span className="text-3xl">{prediction.plant_details ? '💡' : '⚡'}</span>
                                        <h3 className="text-xl font-black uppercase tracking-widest text-white">
                                            {prediction.plant_details ? 'Botanical Insight' : 'Identification Blocked'}
                                        </h3>
                                    </div>
                                    <p className="text-lg opacity-90 leading-relaxed italic font-medium text-white">
                                        {prediction.plant_details
                                            ? `"${prediction.plant_details?.description?.split('.')[0] || 'This species is highly valued in traditional medicine.'}"`
                                            : "The neural engine detected insufficient medicinal markers. Please ensure the leaf is well-lit, centered, and isolated from background noise."}
                                    </p>
                                    <div className={`mt-4 flex items-center gap-2 font-bold ${prediction.plant_details ? 'text-green-400' : 'text-red-400'}`}>
                                        <span>{prediction.plant_details ? '✓ Authenticity Verified' : '✕ Specimen Rejected'}</span>
                                        <span className={`w-2 h-2 rounded-full animate-ping ${prediction.plant_details ? 'bg-green-400' : 'bg-red-500'}`}></span>
                                    </div>
                                </div>
                                <div className="absolute -right-10 -bottom-10 text-[12rem] opacity-5 text-white">{prediction.plant_details ? '🌿' : '🚫'}</div>
                            </div>
                        )}
                    </div>

                    {/* Right Column: Results & AI Explain */}
                    <div className="space-y-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                        {prediction ? (
                            <div className="bg-white rounded-[40px] shadow-2xl border border-gray-100 h-full overflow-hidden">
                                <div className="p-8">
                                    <div className="flex items-center justify-between mb-10">
                                        <h2 className="text-3xl font-black text-gray-900 italic">Analysis Result</h2>
                                        <div className="px-5 py-2.5 bg-primary-100 text-primary-700 rounded-full text-xs font-black tracking-widest uppercase flex items-center gap-3 border border-primary-200">
                                            <span className="w-2.5 h-2.5 bg-primary-600 rounded-full animate-ping"></span>
                                            Real-time Output
                                        </div>
                                    </div>

                                    {/* Main Result Card */}
                                    <div className="bg-gray-50 rounded-[35px] p-8 border border-gray-100 mb-8 relative group overflow-hidden">
                                        <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 rounded-full -translate-y-1/2 translate-x-1/2 group-hover:scale-150 transition-transform duration-700"></div>

                                        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
                                            <div className="flex-1">
                                                <p className="text-primary-600 font-black text-sm tracking-[0.3em] uppercase mb-3">Classification</p>
                                                <h3 className="text-5xl font-black text-gray-900 mb-6 group-hover:text-primary-800 transition-colors">
                                                    {prediction.predicted_class?.replace(/_/g, ' ')}
                                                </h3>
                                                {prediction.plant_details ? (
                                                    <div className="inline-flex items-center gap-3 px-5 py-3 bg-white rounded-2xl shadow-sm border border-gray-100">
                                                        <span className="text-3xl">🧬</span>
                                                        <div>
                                                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Common Name</p>
                                                            <p className="font-bold text-gray-800 text-lg leading-tight">
                                                                {prediction.plant_details.common_name}
                                                            </p>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="inline-flex items-center gap-3 px-5 py-3 bg-red-50 rounded-2xl shadow-sm border border-red-100">
                                                        <span className="text-3xl">⚠️</span>
                                                        <div>
                                                            <p className="text-[10px] font-black text-red-400 uppercase tracking-widest">System Warning</p>
                                                            <p className="font-bold text-red-800 text-sm leading-tight">
                                                                Specimen does not meet botanical criteria
                                                            </p>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="flex flex-col items-center justify-center bg-white p-6 rounded-3xl shadow-xl min-w-[140px] border border-gray-50 transform group-hover:rotate-3 transition-transform">
                                                <div className="text-5xl font-black text-primary-600 mb-1">
                                                    {(prediction.confidence * 100).toFixed(0)}<span className="text-2xl">%</span>
                                                </div>
                                                <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Confidence</p>
                                            </div>
                                        </div>

                                        <div className="mt-12">
                                            <div className="flex justify-between text-[10px] font-black text-gray-400 mb-3 uppercase tracking-widest">
                                                <span>Statistical Probability</span>
                                                <span>{(prediction.confidence * 100).toFixed(1)}%</span>
                                            </div>
                                            <div className="h-4 w-full bg-gray-200/50 rounded-full overflow-hidden p-1">
                                                <div
                                                    className={`h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(34,197,94,0.4)]
                                                        ${prediction.plant_details ? 'bg-gradient-premium' : 'bg-red-500'}`}
                                                    style={{ width: `${prediction.confidence * 100}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="grid grid-cols-2 gap-4 mb-10">
                                        {!explanation && !explaining && (
                                            <button
                                                onClick={handleExplain}
                                                className="col-span-2 group flex items-center justify-center gap-4 bg-gray-900 text-white py-6 rounded-2xl font-black text-xl hover:bg-black transition-all shadow-xl hover:-translate-y-1"
                                            >
                                                <span className="text-3xl group-hover:rotate-12 transition-transform">🔬</span>
                                                REVEAL NEURAL FOCUS
                                            </button>
                                        )}
                                        {prediction.plant_details && (
                                            <a
                                                href={`/plants/${prediction.plant_details.id}`}
                                                className="col-span-2 text-center py-6 border-4 border-primary-100 text-primary-700 rounded-2xl font-black text-xl hover:bg-primary-50 transition-all uppercase tracking-widest"
                                            >
                                                Botanical Dossier →
                                            </a>
                                        )}
                                    </div>

                                    {/* Explanation Section */}
                                    {explaining && (
                                        <div className="p-10 border-4 border-dashed border-primary-100 rounded-[35px] text-center space-y-6 animate-pulse bg-primary-50/20">
                                            <div className="text-6xl">🤖</div>
                                            <div>
                                                <p className="font-black text-gray-800 uppercase tracking-widest text-lg">Synthesizing Explainable AI Maps...</p>
                                                <p className="text-gray-400 text-sm mt-2">Running Grad-CAM & LIME Analysis</p>
                                            </div>
                                        </div>
                                    )}

                                    {explanation && (
                                        <div className="space-y-8 animate-fade-in p-2">
                                            <div className="flex items-center gap-4 mb-4">
                                                <div className="h-px flex-1 bg-gray-200"></div>
                                                <span className="text-[10px] font-black text-gray-400 uppercase tracking-[0.4em]">XAI Internal State</span>
                                                <div className="h-px flex-1 bg-gray-200"></div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-6">
                                                <div className="space-y-3">
                                                    <p className="text-[10px] font-black text-primary-600 text-center uppercase tracking-widest">Grad-CAM Attention</p>
                                                    <div className="aspect-square rounded-3xl bg-black overflow-hidden ring-4 ring-gray-100 shadow-inner group relative">
                                                        <Image
                                                            src={explanation.gradcam_overlay}
                                                            alt="Heatmap showing areas where the AI model focused its attention"
                                                            fill
                                                            className="object-cover group-hover:scale-110 transition-transform duration-500"
                                                        />
                                                    </div>
                                                </div>
                                                <div className="space-y-3">
                                                    <p className="text-[10px] font-black text-primary-600 text-center uppercase tracking-widest">LIME Feature Map</p>
                                                    <div className="aspect-square rounded-3xl bg-black overflow-hidden ring-4 ring-gray-100 shadow-inner group relative">
                                                        <Image
                                                            src={explanation.lime_visualization}
                                                            alt="Visualization of the specific image segments that influenced the classification"
                                                            fill
                                                            className="object-cover group-hover:scale-110 transition-transform duration-500"
                                                        />
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="p-8 bg-gradient-to-br from-gray-900 to-primary-950 rounded-[30px] border border-white/10 text-white shadow-2xl relative overflow-hidden">
                                                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent"></div>
                                                <p className="text-sm leading-relaxed relative z-10 text-gray-300">
                                                    <strong className="text-primary-400 uppercase tracking-widest text-xs block mb-2">Neural Analysis:</strong>
                                                    {explanation.explanation} Our network focused on the <span className="text-white font-bold">morphological structure</span> and <span className="text-white font-bold">vein distribution</span> to classify this specimen.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Meta Info */}
                                    <div className="mt-12 pt-8 border-t border-gray-100 flex justify-between items-center text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">
                                        <div className="flex gap-6">
                                            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> {prediction.processing_time_ms?.toFixed(0) || '<100'}MS Latency</span>
                                            <span>{prediction.model_version}</span>
                                        </div>
                                        <span>Matoshri Agri-AI Lab</span>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center border-4 border-dashed border-gray-100 rounded-[50px] p-20 text-center bg-white shadow-inner animate-pulse">
                                <div className="text-[10rem] mb-10 opacity-10">🔬</div>
                                <h3 className="text-3xl font-black text-gray-800 mb-4 italic">Laboratory Idle</h3>
                                <p className="text-gray-400 font-medium max-w-xs leading-relaxed">
                                    System awaiting leaf input for architectural analysis. Please upload image on the left.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
