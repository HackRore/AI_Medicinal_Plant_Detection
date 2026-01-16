"use client";

import React from "react";
import { motion } from "framer-motion";

export const StatsSection = () => {
    return (
        <section className="py-24 bg-gray-900 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-1/2 h-full bg-primary-900/10 skew-x-12 translate-x-1/4" />

            <div className="container mx-auto px-4 relative z-10">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
                    {[
                        { value: "40+", label: "Medicinal Species" },
                        { value: "92.5%", label: "Accuracy" },
                        { value: "< 2s", label: "Inference Time" },
                        { value: "24/7", label: "Availability" }
                    ].map((stat, idx) => (
                        <div key={idx}>
                            <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-400 mb-2">
                                {stat.value}
                            </div>
                            <div className="text-primary-400 font-bold uppercase tracking-widest text-xs">
                                {stat.label}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
