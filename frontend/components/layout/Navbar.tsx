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
    { name: "Botanical DB", href: "/plants" },
    { name: "Architects", href: "/about" },
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
                    "fixed top-0 left-0 w-full z-50 transition-all duration-300 border-b border-transparent",
                    isScrolled ? "bg-white/80 backdrop-blur-md shadow-sm border-gray-200/50" : "bg-transparent"
                )}
            >
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-20">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="relative w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center text-white shadow-lg group-hover:rotate-12 transition-transform">
                                <Leaf className="w-6 h-6" />
                            </div>
                            <div className="flex flex-col">
                                <span className={cn("text-lg font-black leading-none tracking-tight", isScrolled ? "text-gray-900" : "text-gray-900")}>
                                    MEDICINAL
                                </span>
                                <span className="text-xs font-bold text-primary-600 tracking-widest uppercase">PLANT AI</span>
                            </div>
                        </Link>

                        {/* Desktop Nav */}
                        <div className="hidden md:flex items-center gap-8">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    href={link.href}
                                    className={cn(
                                        "text-sm font-bold transition-colors hover:text-primary-600",
                                        pathname === link.href ? "text-primary-600" : "text-gray-600"
                                    )}
                                >
                                    {link.name}
                                </Link>
                            ))}
                            <Link href="/predict">
                                <Button size="sm" variant="primary">
                                    Get Started
                                </Button>
                            </Link>
                        </div>

                        {/* Mobile Toggle */}
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="md:hidden p-2 text-gray-600"
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
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden fixed top-20 left-0 w-full bg-white border-b border-gray-100 shadow-xl z-40 overflow-hidden"
                    >
                        <div className="container mx-auto px-4 py-6 flex flex-col gap-4">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    href={link.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={cn(
                                        "text-lg font-bold py-2 border-b border-gray-50",
                                        pathname === link.href ? "text-primary-600" : "text-gray-600"
                                    )}
                                >
                                    {link.name}
                                </Link>
                            ))}
                            <Link href="/predict" onClick={() => setIsMobileMenuOpen(false)}>
                                <Button className="w-full mt-4">Get Started</Button>
                            </Link>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};
