'use client'

import { useState } from 'react'

// CSS for scanning animation
const scannerStyle = `
@keyframes scan {
    0% { top: 0%; opacity: 0; }
    5% { opacity: 1; }
    90% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}
.animate-scan {
    animation: scan 2s linear infinite;
}
`;

export default function PredictPage() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [preview, setPreview] = useState<string | null>(null)
    const [prediction, setPrediction] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setSelectedFile(file)
            setPreview(URL.createObjectURL(file))
            setPrediction(null)
            setError(null)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        const file = e.dataTransfer.files[0]
        if (file && file.type.startsWith('image/')) {
            setSelectedFile(file)
            setPreview(URL.createObjectURL(file))
            setPrediction(null)
            setError(null)
        }
    }

    const handlePredict = async () => {
        if (!selectedFile) return

        setLoading(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)

            const response = await fetch(`${process.env.API_URL || 'http://localhost:8000'}/api/v1/predict/`, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Prediction failed')
            }

            const data = await response.json()
            setPrediction(data)
        } catch (err) {
            setError('Unable to connect to the server. Please check if the backend is running.')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container mx-auto px-4 py-12">
            <style>{scannerStyle}</style>
            <h1 className="text-4xl font-bold text-center text-primary-700 mb-8">
                Plant Identification
            </h1>

            <div className="max-w-4xl mx-auto">
                {/* Upload Section */}
                <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Upload Leaf Image</h2>

                    <div
                        className="border-4 border-dashed border-primary-300 rounded-lg p-12 text-center hover:border-primary-500 transition-colors cursor-pointer"
                        onDrop={handleDrop}
                        onDragOver={(e) => e.preventDefault()}
                        onClick={() => document.getElementById('fileInput')?.click()}
                    >
                        {preview ? (
                            <div className="space-y-4">
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="max-h-64 mx-auto rounded-lg shadow-md"
                                />
                                <p className="text-gray-600">Click to change image</p>
                            </div>
                        ) : (
                            <div>
                                <div className="text-6xl mb-4">📸</div>
                                <p className="text-xl text-gray-700 mb-2">
                                    Drop an image here or click to browse
                                </p>
                                <p className="text-gray-500">
                                    Supports JPG, PNG (max 10MB)
                                </p>
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

                    {selectedFile && (
                        <div className="mt-6">
                            {loading ? (
                                <div className="space-y-4">
                                    <div className="relative overflow-hidden h-64 rounded-lg bg-gray-900 shadow-inner">
                                        <img
                                            src={preview!}
                                            className="w-full h-full object-contain opacity-50"
                                            alt="Scanning..."
                                        />
                                        <div className="absolute top-0 left-0 w-full h-1 bg-green-500 shadow-[0_0_15px_rgba(34,197,94,0.8)] animate-scan"></div>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <p className="text-green-400 font-mono text-lg animate-pulse">ANALYZING LEAF STRUCTURE...</p>
                                        </div>
                                    </div>
                                    <p className="text-gray-500 text-center text-sm">Please wait while our AI identifies the plant species...</p>
                                </div>
                            ) : (
                                <button
                                    onClick={handlePredict}
                                    className="w-full bg-gradient-to-r from-primary-600 to-primary-500 text-white py-4 rounded-lg text-lg font-bold hover:from-primary-700 hover:to-primary-600 transform hover:scale-[1.02] transition-all shadow-lg hover:shadow-primary-500/30 ring-2 ring-primary-400/20"
                                >
                                    Identify Plant
                                </button>
                            )}
                        </div>
                    )}

                    {error && (
                        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Section */}
                {prediction && (
                    <div className="bg-white rounded-xl shadow-lg p-8 animate-slide-up">
                        <h2 className="text-2xl font-bold mb-6">Prediction Results</h2>

                        {/* Main Prediction */}
                        <div className="bg-primary-50 rounded-lg p-6 mb-6">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <h3 className="text-2xl font-bold text-primary-800">
                                        {prediction.predicted_plant?.replace(/_/g, ' ')}
                                    </h3>
                                    {prediction.plant_details && (
                                        <p className="text-gray-600 mt-1">
                                            {prediction.plant_details.common_name}
                                        </p>
                                    )}
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-bold text-primary-600">
                                        {(prediction.confidence * 100).toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-gray-600">Confidence</div>
                                </div>
                            </div>

                            {/* Confidence Bar */}
                            <div className="w-full bg-gray-200 rounded-full h-3">
                                <div
                                    className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                                    style={{ width: `${prediction.confidence * 100}%` }}
                                />
                            </div>
                        </div>

                        {/* Plant Details */}
                        {prediction.plant_details && (
                            <div className="mb-6">
                                <h4 className="font-bold text-lg mb-2">About This Plant</h4>
                                <p className="text-gray-700">
                                    {prediction.plant_details.description}
                                </p>
                                <a
                                    href={`/plants/${prediction.plant_details.id}`}
                                    className="inline-block mt-4 text-primary-600 hover:text-primary-700 font-semibold"
                                >
                                    View Full Details →
                                </a>
                            </div>
                        )}

                        {/* Top Predictions */}
                        {prediction.top_predictions && prediction.top_predictions.length > 1 && (
                            <div>
                                <h4 className="font-bold text-lg mb-3">Alternative Predictions</h4>
                                <div className="space-y-2">
                                    {prediction.top_predictions.slice(1, 4).map((pred: any, idx: number) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                            <span className="text-gray-700">
                                                {pred.class_name?.replace(/_/g, ' ')}
                                            </span>
                                            <span className="text-gray-600 font-semibold">
                                                {(pred.confidence * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Processing Info */}
                        <div className="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-500">
                            <div className="flex justify-between">
                                <span>Processing Time:</span>
                                <span>{prediction.processing_time_ms?.toFixed(0)}ms</span>
                            </div>
                            <div className="flex justify-between mt-1">
                                <span>Model Version:</span>
                                <span>{prediction.model_version}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
