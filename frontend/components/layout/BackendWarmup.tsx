"use client";
import { useEffect } from "react";

export function BackendWarmup() {
  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://plantoai-backend.onrender.com"
    fetch(`${API_BASE}/health`).catch(() => {});
  }, []);
  return null;
}
