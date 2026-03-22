"use client"

import { cn } from "@/utils/cn"

interface ProgressProps {
  value: number
  className?: string
  max?: number
}

export function Progress({ value, max = 100, className }: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  return (
    <div className={cn("relative h-3 w-full overflow-hidden rounded-full bg-secondary", className)}>
      <div 
        className={cn(
          "h-full w-full flex-none bg-gradient-to-r from-primary to-green-500 transition-all duration-1000 ease-out",
          percentage === 100 ? "shadow-glow" : ""
        )} 
        style={{ transform: `translateX(-${100 - percentage}%)` }}
      />
    </div>
  )
}
