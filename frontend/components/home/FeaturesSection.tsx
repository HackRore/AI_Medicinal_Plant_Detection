"use client";
// Force deployment sync: 1774266800

import React from "react";
import { motion } from "framer-motion";
import { Card } from "../ui/Card";

export const FeaturesSection = () => {
    const FEATURES = [
        { 
            title: 'Explainable AI', 
            desc: 'Grad-CAM heatmaps show exactly which leaf features the AI used for identification.', 
            icon: '🔬',
            color: 'bg-blue-50',
            textColor: 'text-blue-700'
        },
        { 
            title: 'Ayurvedic Intelligence', 
            desc: 'Classical dosage, dosha, preparation and compound data from Ayurvedic texts for 81 species.', 
            icon: '🌿',
            color: 'bg-green-50',
            textColor: 'text-green-700'
        },
        { 
            title: 'Dual Verification', 
            desc: 'CNN + Gemini Vision cross-check every identification for maximum accuracy.', 
            icon: '⚡',
            color: 'bg-amber-50',
            textColor: 'text-amber-700'
        },
    ];

    return (
        <section className="py-24 bg-white">
            <div className="container mx-auto px-4">
                <div className="grid md:grid-cols-3 gap-8">
                    {FEATURES.map((feature, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            whileHover={{ y: -10 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <Card className="h-full border-gray-100 shadow-xl bg-white flex flex-col items-start p-10 rounded-[32px] transition-all hover:shadow-2xl hover:border-primary-100">
                                <div className={`w-16 h-16 ${feature.color} rounded-2xl flex items-center justify-center mb-6 text-3xl shadow-sm`}>
                                    {feature.icon}
                                </div>
                                <h3 className={`text-2xl font-black ${feature.textColor} mb-4`}>
                                    {feature.title}
                                </h3>
                                <p className="text-gray-500 font-medium leading-relaxed text-lg">
                                    {feature.desc}
                                </p>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
