/**
 * HyperOS - AI Desktop Agent Frontend
 * A beautiful, transparent overlay UI for the vision-enabled AI agent
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Zap,
    Eye,
    Brain,
    PlayCircle,
    StopCircle,
    Mic,
    Settings,
    Send,
    Loader2,
    AlertCircle,
    CheckCircle2,
    Minimize2,
    X,
    Sparkles,
    Target,
    MousePointer2
} from 'lucide-react';

// API configuration
const API_BASE = 'http://127.0.0.1:8000';

// Types
interface Step {
    id: number;
    phase: 'analyze' | 'plan' | 'execute' | 'complete';
    thinking: string;
    action: string;
    parameters?: Record<string, any>;
    timestamp: number;
    status: 'pending' | 'active' | 'done' | 'error';
}

interface ApiStep {
    step: number;
    thinking: string;
    action: string;
    parameters?: Record<string, any>;
    done?: boolean;
}

interface TaskResponse {
    status: 'success' | 'error' | 'timeout' | 'cancelled';
    message?: string;
    history?: ApiStep[];
    steps_completed?: number;
}

// Phase icons and colors
const phaseConfig = {
    analyze: {
        icon: Eye,
        color: 'text-cyan-400',
        bg: 'bg-cyan-500/20',
        border: 'border-cyan-500/30',
        label: 'Analyzing Screen'
    },
    plan: {
        icon: Brain,
        color: 'text-purple-400',
        bg: 'bg-purple-500/20',
        border: 'border-purple-500/30',
        label: 'Planning Action'
    },
    execute: {
        icon: PlayCircle,
        color: 'text-green-400',
        bg: 'bg-green-500/20',
        border: 'border-green-500/30',
        label: 'Executing'
    },
    complete: {
        icon: CheckCircle2,
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/20',
        border: 'border-emerald-500/30',
        label: 'Complete'
    }
};

function App() {
    // State
    const [isVisible, setIsVisible] = useState(true);
    const [taskInput, setTaskInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [steps, setSteps] = useState<Step[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [currentStatus, setCurrentStatus] = useState<string>('');

    // Refs
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const lastInsideRef = useRef<boolean>(false);

    // Auto-scroll on new steps
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({
                top: scrollRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, [steps]);

    // Handle click-through for transparent areas
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (containerRef.current && window.hyperOS) {
                const rect = containerRef.current.getBoundingClientRect();
                const isInside = (
                    e.clientX >= rect.left &&
                    e.clientX <= rect.right &&
                    e.clientY >= rect.top &&
                    e.clientY <= rect.bottom
                );

                if (isInside !== lastInsideRef.current) {
                    window.hyperOS.setClickThrough(!isInside);
                    lastInsideRef.current = isInside;
                }
            }
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    // Auto-dismiss error
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    // Convert API response to steps
    const processApiResponse = useCallback((history: ApiStep[]): Step[] => {
        return history.map((item, idx) => ({
            id: idx,
            phase: item.done ? 'complete' :
                item.action === 'done' ? 'complete' :
                    'execute' as const,
            thinking: item.thinking || '',
            action: item.action || '',
            parameters: item.parameters,
            timestamp: Date.now(),
            status: 'done' as const
        }));
    }, []);

    // Submit task
    const handleSubmit = async () => {
        if (!taskInput.trim() || isProcessing) return;

        setIsProcessing(true);
        setSteps([]);
        setError(null);
        setCurrentStatus('Initializing agent...');

        try {
            const response = await fetch(`${API_BASE}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task: taskInput.trim() })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data: TaskResponse = await response.json();

            if (data.status === 'success' || data.status === 'timeout') {
                if (data.history) {
                    setSteps(processApiResponse(data.history));
                }
                setCurrentStatus(data.message || 'Task completed');
            } else if (data.status === 'cancelled') {
                setCurrentStatus('Task cancelled');
            } else {
                throw new Error(data.message || 'Task failed');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Connection failed';
            setError(errorMessage);
            setCurrentStatus('');
        } finally {
            setIsProcessing(false);
        }
    };

    // Cancel task
    const handleCancel = async () => {
        try {
            await fetch(`${API_BASE}/cancel`, { method: 'POST' });
            setCurrentStatus('Cancelling...');
        } catch {
            setError('Failed to cancel task');
        }
    };

    // Handle keyboard shortcuts
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="h-screen w-full relative overflow-hidden pointer-events-none select-none font-sans text-white">

            {/* Error Toast */}
            {error && (
                <div className="absolute top-6 right-6 z-50 pointer-events-auto animate-slide-down">
                    <div className="flex items-center gap-3 px-4 py-3 bg-red-500/90 backdrop-blur-xl rounded-xl border border-red-400/30 shadow-2xl">
                        <AlertCircle className="w-5 h-5 text-white" />
                        <span className="text-sm font-medium">{error}</span>
                        <button
                            onClick={() => setError(null)}
                            className="ml-2 hover:bg-white/10 p-1 rounded-lg transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Processing Indicator */}
            {isProcessing && (
                <div className="absolute top-6 left-1/2 -translate-x-1/2 z-50 animate-fade-in">
                    <div className="flex items-center gap-3 px-5 py-3 bg-slate-900/90 backdrop-blur-xl rounded-full border border-white/10 shadow-2xl">
                        <div className="relative">
                            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
                            <div className="absolute inset-0 w-3 h-3 rounded-full bg-red-500 animate-ping" />
                        </div>
                        <span className="text-sm font-medium text-white/80 uppercase tracking-wider">
                            Agent Active
                        </span>
                    </div>
                </div>
            )}

            {/* Main UI Container */}
            <div
                ref={containerRef}
                className="absolute right-6 top-1/2 -translate-y-1/2 w-[420px] h-[720px] 
                           bg-gradient-to-b from-slate-900/95 via-slate-900/90 to-slate-950/95
                           backdrop-blur-2xl border border-white/10 rounded-3xl 
                           shadow-[0_0_80px_rgba(0,0,0,0.8),0_0_40px_rgba(99,102,241,0.1)]
                           flex flex-col overflow-hidden pointer-events-auto
                           animate-slide-in ring-1 ring-white/5"
            >
                {/* Header */}
                <div className="px-6 py-5 flex items-center justify-between bg-gradient-to-r from-white/5 to-transparent border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
                                <Zap className="w-6 h-6 text-white" />
                            </div>
                            <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full bg-emerald-500 border-2 border-slate-900 flex items-center justify-center">
                                <div className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
                            </div>
                        </div>
                        <div>
                            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                                HyperOS
                            </h1>
                            <p className="text-[10px] text-white/40 font-semibold uppercase tracking-[0.2em]">
                                Vision AI Agent
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="p-2.5 rounded-xl hover:bg-white/5 transition-colors group">
                            <Settings className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors" />
                        </button>
                        <button
                            onClick={() => window.hyperOS?.hideWindow()}
                            className="p-2.5 rounded-xl hover:bg-white/5 transition-colors group"
                        >
                            <Minimize2 className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors" />
                        </button>
                    </div>
                </div>

                {/* Steps Display */}
                <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-hide">
                    {steps.length === 0 && !isProcessing && (
                        <div className="h-full flex flex-col items-center justify-center text-center space-y-5 opacity-60">
                            <div className="relative">
                                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-white/10">
                                    <Sparkles className="w-9 h-9 text-indigo-400" />
                                </div>
                                <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-indigo-500/30 flex items-center justify-center">
                                    <MousePointer2 className="w-3 h-3 text-indigo-300" />
                                </div>
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold mb-2 text-white/80">Ready to Assist</h2>
                                <p className="text-sm text-white/40 max-w-[220px] mx-auto leading-relaxed">
                                    Describe a task and I'll analyze the screen, plan actions, and execute them for you.
                                </p>
                            </div>
                            <div className="flex items-center gap-6 text-xs text-white/30">
                                <div className="flex items-center gap-2">
                                    <Eye className="w-4 h-4" />
                                    <span>See</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Brain className="w-4 h-4" />
                                    <span>Think</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Target className="w-4 h-4" />
                                    <span>Act</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {steps.map((step, idx) => {
                        const config = phaseConfig[step.phase];
                        const Icon = config.icon;

                        return (
                            <div
                                key={step.id}
                                className="animate-slide-up"
                                style={{ animationDelay: `${Math.min(idx * 50, 500)}ms` }}
                            >
                                {/* Step Number */}
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-xs font-bold text-indigo-400">
                                        {idx + 1}
                                    </div>
                                    <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                                </div>

                                {/* Step Card */}
                                <div className={`relative p-4 rounded-xl ${config.bg} border ${config.border} transition-all hover:border-opacity-50`}>
                                    {/* Phase Header */}
                                    <div className="flex items-center gap-2 mb-3">
                                        <Icon className={`w-4 h-4 ${config.color}`} />
                                        <span className={`text-xs font-bold uppercase tracking-wider ${config.color}`}>
                                            {config.label}
                                        </span>
                                        {step.status === 'done' && (
                                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 ml-auto" />
                                        )}
                                    </div>

                                    {/* Thinking */}
                                    {step.thinking && (
                                        <p className="text-sm text-white/70 leading-relaxed mb-3">
                                            {step.thinking}
                                        </p>
                                    )}

                                    {/* Action */}
                                    {step.action && step.action !== 'done' && (
                                        <div className="flex items-center gap-2 p-2.5 bg-black/30 rounded-lg">
                                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                            <code className="text-xs font-mono text-white/80">
                                                {step.action.toUpperCase()}
                                                {step.parameters && (
                                                    <span className="text-white/50">
                                                        ({Object.values(step.parameters).slice(0, 2).join(', ')})
                                                    </span>
                                                )}
                                            </code>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}

                    {/* Processing Indicator */}
                    {isProcessing && (
                        <div className="flex items-center gap-3 p-4 bg-white/5 rounded-xl border border-white/10 animate-pulse">
                            <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                            <span className="text-sm text-white/60">{currentStatus || 'Processing...'}</span>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-5 bg-gradient-to-t from-black/40 to-transparent border-t border-white/5">
                    <div className="relative group">
                        <textarea
                            ref={inputRef}
                            value={taskInput}
                            onChange={(e) => setTaskInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="What would you like me to do?"
                            rows={2}
                            disabled={isProcessing}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 pr-24
                                     text-sm text-white placeholder-white/30 resize-none
                                     focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20
                                     disabled:opacity-50 disabled:cursor-not-allowed
                                     transition-all duration-200"
                        />
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <button
                                className="p-2.5 rounded-xl text-white/30 hover:text-white/50 hover:bg-white/5 transition-all"
                                title="Voice input"
                            >
                                <Mic className="w-5 h-5" />
                            </button>
                            {isProcessing ? (
                                <button
                                    onClick={handleCancel}
                                    className="p-2.5 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all"
                                    title="Cancel"
                                >
                                    <StopCircle className="w-5 h-5" />
                                </button>
                            ) : (
                                <button
                                    onClick={handleSubmit}
                                    disabled={!taskInput.trim()}
                                    className="p-2.5 rounded-xl bg-indigo-500 text-white 
                                             hover:bg-indigo-600 disabled:opacity-30 disabled:cursor-not-allowed
                                             shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50
                                             hover:scale-105 active:scale-95 transition-all"
                                    title="Execute task"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Keyboard hint */}
                    <p className="text-center text-[10px] text-white/20 mt-3">
                        Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40">Enter</kbd> to send • <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40">Ctrl+Space</kbd> to toggle
                    </p>
                </div>

                {/* Footer */}
                <div className="px-6 py-3 flex justify-between items-center border-t border-white/5">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
                        <span className="text-[10px] font-medium text-white/30 uppercase tracking-widest">
                            {isProcessing ? 'Working' : 'Ready'}
                        </span>
                    </div>
                    <span className="text-[10px] text-white/20">v1.1.0</span>
                </div>
            </div>
        </div>
    );
}

export default App;
