"use client";
// Force deployment sync: 1774266800

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

export const StatsSection = () => {
    const [stats, setStats] = useState({
        species: "13",
        accuracy: "96.4%",
        speed: "< 2s",
        models: "5",
        status: "Live"
    });

    useEffect(() => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/stats`)
            .then(r => r.json())
            .then(data => {
                setStats({
                    species: data.species_count ?? "—",
                    accuracy: data.top1_accuracy ? `${data.top1_accuracy}%` : "—",
                    speed: "< 2s",
                    models: "Ensemble-V2",
                    status: "Live"
                });
            })
            .catch(() => {});
    }, []);

    return (
        <section className="py-24 bg-gray-900 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-1/2 h-full bg-primary-900/10 skew-x-12 translate-x-1/4" />

            <div className="container mx-auto px-4 relative z-10">
                <div className="overflow-x-auto pb-4 hide-scrollbar">
                    <div className="flex justify-between items-center min-w-[800px] md:min-w-0 md:grid md:grid-cols-5 gap-8 bg-black/40 p-8 rounded-[32px] border border-white/5 backdrop-blur-xl">
                        {[
                            { value: stats.species, label: "Medicinal Species" },
                            { value: stats.accuracy, label: "System Accuracy" },
                            { value: stats.speed, label: "Inference Speed" },
                            { value: stats.models, label: "AI Neural Models" },
                            { value: stats.status, label: "Build Target" }
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
