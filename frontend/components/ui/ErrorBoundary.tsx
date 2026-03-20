'use client'

import { Component, ReactNode, ErrorInfo } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from './Button'
import { toast } from 'sonner'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
    toast.error(`Component error: ${error.message}`)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-8">
          <div className="max-w-md w-full space-y-6 text-center">
            <AlertCircle className="w-24 h-24 mx-auto text-destructive" />
            <div className="space-y-3">
              <h2 className="text-2xl font-bold">Something went wrong</h2>
              <p className="text-muted-foreground">
                {this.state.error?.message || 'Unknown error occurred. Please try reloading.'}
              </p>
            </div>
            <Button onClick={this.handleReset} className="w-full gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Reload Page
            </Button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export { ErrorBoundary }

