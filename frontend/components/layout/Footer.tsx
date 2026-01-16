"use client";

import React from "react";
import Link from "next/link";
import { Leaf, Github, Twitter, Linkedin, Heart } from "lucide-react";

export const Footer = () => {
    return (
        <footer className="bg-gray-900 text-white pt-24 pb-12 relative overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-600 via-green-400 to-primary-600 opacity-50"></div>
            <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl"></div>

            <div className="container mx-auto px-4 relative z-10">
                <div className="grid md:grid-cols-4 gap-12 mb-20">
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="flex items-center gap-2 group mb-6">
                            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-primary-400">
                                <Leaf className="w-6 h-6" />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-lg font-black leading-none tracking-tight">MEDICINAL</span>
                                <span className="text-xs font-bold text-primary-400 tracking-widest uppercase">PLANT AI</span>
                            </div>
                        </Link>
                        <p className="text-gray-400 text-sm leading-relaxed mb-6">
                            Bridging the gap between traditional botanical wisdom and modern artificial intelligence.
                        </p>
                        <div className="flex gap-4">
                            <SocialIcon icon={<Github className="w-4 h-4" />} />
                            <SocialIcon icon={<Twitter className="w-4 h-4" />} />
                            <SocialIcon icon={<Linkedin className="w-4 h-4" />} />
                        </div>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Product</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><Link href="/predict" className="hover:text-primary-400 transition-colors">Neural Scanner</Link></li>
                            <li><Link href="/plants" className="hover:text-primary-400 transition-colors">Plant Database</Link></li>
                            <li><Link href="/api-docs" className="hover:text-primary-400 transition-colors">API Reference</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Resources</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><Link href="/about" className="hover:text-primary-400 transition-colors">Documentation</Link></li>
                            <li><Link href="/about" className="hover:text-primary-400 transition-colors">Research Paper</Link></li>
                            <li><Link href="#" className="hover:text-primary-400 transition-colors">Dataset</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Project Info</h4>
                        <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Developed By</p>
                            <p className="text-white font-bold mb-1">Group G9</p>
                            <p className="text-xs text-gray-400">Dr. DY Patil College of Eng. and Innovation, Varale (Talegaon)</p>
                        </div>
                    </div>
                </div>

                <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-xs text-gray-500 font-medium">
                        © 2026 Medicinal Plant AI. Open Source Project.
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>Made with</span>
                        <Heart className="w-3 h-3 text-red-500 fill-red-500" />
                        <span>for nature & health</span>
                    </div>
                </div>
            </div>
        </footer>
    );
};

const SocialIcon = ({ icon }: { icon: React.ReactNode }) => (
    <a href="#" className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:bg-primary-600 hover:text-white transition-all">
        {icon}
    </a>
);
