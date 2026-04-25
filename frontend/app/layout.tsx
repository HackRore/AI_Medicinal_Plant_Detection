import type { Metadata, Viewport } from 'next'
import { Inter, Outfit } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import { Providers } from './providers'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' })

export const viewport: Viewport = {
    themeColor: '#166534',
    width: 'device-width',
    initialScale: 1,
}

export const metadata: Metadata = {
    title: {
        default: 'PlantoAI | Neural Botanical Forge',
        template: '%s | PlantoAI'
    },
    description: 'Professional clinical interface for medicinal plant identification and Ayurvedic intelligence.',
    keywords: ['AI', 'Medicinal Plants', 'Botanical AI', 'Ayurveda', 'Neural Forge'],
    authors: [{ name: 'Neural Architects' }],
    manifest: '/manifest.json',
    icons: {
        icon: '/favicon.ico',
        apple: '/icon-192.png',
    },
}

import { BackendWarmup } from '@/components/layout/BackendWarmup'
import { BackgroundEffects } from '@/components/layout/BackgroundEffects'
import DemoBanner from '@/components/layout/DemoBanner'

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning className={`${inter.variable} ${outfit.variable} scroll-smooth`}>
            <body className="font-sans bg-[#050505] text-white antialiased selection:bg-primary-500/30 selection:text-primary-900 overflow-x-hidden">
                <Providers>
                    <BackgroundEffects />
                    <BackendWarmup />
                    <Navbar />
                    <main className="relative z-10">
                        <ErrorBoundary>
                          {children}
                        </ErrorBoundary>
                    </main>
                    <Footer />
                </Providers>
            </body>
        </html>
    )
}

