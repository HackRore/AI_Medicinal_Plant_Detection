'use client'

import React, { useEffect, useState } from 'react'

export default function DemoBanner() {
    const [demoMode, setDemoMode] = useState<boolean | null>(null)

    useEffect(() => {
        const api = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        fetch(`${api}/health`).then(async (res) => {
            try {
                const j = await res.json()
                setDemoMode(Boolean(j?.demo_mode))
            } catch (e) {
                setDemoMode(true)
            }
        }).catch(() => setDemoMode(true))
    }, [])

    if (demoMode === null) return null

    return (
        <div aria-live="polite">
            {demoMode ? (
                <div className="w-full bg-yellow-400 text-yellow-900 text-center py-2 text-sm font-semibold">
                    Running in demo mode — AI model loading or unavailable.
                </div>
            ) : (
                <></>
            )}
        </div>
    )
}
