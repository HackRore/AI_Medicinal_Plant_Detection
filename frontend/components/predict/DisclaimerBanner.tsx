'use client';

import { motion } from "framer-motion";
import { ShieldAlert } from "lucide-react";

export const DisclaimerBanner = () => {
    return (
        <div className="fixed top-[88px] left-0 w-full z-[9999] px-4 pointer-events-none flex justify-center">
            <motion.div 
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="max-w-4xl w-full bg-amber-500/20 backdrop-blur-3xl border border-amber-500/30 rounded-2xl p-5 flex items-center gap-4 pointer-events-auto shadow-[0_0_80px_rgba(245,158,11,0.25)]"
            >
                <div className="w-12 h-12 rounded-2xl bg-amber-500/20 flex items-center justify-center flex-shrink-0 border border-amber-500/30">
                    <ShieldAlert className="w-6 h-6 text-amber-500" />
                </div>
                <div className="flex-1">
                    <p className="text-[10px] sm:text-xs font-black text-amber-400 leading-none uppercase tracking-[0.2em] mb-1">
                        Educational Use Only
                    </p>
                    <p className="text-[9px] sm:text-[10px] font-bold text-amber-200/60 leading-tight uppercase tracking-wider">
                        Identification and Ayurvedic monographs must be verified by a qualified practitioner before any use.
                    </p>
                </div>
            </motion.div>
        </div>
    );
};
