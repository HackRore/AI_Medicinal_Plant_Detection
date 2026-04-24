import { HeroSection } from "@/components/home/HeroSection";
import { FeaturesSection } from "@/components/home/FeaturesSection";
import { StatsSection } from "@/components/home/StatsSection";

export default function Home() {
    return (
        <div className="flex flex-col">
            <HeroSection />
            <StatsSection />
            <FeaturesSection />

            {/* CTA Section */}
            <section className="py-32 container mx-auto px-4">
                <div className="glass-card p-16 md:p-24 text-center relative overflow-hidden group">
                    <div className="absolute inset-0 bg-primary-500/5 group-hover:bg-primary-500/10 transition-all duration-700" />
                    
                    <div className="relative z-10 max-w-3xl mx-auto space-y-10">
                        <h2 className="text-5xl md:text-7xl font-black mb-8 leading-[0.9] uppercase tracking-tighter">
                            Enter the <br />
                            <span className="text-primary-500">Neural Boundary</span>
                        </h2>
                        <p className="text-gray-400 text-lg font-medium max-w-xl mx-auto italic">
                            The G9 Forge is synchronized. Access the world's most precise botanical intelligence interface now.
                        </p>
                        <div className="pt-10">
                            <a
                                href="/predict"
                                className="inline-block bg-primary-500 text-black px-16 py-6 rounded-2xl text-xl font-black uppercase tracking-[0.2em] hover:bg-primary-400 hover:scale-105 hover:shadow-[0_0_50px_rgba(16,185,129,0.3)] transition-all active:scale-95"
                            >
                                Launch Monolith
                            </a>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
