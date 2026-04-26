"use client";
// Force deployment sync: 1774266800

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

export const StatsSection = () => {
    const [stats, setStats] = useState({
        species: "46",
        accuracy: "99.6%",
        speed: "< 2s",
        models: "G9 Monolith",
        status: "Live"
    });

    useEffect(() => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"}/api/v1/stats`)
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
        <section className="py-24 bg-[#050505] text-white relative overflow-hidden">
            <div className="absolute inset-0 bg-primary-500/5 pointer-events-none" />

            <div className="container mx-auto px-4 relative z-10">
                <div className="overflow-x-auto pb-4 hide-scrollbar">
                    <div className="flex justify-between items-center min-w-[800px] md:min-w-0 md:grid md:grid-cols-5 gap-8 bg-black/40 p-12 rounded-[48px] border border-white/5 backdrop-blur-2xl">
                        {[
                            { value: stats.species, label: "Monographs" },
                            { value: stats.accuracy, label: "Precision" },
                            { value: stats.speed, label: "Latency" },
                            { value: stats.models, label: "Neural Models" },
                            { value: stats.status, label: "Engine Status" }
                        ].map((stat, idx) => (
                            <motion.div 
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                viewport={{ once: true }}
                                className="text-center px-4"
                            >
                                <div className="text-4xl md:text-5xl font-black text-white mb-2 tracking-tighter">
                                    {stat.value}
                                </div>
                                <div className="text-primary-500 font-black uppercase tracking-[0.4em] text-[8px] whitespace-nowrap opacity-60">
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
