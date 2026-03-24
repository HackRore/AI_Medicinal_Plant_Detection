"use client"

import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 min
    },
  },
})

export function Providers({ children }: { children: React.ReactNode }) {
  // Proactive Backend Warm-up (Render Cold Start Mitigation)
  React.useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"
    fetch(`${API_BASE}/health`).catch(() => console.log("Backend warm-up initiated"))
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster 
        richColors 
        position="top-right" 
        closeButton 
        expand={false}
      />
    </QueryClientProvider>
  )
}

