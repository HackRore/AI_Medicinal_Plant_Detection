"use client";
// Force deployment sync: 1774266800

import React from "react";
import { motion } from "framer-motion";

export const StatsSection = () => {
    return (
        <section className="py-24 bg-gray-900 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-1/2 h-full bg-primary-900/10 skew-x-12 translate-x-1/4" />

            <div className="container mx-auto px-4 relative z-10">
                <div className="overflow-x-auto pb-4 hide-scrollbar">
                    <div className="flex justify-between items-center min-w-[800px] md:min-w-0 md:grid md:grid-cols-5 gap-8 bg-black/40 p-8 rounded-[32px] border border-white/5 backdrop-blur-xl">
                        {[
                            { value: "81", label: "Medicinal Species" },
                            { value: "92.5%", label: "System Accuracy" },
                            { value: "< 2s", label: "Inference Speed" },
                            { value: "5", label: "AI Neural Models" },
                            { value: "Free", label: "Forever Open-Source" }
                        ].map((stat, idx) => (
                            <motion.div 
                                key={idx}
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                transition={{ delay: idx * 0.1 }}
                                viewport={{ once: true }}
                                className="text-center px-4"
                            >
                                <div className="text-3xl md:text-5xl font-black text-white mb-2 tracking-tighter">
                                    {stat.value}
                                </div>
                                <div className="text-primary-400 font-mono uppercase tracking-[0.2em] text-[10px] whitespace-nowrap">
                                    {stat.label}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};
