"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Leaf } from "lucide-react";
import { cn } from "@/utils/cn";
import { Button } from "../ui/Button";

const navLinks = [
    { name: "Home", href: "/" },
    { name: "Neural Scanner", href: "/predict" },
    { name: "Symptom Search", href: "/symptom-search" },
    { name: "Botanical DB", href: "/plants" },
    { name: "About", href: "/about" },
];

export const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const pathname = usePathname();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <>
            <motion.nav
                initial={{ y: -100 }}
                animate={{ y: 0 }}
                transition={{ duration: 0.5 }}
                className={cn(
                    "fixed top-0 left-0 w-full z-50 transition-all duration-300 border-b",
                    isScrolled ? "bg-black/80 backdrop-blur-xl border-white/10 shadow-2xl" : "bg-transparent border-transparent"
                )}
            >
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-20">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="relative w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center text-black shadow-lg group-hover:rotate-12 transition-transform">
                                <Leaf className="w-6 h-6" />
                            </div>
                            <div className="flex flex-col">
                                <span className={cn("text-lg font-black leading-none tracking-tighter text-white")}>
                                    PLANTO<span className="text-primary-400">AI</span>
                                </span>
                                <span className="text-[8px] font-black text-gray-500 tracking-[0.4em] uppercase">Tactical Botani</span>
                            </div>
                        </Link>

                        {/* Desktop Nav */}
                        <div className="hidden md:flex items-center gap-10">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    href={link.href}
                                    className={cn(
                                        "text-[10px] font-black uppercase tracking-[0.2em] transition-all hover:text-primary-400",
                                        pathname === link.href ? "text-primary-400" : "text-gray-400"
                                    )}
                                >
                                    {link.name}
                                </Link>
                            ))}
                            <Link href="/predict">
                                <Button size="sm" className="bg-primary-500 text-black font-black uppercase tracking-widest text-[10px] px-6 rounded-xl hover:bg-primary-400 transition-all shadow-xl shadow-primary-500/20">
                                    Launch HUD
                                </Button>
                            </Link>
                        </div>

                        {/* Mobile Toggle */}
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="md:hidden p-2 text-white"
                        >
                            {isMobileMenuOpen ? <X /> : <Menu />}
                        </button>
                    </div>
                </div>
            </motion.nav>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="md:hidden fixed top-20 left-0 w-full bg-black/95 backdrop-blur-2xl border-b border-white/10 z-40 overflow-hidden"
                    >
                        <div className="container mx-auto px-4 py-8 flex flex-col gap-6">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    href={link.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={cn(
                                        "text-xs font-black uppercase tracking-[0.3em] py-3 border-b border-white/5",
                                        pathname === link.href ? "text-primary-400" : "text-gray-400"
                                    )}
                                >
                                    {link.name}
                                </Link>
                            ))}
                            <Link href="/predict" onClick={() => setIsMobileMenuOpen(false)}>
                                <Button className="w-full h-16 rounded-2xl bg-primary-500 text-black font-black uppercase tracking-widest">Launch Scanner</Button>
                            </Link>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};
