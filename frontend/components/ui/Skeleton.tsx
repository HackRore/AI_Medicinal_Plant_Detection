"use client"

import { cn } from "@/utils/cn"
import { forwardRef } from "react"

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "animate-pulse rounded-md bg-muted",
        className
      )}
      {...props}
    />
  )
)

Skeleton.displayName = "Skeleton"

