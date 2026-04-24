'use client'

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import { 
  Search, 
  Leaf, 
  AlertCircle, 
  BookOpen, 
  Stethoscope, 
  MessageSquare,
  ArrowRight,
  ShieldAlert,
  Info
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"

const THINKING_STEPS = [
  { icon: "🧠", text: "Executing Multi-Path Symptom Synthesis..." },
  { icon: "📚", text: "Cross-referencing Ayurvedic Classical Taxonomies..." },
  { icon: "🌿", text: "Filtering Bio-Active Botanical Matches..." },
  { icon: "⚖️", text: "Verifying Pharmacological Safety Profiles..." },
  { icon: "📝", text: "Compiling Clinical Recommendation Matrix..." },
]

function AIThinkingOverlay({ isVisible }: { isVisible: boolean }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  useState(() => {
    if (!isVisible) return
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < THINKING_STEPS.length - 1) {
          setCompletedSteps(c => [...c, prev])
          return prev + 1
        }
        return prev
      })
    }, 1500)
    return () => clearInterval(interval)
  })

  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-2xl mx-auto mt-12 p-8 rounded-3xl border border-emerald-500/20 bg-black/40 backdrop-blur-xl shadow-2xl"
    >
      <div className="flex items-center gap-3 mb-8">
        <div className="relative">
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping absolute inset-0" />
          <div className="w-3 h-3 rounded-full bg-emerald-500 relative" />
        </div>
        <span className="text-emerald-400 text-sm font-mono font-bold tracking-widest uppercase">
          PlantoAI Intelligence Monolith
        </span>
      </div>
      
      <div className="space-y-4">
        {THINKING_STEPS.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ 
              opacity: i <= currentStep ? 1 : 0.1, 
              x: 0,
              filter: i < currentStep ? 'grayscale(1)' : 'none'
            }}
            className="flex items-center gap-4 py-1"
          >
            <span className="text-2xl w-8 h-8 flex items-center justify-center bg-white/5 rounded-lg">
              {step.icon}
            </span>
            <span className={`text-base font-medium flex-1 ${
              i === currentStep ? 'text-emerald-300' :
              completedSteps.includes(i) ? 'text-gray-500' : 'text-gray-700'
            }`}>
              {step.text}
            </span>
            {completedSteps.includes(i) && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-emerald-500">
                <Leaf className="w-4 h-4 fill-current" />
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
      
      <div className="mt-8 relative h-2 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-emerald-600 to-teal-400"
          animate={{ width: `${((currentStep + 1) / THINKING_STEPS.length) * 100}%` }}
        />
      </div>
    </motion.div>
  )
}

