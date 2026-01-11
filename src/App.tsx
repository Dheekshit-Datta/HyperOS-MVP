import React, { useState, useEffect, useRef } from 'react'
import { Command, Mic, Settings, Terminal, Activity, X, Minus, Send, MousePointer2, CheckCircle2, ChevronRight, Layout, Cpu, Target } from 'lucide-react'

declare global {
    interface Window {
        ipcRenderer: {
            setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => void;
        }
    }
}

interface Step {
    step: number;
    analysis: string;
    action: {
        type: string;
        target?: string;
        reasoning: string;
        coords?: [number, number];
    };
}

function App() {
    const [input, setInput] = useState('')
    const [history, setHistory] = useState<Step[]>([])
    const [isProcessing, setIsProcessing] = useState(false)
    const [currentStatus, setCurrentStatus] = useState<string>('')
    const chatRef = useRef<HTMLDivElement>(null)
    const scrollRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (chatRef.current) {
                const rect = chatRef.current.getBoundingClientRect()
                const isInside = (
                    e.clientX >= rect.left &&
                    e.clientX <= rect.right &&
                    e.clientY >= rect.top &&
                    e.clientY <= rect.bottom
                )
                window.ipcRenderer.setIgnoreMouseEvents(!isInside, { forward: true })
            }
        }
        window.addEventListener('mousemove', handleMouseMove)
        return () => window.removeEventListener('mousemove', handleMouseMove)
    }, [])

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [history, isProcessing])

    const handleCommand = async () => {
        if (!input.trim()) return
        setIsProcessing(true)
        setCurrentStatus('Initializing Agent...')
        const currentInput = input
        setInput('')
        setHistory([])

        try {
            const res = await fetch('http://127.0.0.1:8000/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: currentInput })
            })
            const data = await res.json()

            if (data.status === 'success' || data.status === 'timeout') {
                setHistory(data.history || [])
            } else {
                // Error handling
                console.error(data.message)
            }
        } catch (e) {
            console.error('Failed to connect to agent core.')
        }
        setIsProcessing(false)
        setCurrentStatus('')
    }

    return (
        <div className="h-screen w-full relative overflow-hidden pointer-events-none select-none font-['Inter',_sans-serif] text-white">

            {/* Background Glow */}
            <div className="absolute inset-0 bg-transparent" />

            {/* Main Agent Interface */}
            <div
                ref={chatRef}
                className="absolute right-8 top-1/2 -translate-y-1/2 w-[450px] h-[800px] bg-slate-950/80 backdrop-blur-2xl border border-white/10 rounded-[32px] shadow-[0_0_100px_rgba(0,0,0,0.8),0_0_40px_rgba(0,128,255,0.1)] flex flex-col overflow-hidden pointer-events-auto animate-in slide-in-from-right duration-700 ring-1 ring-white/5"
            >
                {/* Header */}
                <div className="px-8 py-6 flex items-center justify-between bg-white/5 border-b border-white/5">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#0080FF] to-[#00C2FF] flex items-center justify-center shadow-[0_0_20px_rgba(0,128,255,0.4)]">
                                <Cpu className="w-6 h-6 text-white" />
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-green-500 border-2 border-slate-950 shadow-[0_0_10px_#22c55e]" />
                        </div>
                        <div>
                            <h1 className="font-bold text-lg tracking-tight">HyperOS</h1>
                            <p className="text-[10px] text-white/40 font-bold uppercase tracking-[0.2em]">Autonomous Model v1.0</p>
                        </div>
                    </div>
                </div>

                {/* Progress Content */}
                <div
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-hide"
                >
                    {history.length === 0 && !isProcessing && (
                        <div className="h-full flex flex-col items-center justify-center text-center space-y-6 opacity-60">
                            <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                                <Command className="w-10 h-10 text-[#0080FF]" />
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold mb-2">Awaiting Instructions</h2>
                                <p className="text-sm text-white/40 max-w-[200px] mx-auto">Input a task to begin the Analyze-Plan-Execute cycle.</p>
                            </div>
                        </div>
                    )}

                    {history.map((step, i) => (
                        <div key={i} className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-xs font-bold text-[#0080FF]">
                                    {step.step}
                                </div>
                                <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                            </div>

                            {/* Analyze Phase */}
                            <div className="group relative pl-4 border-l-2 border-[#0080FF]/20 hover:border-[#0080FF] transition-colors">
                                <div className="flex items-center gap-2 mb-2 text-[10px] font-bold text-[#0080FF] uppercase tracking-widest">
                                    <Layout className="w-3 h-3" />
                                    <span>Analyze</span>
                                </div>
                                <p className="text-sm text-white/70 leading-relaxed">{step.analysis}</p>
                            </div>

                            {/* Plan Phase */}
                            <div className="group relative pl-4 border-l-2 border-purple-500/20 hover:border-purple-500 transition-colors">
                                <div className="flex items-center gap-2 mb-2 text-[10px] font-bold text-purple-500 uppercase tracking-widest">
                                    <Target className="w-3 h-3" />
                                    <span>Plan</span>
                                </div>
                                <p className="text-sm text-white/70 leading-relaxed italic">"{step.action.reasoning}"</p>
                            </div>

                            {/* Execute Phase */}
                            <div className="group relative pl-4 border-l-2 border-green-500/20 hover:border-green-500 transition-colors">
                                <div className="flex items-center gap-2 mb-2 text-[10px] font-bold text-green-500 uppercase tracking-widest">
                                    <ChevronRight className="w-3 h-3" />
                                    <span>Execute</span>
                                </div>
                                <div className="flex items-center gap-3 p-3 bg-white/5 rounded-xl border border-white/5">
                                    <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_#22c55e]" />
                                    <span className="text-xs font-mono text-white/90">
                                        {step.action.type.toUpperCase()}(
                                        {step.action.target || step.action.key || step.action.coords?.join(', ')}
                                        )
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}

                    {isProcessing && (
                        <div className="space-y-4 animate-pulse">
                            <div className="h-px bg-white/10" />
                            <div className="flex items-center gap-3">
                                <Activity className="w-5 h-5 text-[#0080FF] animate-spin" />
                                <span className="text-sm font-medium text-white/60">{currentStatus || 'Processing next cycle...'}</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-8 bg-black/40 border-t border-white/5">
                    <div className="relative group">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleCommand()}
                            placeholder="What task should I perform?"
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm text-white placeholder-white/20 focus:outline-none focus:border-[#0080FF]/50 focus:ring-4 focus:ring-[#0080FF]/10 transition-all"
                            disabled={isProcessing}
                        />
                        <button
                            onClick={handleCommand}
                            disabled={isProcessing}
                            className={`absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-xl transition-all ${isProcessing
                                    ? 'bg-white/5 text-white/20'
                                    : 'bg-[#0080FF] text-white hover:bg-[#0080FF]/80 shadow-[0_0_15px_rgba(0,128,255,0.4)] hover:scale-105 active:scale-95'
                                }`}
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Footer Deco */}
                <div className="px-8 pb-4 flex justify-between items-center opacity-20 group">
                    <div className="flex gap-1.5">
                        <div className="w-1 h-1 rounded-full bg-white" />
                        <div className="w-1 h-1 rounded-full bg-white" />
                        <div className="w-1 h-1 rounded-full bg-white" />
                    </div>
                    <span className="text-[10px] font-black tracking-widest uppercase">System Active</span>
                </div>
            </div>

            {/* Visual Indicator of Execution (Optional) */}
            {isProcessing && (
                <div className="absolute top-8 left-1/2 -translate-x-1/2 px-6 py-3 bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-full flex items-center gap-3 shadow-2xl animate-in fade-in slide-in-from-top-4">
                    <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
                    <span className="text-xs font-bold uppercase tracking-widest text-white/80">Agent Operational Mode</span>
                </div>
            )}

        </div>
    )
}

export default App
