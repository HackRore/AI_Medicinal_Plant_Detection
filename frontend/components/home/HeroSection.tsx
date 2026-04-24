"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "../ui/Button";

export const HeroSection = () => {
    return (
        <section className="relative min-h-screen flex items-center justify-center pt-20">
            <div className="container mx-auto px-4 grid lg:grid-cols-2 gap-20 items-center">
                <div className="text-left space-y-12">
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 1, ease: "circOut" }}
                    >
                        <span className="px-5 py-2 rounded-full bg-primary-500/10 text-primary-400 text-[9px] font-black tracking-[0.5em] uppercase border border-primary-500/20 shadow-[0_0_40px_rgba(16,185,129,0.15)] inline-flex items-center gap-3">
                            <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-ping" />
                            Active Neural Forge v5.1.0
                        </span>
                    </motion.div>

                    <div className="space-y-8">
                        <motion.h1
                            initial={{ opacity: 0, y: 40 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1, delay: 0.2, ease: "circOut" }}
                            className="text-7xl md:text-[10rem] font-black text-white mb-8 tracking-tighter leading-[0.85] uppercase text-glow-white"
                        >
                            Neural <br />
                            <span className="text-primary-500 text-glow">Botanical</span> <br />
                            Forge
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1, delay: 0.4, ease: "circOut" }}
                            className="text-xl text-gray-500 max-w-xl leading-relaxed font-medium italic"
                        >
                            The boundary between ancient Ayurveda and high-fidelity neural computation. Curated by clinical intelligence.
                        </motion.p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 0.6, ease: "circOut" }}
                        className="flex flex-col sm:flex-row gap-8 items-start"
                    >
                        <Link href="/predict">
                            <Button size="lg" className="h-20 text-xl px-16 rounded-2xl bg-primary-500 text-black font-black uppercase tracking-[0.2em] hover:bg-primary-400 transition-all shadow-[0_0_60px_rgba(16,185,129,0.2)] active:scale-95 glass-reflection">
                                Launch HUD
                            </Button>
                        </Link>
                        <Link href="/symptom-search">
                            <Button variant="outline" size="lg" className="h-20 text-xl px-16 rounded-2xl border-white/10 text-white font-black uppercase tracking-[0.2em] hover:bg-white/5 transition-all backdrop-blur-xl">
                                Clinical Search
                            </Button>
                        </Link>
                    </motion.div>
                </div>

                {/* Tactical Visual Hero */}
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9, rotate: 3 }}
                    animate={{ opacity: 1, scale: 1, rotate: 0 }}
                    transition={{ duration: 1.5, ease: "circOut" }}
                    className="relative hidden lg:block"
                >
                    <div className="absolute -inset-10 bg-primary-500/10 rounded-[80px] blur-[100px] animate-pulse" />
                    <div className="glass-card p-6 relative overflow-hidden group rounded-[60px]">
                        <div className="scanline opacity-20" />
                        <img 
                            src="https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2670&auto=format&fit=crop" 
                            alt="Neural Forge HUD" 
                            className="w-full rounded-[40px] grayscale contrast-125 opacity-70 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-1000 scale-105 group-hover:scale-100"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent opacity-80" />
                        
                        <div className="absolute bottom-12 left-12 right-12 space-y-6">
                            <div className="p-8 bg-black/60 backdrop-blur-2xl border border-white/10 rounded-[40px] shadow-2xl">
                                <div className="flex items-center justify-between mb-6">
                                    <span className="text-[10px] font-black text-primary-400 uppercase tracking-[0.5em]">Neural Link: 88.4ms</span>
                                    <div className="flex gap-1">
                                        {[...Array(4)].map((_, i) => (
                                            <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                                        ))}
                                    </div>
                                </div>
                                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                    <motion.div 
                                        className="h-full bg-primary-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]"
                                        animate={{ width: ["10%", "100%"] }}
                                        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 1 }}
                className="absolute bottom-10 left-10 flex items-center gap-4"
            >
                <div className="w-12 h-[1px] bg-primary-500/30" />
                <span className="text-[10px] font-black text-gray-500 uppercase tracking-[0.5em]">Forge Manual</span>
            </motion.div>
        </section>
    );
};
