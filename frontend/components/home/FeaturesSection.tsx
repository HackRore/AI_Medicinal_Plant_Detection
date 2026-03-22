"use client";

import React from "react";
import { motion } from "framer-motion";
import { Card } from "../ui/Card";

export const FeaturesSection = () => {
    const STATS = [
        { number: '80', label: 'Medicinal Species', icon: '🌿' },
        { number: 'Dual', label: 'Attention AI Architecture', icon: '🧠' },
        { number: 'Grad-CAM', label: 'Explainable AI', icon: '🔬' },
        { number: '100%', label: 'Toxicity Detection', icon: '⚠️' },
        { number: '5000+', label: 'Ayurvedic Facts', icon: '📚' },
    ];

    return (
        <section className="py-24 bg-gray-50">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-black text-gray-900 mb-4">
                        PlantoAI <span className="text-primary-600">Intelligence</span>
                    </h2>
                    <p className="text-gray-500 max-w-2xl mx-auto">
                        Crowd Outstanding AI Medicinal Plant Detection Pipeline.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-6">
                    {STATS.map((stat, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <Card className="h-full border-transparent shadow-lg bg-white flex flex-col items-center text-center py-8 px-6 hoverEffect">
                                <div className="w-16 h-16 bg-green-50 rounded-2xl flex items-center justify-center mb-4 text-3xl shadow-sm border border-green-100/50">
                                    {stat.icon}
                                </div>
                                <h3 className="text-4xl font-black text-green-700 tracking-tight mb-2">
                                    {stat.number}
                                </h3>
                                <p className="text-gray-600 font-medium leading-snug">
                                    {stat.label}
                                </p>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
