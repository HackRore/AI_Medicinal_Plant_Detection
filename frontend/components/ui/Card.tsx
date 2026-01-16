"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

interface CardProps {
    className?: string;
    children: React.ReactNode;
    hoverEffect?: boolean;
}

export const Card = ({ className, children, hoverEffect = true }: CardProps) => {
    return (
        <motion.div
            whileHover={hoverEffect ? { y: -5 } : undefined}
            className={cn(
                "relative overflow-hidden rounded-3xl bg-white/50 backdrop-blur-sm border border-white/40 shadow-xl",
                className
            )}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/40 to-white/0 pointer-events-none" />
            <div className="relative z-10 p-6 sm:p-8">
                {children}
            </div>
        </motion.div>
    );
};
