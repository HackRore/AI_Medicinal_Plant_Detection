'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

interface MedicinalProperty {
    ailment: string
    usage: string
    preparation: string
    dosage: string
    precautions: string
}

interface PlantDetails {
    id: number
    species_name: string
    common_names: {
        en: string
        hi: string
        ta: string
        te: string
        bn: string
    }
    scientific_classification: string
    description: string
    image_url: string
    medicinal_properties: MedicinalProperty[]
}

export default function PlantDetailPage() {
    const params = useParams()
    const [plant, setPlant] = useState<PlantDetails | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (params.id) {
            fetchPlantDetails(params.id as string)
        }
    }, [params.id])

    const fetchPlantDetails = async (id: string) => {
        try {
            const res = await fetch(`${process.env.API_URL || 'http://localhost:8000'}/api/v1/plants/${id}`)
            if (res.ok) {
                const data = await res.json()
                setPlant(data)
            }
        } catch (error) {
            console.error('Failed to fetch plant details:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-12 animate-pulse">
                <div className="h-96 bg-gray-200 rounded-xl mb-8" />
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-4" />
                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                <div className="h-4 bg-gray-200 rounded w-3/4" />
            </div>
        )
    }

    if (!plant) {
        return (
            <div className="container mx-auto px-4 py-20 text-center">
                <h1 className="text-3xl font-bold text-gray-800 mb-4">Plant Not Found</h1>
                <Link href="/plants" className="text-primary-600 hover:underline">
                    ← Back to Plants
                </Link>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <Link
                href="/plants"
                className="inline-flex items-center text-gray-600 hover:text-primary-600 mb-6 transition-colors"
            >
                ← Back to Plants
            </Link>

            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                {/* Header Image */}
                <div className="relative h-[400px] w-full">
                    <img
                        src={plant.image_url}
                        alt={plant.species_name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/1200x600?text=No+Image+Available'
                        }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end">
                        <div className="p-8 text-white w-full">
                            <h1 className="text-5xl font-bold mb-2">
                                {plant.common_names.en}
                            </h1>
                            <p className="text-xl font-mono opacity-90 italic">
                                {plant.species_name.replace(/_/g, ' ')}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="p-8 lg:p-12">
                    <div className="grid lg:grid-cols-3 gap-12">
                        {/* Main Content */}
                        <div className="lg:col-span-2 space-y-8">
                            {/* Description */}
                            <section>
                                <h2 className="text-2xl font-bold text-primary-800 mb-4 flex items-center gap-2">
                                    <span>📖</span> About
                                </h2>
                                <p className="text-gray-700 leading-relaxed text-lg">
                                    {plant.description}
                                </p>
                            </section>

                            {/* Regional Names */}
                            <section className="bg-orange-50 p-6 rounded-xl border border-orange-100">
                                <h2 className="text-xl font-bold text-orange-800 mb-4">Regional Names</h2>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div>
                                        <span className="text-xs uppercase font-bold text-orange-400">Hindi</span>
                                        <p className="font-medium text-gray-800">{plant.common_names.hi || '-'}</p>
                                    </div>
                                    <div>
                                        <span className="text-xs uppercase font-bold text-orange-400">Tamil</span>
                                        <p className="font-medium text-gray-800">{plant.common_names.ta || '-'}</p>
                                    </div>
                                    <div>
                                        <span className="text-xs uppercase font-bold text-orange-400">Telugu</span>
                                        <p className="font-medium text-gray-800">{plant.common_names.te || '-'}</p>
                                    </div>
                                    <div>
                                        <span className="text-xs uppercase font-bold text-orange-400">Bengali</span>
                                        <p className="font-medium text-gray-800">{plant.common_names.bn || '-'}</p>
                                    </div>
                                </div>
                            </section>

                            {/* Medicinal Properties */}
                            <section>
                                <h2 className="text-2xl font-bold text-primary-800 mb-6 flex items-center gap-2">
                                    <span>💊</span> Medicinal Uses
                                </h2>
                                <div className="space-y-6">
                                    {plant.medicinal_properties.map((prop, idx) => (
                                        <div key={idx} className="bg-primary-50 rounded-xl p-6 border border-primary-100 shadow-sm">
                                            <h3 className="text-xl font-bold text-primary-700 mb-3 border-b border-primary-200 pb-2">
                                                {prop.ailment}
                                            </h3>
                                            <div className="grid md:grid-cols-2 gap-6">
                                                <div>
                                                    <h4 className="font-semibold text-gray-700 text-sm mb-1">Usage</h4>
                                                    <p className="text-gray-600 mb-4">{prop.usage}</p>

                                                    <h4 className="font-semibold text-gray-700 text-sm mb-1">Preparation</h4>
                                                    <p className="text-gray-600">{prop.preparation}</p>
                                                </div>
                                                <div className="bg-white/50 p-4 rounded-lg">
                                                    <h4 className="font-semibold text-gray-700 text-sm mb-1">Dosage</h4>
                                                    <p className="text-gray-600 mb-3">{prop.dosage}</p>

                                                    <h4 className="font-semibold text-red-600 text-xs uppercase mb-1">Precautions</h4>
                                                    <p className="text-red-700 text-sm">{prop.precautions}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        </div>

                        {/* Sidebar */}
                        <div className="space-y-8">
                            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-md sticky top-8">
                                <h3 className="font-bold text-gray-800 mb-4 border-b pb-2">Scientific Classification</h3>
                                <p className="text-sm text-gray-600 leading-relaxed font-mono">
                                    {plant.scientific_classification}
                                </p>

                                <div className="mt-8 pt-6 border-t">
                                    <h4 className="font-bold text-gray-800 mb-2">Disclaimer</h4>
                                    <p className="text-xs text-gray-500 italic">
                                        The information provided here is for educational purposes only.
                                        Please consult a qualified healthcare professional before using any
                                        herbal remedies.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
