'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Plant {
    id: number
    species_name: string
    common_name: string
    description: string
    image_url: string
}

export default function PlantsPage({
    searchParams,
}: {
    searchParams: { q?: string }
}) {
    const [plants, setPlants] = useState<Plant[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState(searchParams.q || '')

    useEffect(() => {
        fetchPlants(search)
    }, [])

    const fetchPlants = async (query = '') => {
        setLoading(true)
        try {
            const url = query
                ? `${process.env.API_URL || 'http://localhost:8000'}/api/v1/plants/search/by-name?q=${query}`
                : `${process.env.API_URL || 'http://localhost:8000'}/api/v1/plants?limit=50`

            const res = await fetch(url)
            const data = await res.json()

            if (query) {
                setPlants(data.results || [])
            } else {
                setPlants(data.plants || [])
            }
        } catch (error) {
            console.error('Failed to fetch plants:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        fetchPlants(search)
    }

    return (
        <div className="container mx-auto px-4 py-12">
            <div className="flex flex-col md:flex-row justify-between items-center mb-12">
                <h1 className="text-4xl font-bold text-primary-800 mb-6 md:mb-0">
                    Medicinal Plants
                </h1>

                {/* Search Bar */}
                <form onSubmit={handleSearch} className="flex w-full md:w-auto gap-2">
                    <input
                        type="text"
                        placeholder="Search plants..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full md:w-80 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                    />
                    <button
                        type="submit"
                        className="bg-primary-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                    >
                        Search
                    </button>
                </form>
            </div>

            {loading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="bg-white rounded-xl shadow-lg h-96 animate-pulse">
                            <div className="h-48 bg-gray-200 rounded-t-xl" />
                            <div className="p-6 space-y-4">
                                <div className="h-6 bg-gray-200 rounded w-3/4" />
                                <div className="h-4 bg-gray-200 rounded w-1/2" />
                                <div className="h-20 bg-gray-200 rounded" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <>
                    {plants.length === 0 ? (
                        <div className="text-center py-20 text-gray-500">
                            <p className="text-xl">No plants found matching your criteria.</p>
                        </div>
                    ) : (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {plants.map((plant) => (
                                <Link href={`/plants/${plant.id}`} key={plant.id} className="group">
                                    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 h-full flex flex-col">
                                        <div className="relative h-56 overflow-hidden bg-gray-100">
                                            <img
                                                src={plant.image_url || '/placeholder-leaf.jpg'}
                                                alt={plant.species_name}
                                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                                onError={(e) => {
                                                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=No+Image'
                                                }}
                                            />
                                        </div>
                                        <div className="p-6 flex-1 flex flex-col">
                                            <h2 className="text-2xl font-bold text-gray-800 mb-2 group-hover:text-primary-600 transition-colors">
                                                {plant.common_name || plant.species_name?.replace(/_/g, ' ')}
                                            </h2>
                                            <p className="text-sm font-mono text-primary-500 mb-4">
                                                {plant.species_name?.replace(/_/g, ' ')}
                                            </p>
                                            <p className="text-gray-600 line-clamp-3 mb-4 flex-1">
                                                {plant.description}
                                            </p>
                                            <div className="text-primary-600 font-semibold flex items-center group-hover:translate-x-2 transition-transform">
                                                Learn More →
                                            </div>
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
