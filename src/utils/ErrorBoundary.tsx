/**
 * HyperOS React Error Boundary
 * Catches render errors and displays friendly UI
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        this.setState({ errorInfo });
        console.error('ErrorBoundary caught:', error, errorInfo);

        // Log to backend
        this.logError(error, errorInfo);
    }

    async logError(error: Error, errorInfo: ErrorInfo): Promise<void> {
        try {
            await fetch('http://127.0.0.1:8000/log-error', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: error.message,
                    stack: error.stack,
                    componentStack: errorInfo.componentStack,
                    timestamp: new Date().toISOString(),
                }),
            });
        } catch {
            // Silently fail if backend unavailable
        }
    }

    handleRetry = (): void => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    handleReload = (): void => {
        window.location.reload();
    };

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) return this.props.fallback;

            return (
                <div className="fixed inset-0 flex items-center justify-center bg-slate-900/95 backdrop-blur-xl p-6">
                    <div className="max-w-md w-full bg-slate-800/80 rounded-2xl border border-red-500/30 p-8 text-center">
                        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center">
                            <AlertTriangle className="w-8 h-8 text-red-400" />
                        </div>

                        <h2 className="text-xl font-bold text-white mb-2">
                            Something went wrong
                        </h2>

                        <p className="text-white/60 text-sm mb-6">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>

                        <div className="flex gap-3 justify-center">
                            <button
                                onClick={this.handleRetry}
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg text-white text-sm transition-colors"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Try Again
                            </button>
                            <button
                                onClick={this.handleReload}
                                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white/80 text-sm transition-colors"
                            >
                                <Home className="w-4 h-4" />
                                Reload
                            </button>
                        </div>

                        {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                            <details className="mt-6 text-left">
                                <summary className="text-xs text-white/40 cursor-pointer">
                                    Stack trace
                                </summary>
                                <pre className="mt-2 p-3 bg-black/30 rounded-lg text-xs text-red-300/80 overflow-auto max-h-32">
                                    {this.state.error?.stack}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
