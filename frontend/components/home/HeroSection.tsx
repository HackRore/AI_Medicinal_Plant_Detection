"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "../ui/Button";
import { Activity, ShieldCheck, Database, Fingerprint } from "lucide-react";

export const HeroSection = () => {
    const { scrollY } = useScroll();
    const y1 = useTransform(scrollY, [0, 1000], [0, -150]);
    const y2 = useTransform(scrollY, [0, 1000], [0, 150]);
    const opacity = useTransform(scrollY, [0, 500], [1, 0]);

    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({
                x: e.clientX,
                y: e.clientY,
            });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    return (
        <section className="relative min-h-[110vh] flex items-center justify-center overflow-hidden bg-[#020202]">
            {/* Cinematic Background Elements */}
            <div className="absolute inset-0 z-0">
                <div 
                    className="absolute inset-0 opacity-30 transition-transform duration-1000 ease-out mix-blend-screen"
                    style={{
                        background: `radial-gradient(1200px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(16, 185, 129, 0.15), transparent 40%)`
                    }}
                />
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary-900/20 rounded-full blur-[150px] mix-blend-screen" />
                <div className="absolute bottom-[-20%] left-[-10%] w-[1000px] h-[1000px] bg-teal-900/20 rounded-full blur-[150px] mix-blend-screen" />
                
                {/* Advanced Grid Topology */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,black_10%,transparent_100%)]" />
            </div>

            <div className="container mx-auto px-4 grid lg:grid-cols-2 gap-20 items-center relative z-10 pt-20">
                <motion.div style={{ y: y1, opacity }} className="text-left space-y-12">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                    >
                        <div className="inline-flex items-center gap-4 px-6 py-3 rounded-full bg-black/40 border border-primary-500/30 shadow-[0_0_50px_rgba(16,185,129,0.15)] backdrop-blur-xl relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-primary-500/10 to-primary-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                            <Activity className="w-4 h-4 text-primary-400 animate-pulse" />
                            <span className="text-primary-400 text-[10px] font-black tracking-[0.4em] uppercase">
                                System Synchronized • Live
                            </span>
                        </div>
                    </motion.div>

                    <div className="space-y-6">
                        <motion.h1
                            initial={{ opacity: 0, filter: "blur(20px)" }}
                            animate={{ opacity: 1, filter: "blur(0px)" }}
                            transition={{ duration: 1.5, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                            className="text-6xl md:text-[8rem] font-black text-white tracking-tighter leading-[0.85] uppercase relative"
                        >
                            <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40 drop-shadow-[0_0_30px_rgba(255,255,255,0.1)]">Neural</span>
                            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-400 via-emerald-300 to-teal-400 drop-shadow-[0_0_60px_rgba(16,185,129,0.4)]">Botanica</span>
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1.2, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
                            className="text-lg md:text-2xl text-gray-400 max-w-xl leading-relaxed font-medium"
                        >
                            The ultimate boundary between ancient Ayurvedic wisdom and <span className="text-white">high-fidelity neural computation.</span> Experience the monolith.
                        </motion.p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1.2, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
                        className="flex flex-col sm:flex-row gap-6 items-stretch sm:items-start w-full sm:w-auto"
                    >
                        <Link href="/predict" className="w-full sm:w-auto">
                            <Button className="group h-16 md:h-20 w-full sm:px-10 md:px-14 rounded-2xl bg-white hover:bg-gray-100 text-black font-black uppercase tracking-[0.2em] transition-all shadow-[0_0_80px_rgba(255,255,255,0.15)] hover:shadow-[0_0_100px_rgba(255,255,255,0.3)] active:scale-95 flex items-center justify-center gap-4">
                                <Fingerprint className="w-6 h-6 group-hover:scale-110 transition-transform" />
                                Initiate Scan
                            </Button>
                        </Link>
                        <Link href="/symptom-search" className="w-full sm:w-auto">
                            <Button variant="outline" className="h-16 md:h-20 w-full sm:px-10 rounded-2xl border-white/10 text-white font-black uppercase tracking-[0.2em] hover:bg-white/5 transition-all backdrop-blur-xl group flex items-center justify-center gap-4">
                                <Database className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                                Clinical Search
                            </Button>
                        </Link>
                    </motion.div>
                </motion.div>

                {/* Highly Immersive 3D/Parallax Visual Asset */}
                <motion.div 
                    style={{ y: y2 }}
                    initial={{ opacity: 0, scale: 0.8, rotateY: 15 }}
                    animate={{ opacity: 1, scale: 1, rotateY: 0 }}
                    transition={{ duration: 2, ease: [0.16, 1, 0.3, 1] }}
                    className="relative hidden lg:block perspective-[2000px]"
                >
                    <div className="absolute inset-[-20%] bg-primary-500/20 rounded-full blur-[120px] animate-pulse mix-blend-screen pointer-events-none" />
                    
                    <motion.div 
                        whileHover={{ scale: 1.02, rotateY: -5, rotateX: 5 }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                        className="glass-card p-4 relative overflow-hidden group rounded-[48px] border border-white/10 shadow-[0_40px_100px_-20px_rgba(16,185,129,0.3)] bg-black/40 backdrop-blur-3xl transform-gpu"
                    >
                        {/* Immersive Scanning Line */}
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-400 to-transparent shadow-[0_0_30px_rgba(16,185,129,1)] z-20 animate-scan pointer-events-none" />
                        <div className="absolute inset-0 bg-primary-500/5 group-hover:bg-transparent transition-colors z-10 pointer-events-none" />
                        
                        <img 
                            src="https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?q=80&w=2574&auto=format&fit=crop" 
                            alt="Neural Monolith Vision" 
                            className="w-full aspect-[4/5] object-cover rounded-[36px] grayscale contrast-[1.1] opacity-60 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-[2000ms] ease-out"
                        />
                        
                        {/* Tactical HUD Overlays */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent z-10 pointer-events-none" />
                        
                        <div className="absolute top-8 right-8 z-20 flex flex-col gap-3">
                            <div className="w-12 h-12 rounded-xl bg-black/50 backdrop-blur-md border border-white/10 flex items-center justify-center">
                                <ShieldCheck className="w-5 h-5 text-primary-400" />
                            </div>
                        </div>

                        <div className="absolute bottom-10 left-10 right-10 z-20">
                            <div className="p-6 bg-black/60 backdrop-blur-2xl border border-white/10 rounded-[24px] overflow-hidden relative">
                                <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-transparent" />
                                <div className="relative flex items-center justify-between mb-4">
                                    <div className="flex flex-col">
                                        <span className="text-[9px] font-black text-gray-400 uppercase tracking-[0.3em]">Telemetry</span>
                                        <span className="text-white font-mono text-sm tracking-widest">A-V3 | L-88ms</span>
                                    </div>
                                    <div className="flex gap-1.5">
                                        {[...Array(5)].map((_, i) => (
                                            <motion.div 
                                                key={i} 
                                                className="w-1 h-4 rounded-full bg-primary-500"
                                                animate={{ height: ["16px", "8px", "24px", "16px"] }}
                                                transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.2 }}
                                            />
                                        ))}
                                    </div>
                                </div>
                                <div className="h-0.5 w-full bg-white/10 rounded-full overflow-hidden relative">
                                    <motion.div 
                                        className="absolute inset-y-0 left-0 bg-primary-400 shadow-[0_0_10px_rgba(16,185,129,1)]"
                                        animate={{ width: ["0%", "100%", "0%"] }}
                                        transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                                    />
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            </div>

            {/* Scroll Indicator - Hidden on mobile to prevent overlap */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 2, duration: 1 }}
                className="absolute bottom-12 left-1/2 -translate-x-1/2 hidden sm:flex flex-col items-center gap-3 z-20"
            >
                <span className="text-[9px] font-black text-gray-500 uppercase tracking-[0.4em] rotate-90 translate-y-[-10px] origin-bottom">Scroll</span>
                <div className="w-[1px] h-16 bg-gradient-to-b from-primary-500/50 to-transparent" />
            </motion.div>
        </section>
    );
};
