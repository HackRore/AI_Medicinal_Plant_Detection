/**
 * Quality Feedback Component
 * Shows image quality assessment results to user
 */

'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, AlertTriangle, Zap } from 'lucide-react'
import { QualityCheckResult, formatQualityFeedback, getConfidenceLevel } from '@/utils/qualityCheck'

export interface QualityFeedbackProps {
  result: QualityCheckResult | null
  isLoading?: boolean
  confidence?: number
}

export function QualityFeedback({
  result,
  isLoading = false,
  confidence,
}: QualityFeedbackProps) {
  if (isLoading) {
    return (
      <div className="p-6 rounded-2xl bg-muted animate-pulse">
        <div className="h-6 bg-muted-foreground/20 rounded mb-4 w-1/2" />
        <div className="h-4 bg-muted-foreground/20 rounded w-3/4" />
      </div>
    )
  }

  if (!result) return null

  const feedback = formatQualityFeedback(result)
  const isPass = feedback.status === 'pass'

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className={`p-6 rounded-2xl border-2 ${
          isPass
            ? 'border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950'
            : 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950'
        }`}
      >
        <div className="flex items-start gap-4 mb-4">
          {isPass ? (
            <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
          )}
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${isPass ? 'text-green-900 dark:text-green-100' : 'text-amber-900 dark:text-amber-100'}`}>
              {feedback.title}
            </h3>
            <p className={`text-sm mt-1 ${isPass ? 'text-green-800 dark:text-green-200' : 'text-amber-800 dark:text-amber-200'}`}>
              {feedback.message}
            </p>
          </div>
        </div>

        {/* Metrics */}
        <div className="space-y-2 mb-4">
          {feedback.metrics.map((metric, idx) => (
            <div
              key={idx}
              className={`text-sm font-mono ${
                metric.startsWith('⚠')
                  ? 'text-amber-700 dark:text-amber-300'
                  : 'text-green-700 dark:text-green-300'
              }`}
            >
              {metric}
            </div>
          ))}
        </div>

        {/* Recommendations */}
        {feedback.recommendations.length > 0 && (
          <div className="space-y-2 pt-4 border-t border-amber-200 dark:border-amber-800">
            <p className="text-sm font-semibold text-amber-900 dark:text-amber-100">
              💡 How to improve:
            </p>
            <ul className="space-y-1">
              {feedback.recommendations.map((rec, idx) => (
                <li
                  key={idx}
                  className="text-sm text-amber-800 dark:text-amber-200 flex items-start gap-2"
                >
                  <span className="text-amber-600 dark:text-amber-400 mt-0.5">•</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

/**
 * Confidence Display Component
 * Shows prediction confidence level and top alternatives
 */
export interface ConfidenceDisplayProps {
  confidence: number
  topPredictions?: Array<{ class_name: string; probability: number }>
}

export function ConfidenceDisplay({
  confidence,
  topPredictions = [],
}: ConfidenceDisplayProps) {
  const confidenceInfo = getConfidenceLevel(confidence)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-4"
    >
      {/* Main Confidence */}
      <div className="bg-gradient-to-br from-primary/10 to-green-500/10 p-6 rounded-2xl border border-primary/20">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Model Confidence
          </span>
          <Zap className="w-4 h-4 text-primary" />
        </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={`h-full bg-gradient-to-r ${
                confidence >= 0.8
                  ? 'from-green-500 to-green-600'
                  : confidence >= 0.6
                    ? 'from-amber-500 to-amber-600'
                    : 'from-orange-500 to-orange-600'
              }`}
            />
          </div>
        </div>

        {/* Percentage and Level */}
        <div className="flex items-center justify-between">
          <span className="text-3xl font-bold">
            {(confidence * 100).toFixed(0)}%
          </span>
          <span className={`text-sm font-semibold ${confidenceInfo.color}`}>
            {confidenceInfo.text}
          </span>
        </div>
      </div>

      {/* Top Alternatives */}
      {topPredictions.length > 1 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Alternative Matches
          </p>
          {topPredictions.slice(1, 3).map((pred, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
            >
              <span className="text-sm font-medium">{pred.class_name}</span>
              <span className="text-xs text-muted-foreground">
                {(pred.probability * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground italic pt-2">
        🔬 For educational purposes. Always consult experts for medical use.
      </p>
    </motion.div>
  )
}
