"use client";

import React from "react";
import { motion } from "framer-motion";
import { Card } from "../ui/Card";
import { Scan, Database, Brain, Sparkles } from "lucide-react";

export const FeaturesSection = () => {
    const features = [
        {
            icon: <Scan className="w-8 h-8 text-primary-600" />,
            title: "Instant Identification",
            desc: "Upload a leaf photo and get results in under 2 seconds with 92% accuracy."
        },
        {
            icon: <Brain className="w-8 h-8 text-secondary-600" />,
            title: "Hybrid AI Engine",
            desc: "Powered by an ensemble of MobileNetV2 and Vision Transformers (ViT)."
        },
        {
            icon: <Database className="w-8 h-8 text-primary-600" />,
            title: "Rich Botanical DB",
            desc: "Detailed medicinal properties, chemical composition, and usage guides."
        },
        {
            icon: <Sparkles className="w-8 h-8 text-secondary-600" />,
            title: "Smart Insights",
            desc: "Get automated suggestions and look-alike warnings powered by Gemini AI."
        }
    ];

    return (
        <section className="py-24 bg-gray-50">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-black text-gray-900 mb-4">Why MedicinalPlant<span className="text-primary-600">AI</span>?</h2>
                    <p className="text-gray-500 max-w-2xl mx-auto">
                        Bridging the gap between ancient Ayurvedic knowledge and modern Deep Learning technology.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <Card className="h-full border-transparent shadow-lg bg-white">
                                <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center mb-6">
                                    {feature.icon}
                                    ]</div>
                                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                                <p className="text-gray-500 text-sm leading-relaxed">{feature.desc}</p>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
