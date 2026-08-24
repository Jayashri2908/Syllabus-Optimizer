import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import './ErrorBoundary.css';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackMessage?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[ErrorBoundary] Uncaught error:', error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-container">
          <div className="error-boundary-card glass-card">
            <div className="error-icon-wrapper">
              <AlertTriangle size={40} />
            </div>
            <h2>Something went wrong</h2>
            <p className="error-message">
              {this.props.fallbackMessage || 'An unexpected error occurred while rendering this page.'}
            </p>
            {this.state.error && (
              <pre className="error-detail mono-tag">
                {this.state.error.message}
              </pre>
            )}
            <div className="error-actions">
              <button className="btn-primary" onClick={this.handleReset}>
                <RotateCcw size={18} /> Try Again
              </button>
              <button
                className="btn-secondary"
                onClick={() => { window.location.href = '/'; }}
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
