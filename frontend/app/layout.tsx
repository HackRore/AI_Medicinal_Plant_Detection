import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'AI Medicinal Plant Detection',
    description: 'Identify medicinal plants from leaf images using AI',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <nav className="bg-primary-600 text-white shadow-lg">
                    <div className="container mx-auto px-4 py-4">
                        <div className="flex items-center justify-between">
                            <h1 className="text-2xl font-bold">🌿 Medicinal Plant AI</h1>
                            <div className="flex gap-6">
                                <a href="/" className="hover:text-primary-200">Home</a>
                                <a href="/predict" className="hover:text-primary-200">Predict</a>
                                <a href="/plants" className="hover:text-primary-200">Plants</a>
                                <a href="/about" className="hover:text-primary-200">About</a>
                            </div>
                        </div>
                    </div>
                </nav>
                <main className="min-h-screen">
                    {children}
                </main>
                <footer className="bg-gray-800 text-white py-8 mt-16">
                    <div className="container mx-auto px-4 text-center">
                        <p>© 2024 AI Medicinal Plant Detection System</p>
                        <p className="text-sm text-gray-400 mt-2">
                            Made with ❤️ for healthcare accessibility
                        </p>
                    </div>
                </footer>
            </body>
        </html>
    )
}
