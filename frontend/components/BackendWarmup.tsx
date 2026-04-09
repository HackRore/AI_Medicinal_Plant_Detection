// frontend/components/BackendWarmup.tsx
"use client";
import { useEffect } from "react";
export default function BackendWarmup() {
  useEffect(() => {
    fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/ping").catch(() => {});
  }, []);
  return null;
}
