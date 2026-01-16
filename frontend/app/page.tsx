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
            <section className="py-20 container mx-auto px-4">
                <div className="bg-primary-900 rounded-[50px] p-16 text-center text-white relative overflow-hidden group">
                    <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1542382259-967cbe5f271a?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-30 group-hover:scale-105 transition-transform duration-700"></div>
                    <div className="absolute inset-0 bg-primary-900/80"></div>

                    <div className="relative z-10 max-w-2xl mx-auto">
                        <h2 className="text-4xl xs:text-5xl font-black mb-8 leading-tight">Ready to see the <span className="text-primary-400">future</span> of botany?</h2>
                        <a
                            href="/predict"
                            className="inline-block bg-white text-primary-900 px-12 py-5 rounded-2xl text-xl font-black hover:bg-gray-100 hover:scale-105 hover:shadow-2xl transition-all"
                        >
                            TRY NEURAL SCANNER
                        </a>
                    </div>
                </div>
            </section>
        </div>
    )
}
