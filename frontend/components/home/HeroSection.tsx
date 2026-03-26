"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "../ui/Button";

export const HeroSection = () => {
    return (
        <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-white">
            {/* Background Ambience */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary-100/40 rounded-full blur-[100px] translate-x-1/2 -translate-y-1/2 animate-float" />
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-secondary-100/40 rounded-full blur-[100px] -translate-x-1/2 translate-y-1/2 animate-float" style={{ animationDelay: "2s" }} />
            </div>

            <div className="container mx-auto px-4 z-10 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="mb-6 inline-block"
                >
                    <span className="px-4 py-2 rounded-full bg-primary-900 text-white text-[10px] font-mono tracking-[0.3em] uppercase border border-white/10 shadow-2xl">
                        Powered by EfficientNetV2 + Gemini Vision
                    </span>
                </motion.div>

                <div className="max-w-5xl mx-auto">
                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
                        className="text-5xl md:text-8xl font-black text-gray-900 mb-8 tracking-tight leading-[0.95]"
                    >
                        The World's First <br />
                        <span className="text-gradient-primary italic">Explainable Ayurvedic</span> <br />
                        Plant Intelligence System
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
                        className="text-xl md:text-2xl text-gray-500 max-w-3xl mx-auto mb-12 leading-relaxed font-medium"
                    >
                        Upload any medicinal plant photo. Get instant AI identification, Grad-CAM explainability, and a complete Ayurvedic clinical profile — in under 2 seconds.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.5, ease: "easeOut" }}
                        className="flex flex-col sm:flex-row gap-6 justify-center items-center"
                    >
                        <Link href="/predict">
                            <Button size="lg" className="text-xl px-12 py-8 rounded-2xl shadow-2xl shadow-primary-500/30 hover:shadow-primary-500/50 hover:scale-105 transition-all bg-primary-900 hover:bg-black">
                                Try Neural Scanner →
                            </Button>
                        </Link>
                        <Link href="/symptom-search">
                            <Button variant="outline" size="lg" className="text-xl px-12 py-8 rounded-2xl border-2 hover:bg-primary-50 transition-all">
                                Search by Symptoms
                            </Button>
                        </Link>
                    </motion.div>
                </div>

                {/* Scroll Indicator */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.5, duration: 1 }}
                    className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
                >
                    <span className="text-xs font-bold text-gray-300 uppercase tracking-widest">Scroll</span>
                    <div className="w-[1px] h-12 bg-gradient-to-b from-gray-300 to-transparent" />
                </motion.div>
            </div>
        </section>
    );
};
