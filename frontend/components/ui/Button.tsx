"use client";

import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/utils/cn"; // We need to create this util

interface ButtonProps extends HTMLMotionProps<"button"> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "glass";
    size?: "sm" | "md" | "lg";
    isLoading?: boolean;
    icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", size = "md", isLoading, icon, children, ...props }, ref) => {

        const variants = {
            primary: "bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/20 border border-transparent",
            secondary: "bg-secondary-500 text-white hover:bg-secondary-600 shadow-md",
            outline: "bg-transparent border-2 border-primary-600 text-primary-600 hover:bg-primary-50",
            ghost: "bg-transparent text-gray-700 hover:bg-gray-100",
            glass: "bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 shadow-xl",
        };

        const sizes = {
            sm: "px-4 py-2 text-sm",
            md: "px-6 py-3 text-base",
            lg: "px-8 py-4 text-lg",
        };

        return (
            <motion.button
                ref={ref}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                    "relative inline-flex items-center justify-center rounded-xl font-bold transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none",
                    variants[variant],
                    sizes[size],
                    className
                )}
                {...props}
            >
                {isLoading && (
                    <span className="mr-2 animate-spin rounded-full h-4 w-4 border-b-2 border-current"></span>
                )}
                {icon && <span className={cn("mr-2", isLoading && "opacity-0")}>{icon}</span>}
                <span className={isLoading ? "opacity-0" : ""}>{children as React.ReactNode}</span>
            </motion.button>
        );
    }
);

Button.displayName = "Button";
