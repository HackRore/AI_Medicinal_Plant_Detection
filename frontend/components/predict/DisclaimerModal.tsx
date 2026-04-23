"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldAlert, CheckCircle2, FlaskConical, AlertTriangle } from "lucide-react";

export default function DisclaimerModal() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem("plantoai_legal_accepted");
    if (!accepted) {
      setIsOpen(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem("plantoai_legal_accepted", "true");
    setIsOpen(false);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div key="legal-modal-container" className="fixed inset-0 z-[100] flex items-center justify-center p-6 sm:p-12">
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/80 backdrop-blur-md"
            onClick={() => {}} 
          />

          {/* Modal Container */}
          <motion.div
            key="modal"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative w-full max-w-2xl bg-zinc-950 border border-white/10 rounded-[48px] overflow-hidden shadow-[0_0_100px_rgba(255,0,0,0.1)]"
          >
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-rose-500 to-transparent" />

            <div className="p-10 sm:p-14 space-y-8">
              <div className="flex flex-col items-center text-center space-y-6">
                <div className="w-20 h-20 bg-rose-500/10 rounded-full flex items-center justify-center border border-rose-500/20">
                  <ShieldAlert className="w-10 h-10 text-rose-500 animate-pulse" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Clinical Safety Protocol</h2>
                  <p className="text-rose-500/60 text-[10px] font-black uppercase tracking-[0.4em]">PlantoAI Neural Defense v5.1</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="p-6 bg-white/5 border border-white/5 rounded-3xl space-y-4">
                  <div className="flex items-start gap-4">
                    <div className="mt-1 w-5 h-5 rounded-full bg-rose-500/20 flex items-center justify-center border border-rose-500/30 flex-shrink-0">
                      <AlertTriangle className="w-3 h-3 text-rose-500" />
                    </div>
                    <p className="text-sm text-gray-400 font-medium leading-relaxed">
                      This AI system is a prototype designed for <span className="text-white font-bold">educational and research validation only</span>. It is not a certified medical device.
                    </p>
                  </div>
                  
                  <div className="flex items-start gap-4">
                    <div className="mt-1 w-5 h-5 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 flex-shrink-0">
                      <FlaskConical className="w-3 h-3 text-indigo-400" />
                    </div>
                    <p className="text-sm text-gray-400 font-medium leading-relaxed">
                      Plant identification and medicinal monographs must be verified by a qualified Ayurvedic practitioner before any application.
                    </p>
                  </div>
                </div>

                <p className="text-[10px] text-gray-500 text-center italic px-8">
                  By clicking accept, you acknowledge that you will not ingest or apply any botanical species based solely on neural identification.
                </p>
              </div>

              <div className="flex justify-center">
                <button
                  onClick={handleAccept}
                  className="group relative px-12 py-5 bg-white text-black text-[10px] font-black uppercase tracking-[0.3em] rounded-2xl hover:bg-rose-500 hover:text-white transition-all active:scale-95 overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    Accept Protocol & Sync Engine <CheckCircle2 className="w-3 h-3" />
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-rose-600 to-rose-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
