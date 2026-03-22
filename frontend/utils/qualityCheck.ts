/**
 * Quality Check Integration Utility
 * Frontend helper for image quality validation before ML inference
 */

export interface QualityCheckResult {
  is_valid: boolean
  scores: {
    blur: number
    blur_threshold: number
    blur_passed: boolean
    brightness: boolean
    composition: boolean
  }
  reasons: string[]
  recommendations: string[]
  image_shape: [number, number, number]
  image_size_mb: number
  filename?: string
  content_type?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1"

/**
 * Check image quality before prediction
 */
export async function checkImageQuality(
  file: File,
  strict: boolean = false
): Promise<QualityCheckResult> {
  const formData = new FormData()
  formData.append("file", file)

  const endpoint = strict ? "/quality-check/strict" : "/quality-check/"

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || "Quality check failed")
  }

  return response.json()
}

/**
 * Format quality feedback for user display
 */
export function formatQualityFeedback(result: QualityCheckResult): {
  status: "pass" | "fail"
  title: string
  message: string
  recommendations: string[]
  metrics: string[]
} {
  if (result.is_valid) {
    return {
      status: "pass",
      title: "Image Quality: Excellent ✓",
      message: "Your image looks great! Ready for plant identification.",
      recommendations: [],
      metrics: [
        `Sharpness: ${result.scores.blur.toFixed(0)} (threshold: ${result.scores.blur_threshold})`,
        `Brightness: Good`,
        `Composition: Good`,
      ],
    }
  }

  return {
    status: "fail",
    title: "Image Quality: Needs Improvement",
    message: `We detected ${result.reasons.length} issue(s) with your image.`,
    recommendations: result.recommendations,
    metrics: [
      `Sharpness: ${result.scores.blur.toFixed(0)} (threshold: ${result.scores.blur_threshold})`,
      ...result.reasons.map((r) => `⚠ ${r}`),
    ],
  }
}

/**
 * Confidence level text
 */
export function getConfidenceLevel(
  confidence: number
): {
  level: "low" | "medium" | "high" | "very_high"
  text: string
  color: string
} {
  if (confidence >= 0.95) {
    return {
      level: "very_high",
      text: "Very High Confidence",
      color: "text-green-600",
    }
  } else if (confidence >= 0.80) {
    return {
      level: "high",
      text: "High Confidence",
      color: "text-emerald-600",
    }
  } else if (confidence >= 0.60) {
    return {
      level: "medium",
      text: "Medium Confidence",
      color: "text-amber-600",
    }
  } else {
    return {
      level: "low",
      text: "Low Confidence",
      color: "text-orange-600",
    }
  }
}
