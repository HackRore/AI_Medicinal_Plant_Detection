export default function Home() {
    return (
        <div className="container mx-auto px-4 py-16">
            {/* Hero Section */}
            <section className="text-center mb-20 animate-fade-in">
                <h1 className="text-6xl font-bold text-primary-700 mb-6">
                    AI-Powered Medicinal Plant Detection
                </h1>
                <p className="text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
                    Identify medicinal plants from leaf images using state-of-the-art deep learning
                </p>
                <div className="flex gap-4 justify-center">
                    <a
                        href="/predict"
                        className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transform hover:scale-105 transition-all shadow-lg"
                    >
                        Try It Now →
                    </a>
                    <a
                        href="/plants"
                        className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold border-2 border-primary-600 hover:bg-primary-50 transform hover:scale-105 transition-all"
                    >
                        Browse Plants
                    </a>
                </div>
            </section>

            {/* Features Section */}
            <section className="grid md:grid-cols-3 gap-8 mb-20">
                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">AI-Powered</h3>
                    <p className="text-gray-600">
                        Dual model architecture with MobileNetV2 and Vision Transformer achieving 90%+ accuracy
                    </p>
                </div>

                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up" style={{ animationDelay: '0.1s' }}>
                    <div className="text-4xl mb-4">🔍</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Explainable AI</h3>
                    <p className="text-gray-600">
                        Grad-CAM and LIME visualizations show exactly what the AI focuses on
                    </p>
                </div>

                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up" style={{ animationDelay: '0.2s' }}>
                    <div className="text-4xl mb-4">🌐</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Multi-Language</h3>
                    <p className="text-gray-600">
                        Support for Hindi, Tamil, Telugu, Bengali with AI-powered descriptions
                    </p>
                </div>

                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up" style={{ animationDelay: '0.3s' }}>
                    <div className="text-4xl mb-4">📚</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Rich Database</h3>
                    <p className="text-gray-600">
                        Comprehensive information on 40+ Indian medicinal plants with traditional uses
                    </p>
                </div>

                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up" style={{ animationDelay: '0.4s' }}>
                    <div className="text-4xl mb-4">🎯</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Smart Recommendations</h3>
                    <p className="text-gray-600">
                        Get plant suggestions based on medicinal properties and ailments
                    </p>
                </div>

                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow animate-slide-up" style={{ animationDelay: '0.5s' }}>
                    <div className="text-4xl mb-4">📱</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Multi-Platform</h3>
                    <p className="text-gray-600">
                        Available as web app, mobile app (iOS/Android), and REST API
                    </p>
                </div>
            </section>

            {/* How It Works */}
            <section className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-2xl p-12 mb-20">
                <h2 className="text-4xl font-bold text-center text-primary-800 mb-12">
                    How It Works
                </h2>
                <div className="grid md:grid-cols-4 gap-6">
                    <div className="text-center">
                        <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-primary-600">
                            1
                        </div>
                        <h4 className="font-bold text-lg mb-2">Upload Image</h4>
                        <p className="text-gray-700">Take or upload a clear photo of the leaf</p>
                    </div>
                    <div className="text-center">
                        <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-primary-600">
                            2
                        </div>
                        <h4 className="font-bold text-lg mb-2">AI Analysis</h4>
                        <p className="text-gray-700">Our models analyze the leaf characteristics</p>
                    </div>
                    <div className="text-center">
                        <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-primary-600">
                            3
                        </div>
                        <h4 className="font-bold text-lg mb-2">Get Results</h4>
                        <p className="text-gray-700">Receive plant identification with confidence score</p>
                    </div>
                    <div className="text-center">
                        <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-primary-600">
                            4
                        </div>
                        <h4 className="font-bold text-lg mb-2">Learn More</h4>
                        <p className="text-gray-700">Explore medicinal properties and uses</p>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="grid md:grid-cols-3 gap-8 text-center mb-20">
                <div>
                    <div className="text-5xl font-bold text-primary-600 mb-2">92.5%</div>
                    <div className="text-gray-600">Model Accuracy</div>
                </div>
                <div>
                    <div className="text-5xl font-bold text-primary-600 mb-2">40+</div>
                    <div className="text-gray-600">Plant Species</div>
                </div>
                <div>
                    <div className="text-5xl font-bold text-primary-600 mb-2">&lt;2s</div>
                    <div className="text-gray-600">Response Time</div>
                </div>
            </section>

            {/* CTA */}
            <section className="text-center bg-primary-600 text-white rounded-2xl p-12">
                <h2 className="text-4xl font-bold mb-4">Ready to Identify Plants?</h2>
                <p className="text-xl mb-8 opacity-90">
                    Start using our AI-powered plant detection system now
                </p>
                <a
                    href="/predict"
                    className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transform hover:scale-105 transition-all inline-block"
                >
                    Get Started →
                </a>
            </section>
        </div>
    )
}
