export default function Home() {
    return (
        <div className="container mx-auto px-4 py-16 space-y-32">
            {/* Hero Section */}
            <section className="text-center relative py-20 animate-fade-in overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-primary-100/50 rounded-full blur-3xl -z-10 animate-pulse-slow"></div>
                <h1 className="text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary-700 via-primary-600 to-green-600 mb-6 py-2">
                    AI-Based Medicinal Plant Detection
                </h1>
                <p className="text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                    Bridging traditional botanical knowledge with state-of-the-art Deep Learning
                    for healthcare accessibility.
                </p>
                <div className="flex gap-6 justify-center">
                    <a
                        href="/predict"
                        className="bg-primary-600 text-white px-10 py-4 rounded-full text-lg font-bold hover:bg-primary-700 transform hover:scale-105 transition-all shadow-xl shadow-primary-200"
                    >
                        Scan Leaf Now →
                    </a>
                    <a
                        href="/plants"
                        className="bg-white text-primary-600 px-10 py-4 rounded-full text-lg font-bold border-2 border-primary-100 hover:border-primary-600 transform hover:scale-105 transition-all shadow-md"
                    >
                        Encyclopedia
                    </a>
                </div>
            </section>

            {/* Project Stages Timeline */}
            <section className="animate-slide-up">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-black text-gray-800 mb-4">Project Milestones</h2>
                    <p className="text-gray-600">The journey from conceptualization to full-stack deployment</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    {[
                        { step: "01", title: "Backend Engine", desc: "FastAPI Core & DB", icon: "⚙️" },
                        { step: "02", title: "ML Pipeline", desc: "Model Training", icon: "🧠" },
                        { step: "03", title: "Web Dashboard", desc: "Desktop Access", icon: "🌐" },
                        { step: "04", title: "Mobile App", desc: "Native Scanning", icon: "📱" },
                        { step: "05", title: "Optimization", desc: "ViT + 92.5% Acc", icon: "🚀" }
                    ].map((item, i) => (
                        <div key={i} className="glass-panel p-6 rounded-2xl relative group hover:-translate-y-2 transition-all">
                            <div className="text-3xl mb-4 group-hover:scale-125 transition-transform">{item.icon}</div>
                            <div className="text-xs font-black text-primary-500 mb-1">STAGE {item.step}</div>
                            <h4 className="font-bold text-gray-800 mb-2">{item.title}</h4>
                            <p className="text-sm text-gray-500">{item.desc}</p>
                            {i < 4 && <div className="hidden md:block absolute top-1/2 -right-4 translate-x-1/2 text-gray-200">→</div>}
                        </div>
                    ))}
                </div>
            </section>

            {/* Model Intelligence & Stats */}
            <section className="bg-slate-900 rounded-[3rem] p-12 text-white relative overflow-hidden animate-slide-up shadow-2xl">
                <div className="absolute top-0 right-0 w-96 h-96 bg-primary-600/20 rounded-full blur-[100px]"></div>
                <div className="grid md:grid-cols-2 gap-16 items-center">
                    <div>
                        <h2 className="text-4xl font-bold mb-8">Model Intelligence</h2>
                        <div className="space-y-6">
                            <div className="flex items-center gap-4 group">
                                <div className="w-16 h-16 bg-primary-600/20 rounded-2xl flex items-center justify-center text-2xl group-hover:bg-primary-600 transition-colors">🎯</div>
                                <div>
                                    <div className="text-3xl font-black text-primary-400">92.5%</div>
                                    <p className="text-gray-400">Validation Accuracy</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4 group">
                                <div className="w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center text-2xl group-hover:bg-blue-600 transition-colors">⚡</div>
                                <div>
                                    <div className="text-3xl font-black text-blue-400">&lt; 1.8s</div>
                                    <p className="text-gray-400">Average Inference Time</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4 group">
                                <div className="w-16 h-16 bg-orange-600/20 rounded-2xl flex items-center justify-center text-2xl group-hover:bg-orange-600 transition-colors">✨</div>
                                <div>
                                    <div className="text-3xl font-black text-orange-400">Dual-Model</div>
                                    <p className="text-gray-400">MobileNetV2 + ViT Ensemble</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="glass-panel border-white/10 p-8 rounded-3xl">
                        <h4 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <span className="w-3 h-3 bg-primary-500 rounded-full animate-pulse"></span>
                            Live Performance Metrics
                        </h4>
                        <div className="space-y-4">
                            <div className="space-y-1">
                                <div className="flex justify-between text-sm"><span className="text-gray-400">Precision</span><span>91.8%</span></div>
                                <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
                                    <div className="bg-primary-500 h-full w-[91.8%]"></div>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <div className="flex justify-between text-sm"><span className="text-gray-400">Recall</span><span>90.2%</span></div>
                                <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
                                    <div className="bg-blue-500 h-full w-[90.2%]"></div>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <div className="flex justify-between text-sm"><span className="text-gray-400">Confidence</span><span>95.5%</span></div>
                                <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
                                    <div className="bg-orange-500 h-full w-[95.5%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Team & Guidance */}
            <section className="animate-slide-up pb-20">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-black text-gray-800 mb-4">Project Group G14</h2>
                    <p className="text-gray-600 italic">Department of Artificial Intelligence & Data Science</p>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    {[
                        { name: "Madhura Wankhade", role: "Team Lead", id: "24167" },
                        { name: "Ravindra Ahire", role: "Full Stack Dev", id: "24101" },
                        { name: "Samruddhi Gholap", role: "ML Researcher", id: "24116" },
                        { name: "Pranali Ghugarkar", role: "UI/UX Designer", id: "24117" }
                    ].map((member, i) => (
                        <div key={i} className="text-center p-6 rounded-2xl border border-gray-100 hover:bg-primary-50 transition-colors">
                            <div className="w-20 h-20 bg-primary-100 rounded-full mx-auto mb-4 flex items-center justify-center text-2xl font-bold text-primary-700">
                                {member.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <h4 className="font-bold text-gray-900">{member.name}</h4>
                            <p className="text-xs text-primary-600 font-bold mb-2 uppercase">{member.role}</p>
                            <p className="text-xs text-gray-400">ID: {member.id}</p>
                        </div>
                    ))}
                </div>
                <div className="mt-12 text-center p-8 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                    <p className="text-gray-500 text-sm mb-2 uppercase tracking-widest font-bold">Under the Guidance of</p>
                    <h3 className="text-2xl font-bold text-gray-800">Ms. Sneha Bankar</h3>
                    <p className="text-gray-600">Dr. D. Y. Patil College of Engineering & Innovation</p>
                </div>
            </section>
        </div>
    )
}