export default function SymptomSearchPage() {
  const [symptoms, setSymptoms] = useState("")
  const [results, setResults] = useState<any>(null)

  const searchMutation = useMutation({
    mutationFn: async (text: string) => {
      const res = await fetch(`${API_BASE}/api/v1/symptom-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms: text })
      })
      if (!res.ok) throw new Error("AI Diagnostic failed")
      return res.json()
    },
    onSuccess: (data) => {
      if (data.error) {
        toast.error(data.error)
      } else {
        setResults(data)
        toast.success("Ayurvedic analysis complete")
        window.scrollTo({ top: 600, behavior: 'smooth' })
      }
    },
    onError: (err: any) => {
      toast.error(err.message || "Service unavailable")
    }
  })

  return (
    <div className="min-h-screen bg-[#05080a] text-white pt-24 pb-20">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-emerald-900/40 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] bg-teal-900/30 rounded-full blur-[100px]" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Hero Section */}
        <div className="max-w-3xl mx-auto text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-widest mb-6"
          >
            <Stethoscope className="w-3 h-3" />
            AI Symptom Analysis
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-black mb-6 bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent"
          >
            Describe your symptoms. <br />
            <span className="text-emerald-500">Expert Clinical Guidance.</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-gray-400 text-lg"
          >
            Our AI physician analyzes your condition against ancient classical texts to recommend the most effective medicinal plants.
          </motion.p>
        </div>

        {/* Search Box */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="max-w-2xl mx-auto"
        >
          <Card className="bg-white/5 border-white/10 backdrop-blur-sm overflow-hidden">
            <CardContent className="p-6">
              <div className="relative">
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Describe how you feel... (e.g., I have fever, body aches and low energy for 3 days...)"
                  className="w-full h-40 bg-black/40 border border-white/10 rounded-2xl p-4 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500/50 transition-all resize-none mb-4"
                />
                <div className="absolute bottom-6 right-4 text-xs text-gray-500 font-mono">
                  {symptoms.length} chars
                </div>
              </div>
              <Button
                onClick={() => searchMutation.mutate(symptoms)}
                disabled={searchMutation.isPending || symptoms.length < 5}
                className="w-full h-14 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl gap-2 shadow-lg shadow-emerald-900/20 transition-all active:scale-[0.98]"
              >
                {searchMutation.isPending ? "Analyzing Conditions..." : "Find Ayurvedic Remedy"}
                <ArrowRight className="w-5 h-5" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence>
          {searchMutation.isPending && (
            <AIThinkingOverlay isVisible={true} />
          )}
        </AnimatePresence>

        {/* Results */}
        {results && !searchMutation.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-20 space-y-12"
          >
            <div className="text-center mb-10">
              <h2 className="text-2xl font-bold text-emerald-400 mb-2">Recommended Remedies</h2>
              <div className="h-1 w-20 bg-emerald-500 mx-auto rounded-full" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {results.recommendations?.map((item: any, idx: number) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Card className="h-full bg-white/5 border-white/10 hover:border-emerald-500/30 transition-all group overflow-hidden">
                    <div className="h-1 bg-emerald-500 w-0 group-hover:w-full transition-all duration-500" />
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start mb-2">
                        <div className="p-2 bg-emerald-500/20 rounded-lg text-emerald-400">
                          <Leaf className="w-5 h-5" />
                        </div>
                        <span className="text-[10px] font-mono text-emerald-500/60 uppercase tracking-widest bg-emerald-500/5 px-2 py-1 rounded">
                          Recommendation #{item.rank || idx + 1}
                        </span>
                      </div>
                      <CardTitle className="text-xl text-white group-hover:text-emerald-400 transition-colors">
                        {item.plant}
                      </CardTitle>
                      <CardDescription className="text-emerald-500/70 font-medium italic">
                        {item.scientific_name} • {item.ayurvedic_name}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-1 font-bold">Why it helps</p>
                        <p className="text-sm text-gray-300 leading-relaxed">{item.why}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 pt-2">
                        <div className="p-3 bg-black/40 rounded-xl border border-white/5">
                          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Dosha Effect</p>
                          <p className="text-xs text-emerald-400">{item.dosha_effect}</p>
                        </div>
                        <div className="p-3 bg-black/40 rounded-xl border border-white/5">
                          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Safety</p>
                          <p className="text-xs text-orange-400">{item.safety}</p>
                        </div>
                      </div>

                      <div className="space-y-3 pt-2">
                        <div className="flex gap-2">
                          <div className="text-emerald-500 mt-0.5"><BookOpen className="w-3 h-3" /></div>
                          <div>
                            <p className="text-[10px] text-gray-500 uppercase font-bold">Preparation</p>
                            <p className="text-xs text-gray-400">{item.preparation}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <div className="text-emerald-500 mt-0.5"><Info className="w-3 h-3" /></div>
                          <div>
                            <p className="text-[10px] text-gray-500 uppercase font-bold">Recommended Dosage</p>
                            <p className="text-xs text-gray-400">{item.dosage}</p>
                          </div>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-white/10 mt-4">
                        <div className="flex items-center gap-2 text-gray-600">
                          <MessageSquare className="w-3 h-3" />
                          <span className="text-[10px] font-mono italic">{item.classical_reference}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Lifestyle & Diet Advice */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="max-w-4xl mx-auto"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-emerald-950/20 border-emerald-500/20 backdrop-blur-sm">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2 text-emerald-400">
                      <Sun className="w-5 h-5" /> Lifestyle Advice
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-300 text-sm leading-relaxed">{results.lifestyle_advice}</p>
                  </CardContent>
                </Card>
                <Card className="bg-teal-950/20 border-teal-500/20 backdrop-blur-sm">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2 text-teal-400">
                      <Moon className="w-5 h-5" /> Dietary Recommendation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-300 text-sm leading-relaxed">{results.diet_tip}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Warning */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-8 p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 flex gap-3"
              >
                <ShieldAlert className="w-6 h-6 text-orange-500 shrink-0" />
                <div>
                  <p className="text-orange-500 text-xs font-bold uppercase tracking-wider mb-1">Medical Disclaimer</p>
                  <p className="text-gray-400 text-xs leading-relaxed">{results.warning}</p>
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

function Sun(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </svg>
  )
}

function Moon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </svg>
  )
}
   
 