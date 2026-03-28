'use client'
import { useEffect, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://plantoai-backend.onrender.com'

export default function PlantsPage() {
    const [plants, setPlants] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [search, setSearch] = useState('')

    useEffect(() => {
        let cancelled = false
        setLoading(true)
        fetch(`${API_URL}/api/v1/plants`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                return res.json()
            })
            .then(data => {
                if (!cancelled) {
                    setPlants(data.plants || data || [])
                    setLoading(false)
                }
            })
            .catch(err => {
                if (!cancelled) {
                    setError('Could not load plants. Please refresh.')
                    setLoading(false)
                    console.error('Plants error:', err)
                }
            })
        return () => { cancelled = true }
    }, [])

    const filtered = plants.filter(p =>
        p.name?.toLowerCase().includes(search.toLowerCase()) ||
        p.medicinal_uses?.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <main style={{ padding: '80px 24px 60px', maxWidth: 1100, margin: '0 auto' }}>
            <h1 style={{ fontSize: 32, fontWeight: 600, marginBottom: 8 }}>
                Medicinal Plants
            </h1>
            <p style={{ color: '#888', marginBottom: 24 }}>
                {loading ? 'Loading...' : `${plants.length} plants in database`}
            </p>

            <input
                type="text"
                placeholder="Search plants or medicinal uses..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{
                    width: '100%', maxWidth: 480, padding: '10px 16px',
                    borderRadius: 8, border: '1px solid #333',
                    background: '#111', color: '#fff', fontSize: 14,
                    marginBottom: 32, outline: 'none'
                }}
            />

            {loading && (
                <p style={{ color: '#7EC89E', fontSize: 16 }}>
                    Loading medicinal plants...
                </p>
            )}

            {error && (
                <p style={{ color: '#D97070', fontSize: 16 }}>{error}</p>
            )}

            {!loading && !error && filtered.length === 0 && (
                <p style={{ color: '#888' }}>No plants found.</p>
            )}

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 16
            }}>
                {filtered.map((plant, i) => (
                    <div key={i} style={{
                        background: '#0f1a10',
                        border: '1px solid rgba(126,200,158,0.15)',
                        borderRadius: 12,
                        padding: '20px',
                        transition: 'border-color 0.2s'
                    }}>
                        <div style={{
                            display: 'flex', justifyContent: 'space-between',
                            alignItems: 'flex-start', marginBottom: 8
                        }}>
                            <h3 style={{ fontSize: 17, fontWeight: 600, color: '#E3EDE4' }}>
                                {plant.name}
                            </h3>
                            <span style={{
                                fontSize: 10, fontWeight: 500,
                                background: 'rgba(126,200,158,0.1)',
                                color: '#7EC89E', padding: '2px 8px',
                                borderRadius: 20, border: '1px solid rgba(126,200,158,0.2)',
                                whiteSpace: 'nowrap'
                            }}>
                                {plant.family || 'Medicinal'}
                            </span>
                        </div>
                        <p style={{
                            fontSize: 12, color: '#7EC89E',
                            fontStyle: 'italic', marginBottom: 8
                        }}>
                            {plant.scientific_name || '—'}
                        </p>
                        {plant.ayurvedic_name && (
                            <p style={{ fontSize: 11, color: '#C8963C', marginBottom: 8 }}>
                                Ayurvedic: {plant.ayurvedic_name}
                            </p>
                        )}
                        <p style={{
                            fontSize: 13, color: 'rgba(227,237,228,0.65)',
                            lineHeight: 1.55
                        }}>
                            {plant.medicinal_uses?.slice(0, 100)}
                            {plant.medicinal_uses?.length > 100 ? '...' : ''}
                        </p>
                    </div>
                ))}
            </div>
        </main>
    )
}