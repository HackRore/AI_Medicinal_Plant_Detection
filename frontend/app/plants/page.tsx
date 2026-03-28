'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Plant {
    id: number
    name?: string
    species_name: string
    scientific_name?: string
    common_name?: string
    description: string
    medicinal_uses?: string
    image_url: string
}

export default function PlantsPage() {
    const [plants, setPlants] = useState<Plant[]>([])
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://plantoai-backend.onrender.com'

    useEffect(() => {
        setLoading(true)
        fetch(`${API_URL}/api/v1/plants`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                return res.json()
            })
            .then(data => {
                // Step 8: Fix setter
                setPlants(data.plants || data || [])
                setLoading(false)
            })
            .catch(err => {
                console.error('Plants fetch error:', err)
                setError('Could not load plants. Please refresh.')
                setLoading(false)
            })
    }, [])

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        fetch(`${API_URL}/api/v1/plants?search=${encodeURIComponent(search)}`)
            .then(res => res.json())
            .then(data => {
                setPlants(data.plants || data || [])
                setLoading(false)
            })
            .catch(() => {
                setError('Search failed')
                setLoading(false)
            })
    }

    // Show loading state
    if (loading) return (
        <div style={{ textAlign: 'center', padding: '100px 20px', color: '#7EC89E', fontSize: '1.2rem', fontFamily: 'sans-serif' }}>
            <div className="animate-pulse">Loading medicinal plants...</div>
        </div>
    )

    // Show error state
    if (error) return (
        <div style={{ textAlign: 'center', padding: '100px 20px', color: '#D97070', fontSize: '1.2rem', fontFamily: 'sans-serif' }}>
            {error}
            <br />
            <button 
                onClick={() => window.location.reload()}
                style={{ marginTop: '20px', padding: '10px 20px', borderRadius: '8px', background: '#D97070', color: 'white', border: 'none', cursor: 'pointer' }}
            >
                Retry
            </button>
        </div>
    )

    return (
        <div className="container mx-auto px-4 py-12" style={{ fontFamily: 'sans-serif' }}>
            <div className="flex flex-col md:flex-row justify-between items-center mb-12">
                <h1 className="text-4xl font-bold text-gray-800 mb-6 md:mb-0">
                    Medicinal Plants
                </h1>

                {/* Search Bar */}
                <form onSubmit={handleSearch} className="flex w-full md:w-auto gap-2">
                    <input
                        type="text"
                        placeholder="Search plants..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full md:w-80 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                    />
                    <button
                        type="submit"
                        className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                    >
                        Search
                    </button>
                </form>
            </div>

            {plants.length === 0 ? (
                <div className="text-center py-20 text-gray-500">
                    <p className="text-xl">No plants found matching your criteria.</p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {plants.map((plant) => (
                        <Link href={`/plants/${plant.id}`} key={plant.id} className="group">
                            <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 h-full flex flex-col border border-gray-100">
                                <div className="relative h-56 overflow-hidden bg-gray-100">
                                    <img
                                        src={plant.image_url || 'https://via.placeholder.com/400x300?text=No+Image'}
                                        alt={plant.species_name}
                                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                    />
                                </div>
                                <div className="p-6 flex-1 flex flex-col">
                                    <h2 className="text-2xl font-bold text-gray-800 mb-2 group-hover:text-green-600 transition-colors">
                                        {plant.name || plant.common_name || plant.species_name?.replace(/_/g, ' ')}
                                    </h2>
                                    <p className="text-sm font-mono text-green-600 mb-4">
                                        {plant.scientific_name || plant.species_name?.replace(/_/g, ' ')}
                                    </p>
                                    <p className="text-gray-600 line-clamp-3 mb-4 flex-1">
                                        {plant.description || plant.medicinal_uses}
                                    </p>
                                    <div className="text-green-600 font-semibold flex items-center group-hover:translate-x-2 transition-transform">
                                        Learn More →
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
