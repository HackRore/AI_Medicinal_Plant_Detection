export default function AboutPage() {
  return (
    <main className="container mx-auto p-12 max-w-4xl space-y-8 min-h-screen">
      <h1 className="text-5xl font-black text-green-700 mb-6 tracking-tight">Project: PlantoAI</h1>
      <div className="bg-white shadow-2xl rounded-3xl p-10 border border-green-100">
        <h2 className="text-3xl font-bold mb-8 text-gray-900 border-b pb-4">Team: Group G9</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-green-50 p-6 rounded-2xl">
            <h3 className="text-xl font-bold text-green-800 mb-2">Tech Stack</h3>
            <p className="text-green-900 font-medium">Next.js + FastAPI + EfficientNetV2 + Grad-CAM</p>
          </div>

          <div className="bg-emerald-50 p-6 rounded-2xl">
            <h3 className="text-xl font-bold text-emerald-800 mb-2">Dataset</h3>
            <p className="text-emerald-900 font-medium">3 Kaggle datasets — 21,412 images — 226 species</p>
          </div>
        </div>

        <div className="mt-8 bg-gray-50 p-8 rounded-2xl">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">Key Features</h3>
          <ul className="space-y-3 text-gray-700 font-medium">
            <li className="flex items-center gap-3"><span className="text-xl">🔬</span> Real AI detection with Grad-CAM explainability</li>
            <li className="flex items-center gap-3"><span className="text-xl">⚠️</span> Toxicity warning system</li>
            <li className="flex items-center gap-3"><span className="text-xl">📚</span> Ayurvedic knowledge base</li>
            <li className="flex items-center gap-3"><span className="text-xl">🛡️</span> Quality gating</li>
            <li className="flex items-center gap-3"><span className="text-xl">📱</span> PWA mobile support</li>
          </ul>
        </div>
      </div>
    </main>
  )
}
