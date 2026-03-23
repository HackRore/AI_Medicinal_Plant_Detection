import type { Metadata, Viewport } from 'next'
import { Inter, Outfit } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'
import DemoBanner from '@/components/layout/DemoBanner'
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
        default: 'AI Medicinal Plant Detection | Group G9',
        template: '%s | Medicinal Plant AI'
    },
    description: 'Advanced deep learning system for high-accuracy botanical identification and medicinal insight extraction.',
    keywords: ['AI', 'Medicinal Plants', 'Leaf Recognition', 'MobileNetV2', 'Vision Transformer', 'Ayurveda', 'Botanical AI'],
    authors: [{ name: 'Group G9' }],
    manifest: '/manifest.json',
    icons: {
        icon: '/favicon.ico',
        apple: '/icon-192.png',
    },
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning className={`${inter.variable} ${outfit.variable} scroll-smooth`}>
            <body className="font-sans bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 antialiased selection:bg-primary-500/30 selection:text-primary-900">
                <Providers>
                    <Navbar />
    <main>
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

