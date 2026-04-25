"use client";
// Force deployment sync: 1774266800

import React from "react";
import { motion } from "framer-motion";
import { Microscope, Leaf, Zap, BrainCircuit } from "lucide-react";

export const FeaturesSection = () => {
    const FEATURES = [
        { 
            title: 'Neural Explainability', 
            desc: 'Grad-CAM heatmaps show exactly which leaf features the AI used for identification.', 
            icon: <Microscope className="w-8 h-8" />,
        },
        { 
            title: 'Clinical Monographs', 
            desc: 'Classical dosage, preparation and compound data from Ayurvedic texts for 81 species.', 
            icon: <Leaf className="w-8 h-8" />,
        },
        { 
            title: 'Dual-Path Analysis', 
            desc: 'CNN + Gemini Vision cross-check every identification for maximum accuracy.', 
            icon: <Zap className="w-8 h-8" />,
        },
        { 
            title: 'Symptom Synthesis', 
            desc: 'Multi-path AI reasoning identifies botanical remedies based on described symptoms.', 
            icon: <BrainCircuit className="w-8 h-8" />,
        },
    ];

    return (
        <section className="py-32 bg-[#050505] relative">
            <div className="container mx-auto px-4">
                <div className="grid md:grid-cols-4 gap-8">
                    {FEATURES.map((feature, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            whileHover={{ y: -10 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <div className="glass-card h-full p-8 flex flex-col items-start hover:border-primary-500/30 transition-all group">
                                <div className="w-16 h-16 bg-primary-500/10 rounded-2xl flex items-center justify-center mb-8 text-primary-500 border border-primary-500/20 group-hover:bg-primary-500 group-hover:text-black transition-all">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xs font-black uppercase tracking-[0.3em] text-primary-400 mb-6">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-400 font-medium leading-relaxed text-lg">
                                    {feature.desc}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
