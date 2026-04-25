"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

export const BackgroundEffects = () => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="fixed inset-0 -z-50 bg-[#050505]" />;

  return (
    <div className="fixed inset-0 -z-50 overflow-hidden bg-[#050505]">
      {/* Noise Texture */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]" />
      
      {/* Mesh Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary-500/10 blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-900/10 blur-[150px]" />
      
      {/* Tactical Grid */}
      <div 
        className="absolute inset-0 opacity-[0.05]" 
        style={{ 
          backgroundImage: `linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)`,
          backgroundSize: '100px 100px'
        }} 
      />

      {/* Floating Particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ 
            opacity: Math.random() * 0.5, 
            x: Math.random() * 100 + "%", 
            y: Math.random() * 100 + "%" 
          }}
          animate={{ 
            y: ["0%", "100%"],
            opacity: [0, 0.5, 0]
          }}
          transition={{ 
            duration: Math.random() * 20 + 20, 
            repeat: Infinity, 
            ease: "linear" 
          }}
          className="absolute w-1 h-1 bg-primary-500/20 rounded-full"
        />
      ))}

      {/* Scanline Effect */}
      <div className="scanline" />
    </div>
  );
};
