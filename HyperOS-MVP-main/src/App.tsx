import { useState, useEffect, useRef } from 'react'
import { Command, Send, Activity, Layout, Cpu, Target, MousePointer2 } from 'lucide-react'

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
        coords_1000?: [number, number];
        key?: string;
        expected_outcome?: string;
    };
    verification?: any;
}

function App() {
    const [input, setInput] = useState('')
    const [history, setHistory] = useState<Step[]>([])
    const [isProcessing, setIsProcessing] = useState(false)
    const [currentStepInfo, setCurrentStepInfo] = useState<{ phase: 'analyze' | 'plan' | 'execute' | 'verify', message: string } | null>(null)
    const scrollRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [history, currentStepInfo])

    const handleCommand = async () => {
        if (!input.trim() || isProcessing) return

        const task = input
        setInput('')
        setHistory([])
        setIsProcessing(true)

        let currentHistory: Step[] = []
        // let finished = false // Removed as unused
        const maxCycles = 15

        for (let i = 0; i < maxCycles; i++) {
            setCurrentStepInfo({ phase: 'analyze', message: 'Analyzing screen state...' })

            try {
                const res = await fetch('http://127.0.0.1:8000/cycle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: task, history: currentHistory })
                })

                if (!res.ok) throw new Error('API Error')
                const data = await res.json()

                if (data.status === 'error') {
                    console.error(data.message)
                    break
                }

                const newStep: Step = {
                    step: currentHistory.length + 1,
                    analysis: data.analysis.screen_state,
                    action: data.action,
                    verification: data.verification
                }

                setCurrentStepInfo({ phase: 'plan', message: `Planning: ${data.action.reasoning}` })
                await new Promise(r => setTimeout(r, 800))

                setCurrentStepInfo({ phase: 'execute', message: `Executing ${data.action.type}...` })
                await new Promise(r => setTimeout(r, 500))

                setHistory(prev => [...prev, newStep])
                currentHistory.push(newStep)

                if (data.status === 'complete' || (data.verification && data.verification.next_action?.type === 'done')) {
                    break
                }

                setCurrentStepInfo({ phase: 'verify', message: 'Verifying outcome...' })
                await new Promise(r => setTimeout(r, 1000))

            } catch (e) {
                console.error('Cycle failed', e)
                break
            }
        }

        setIsProcessing(false)
        setCurrentStepInfo(null)
    }

    return (
        <div className="h-screen w-full flex items-center justify-center p-4 select-none font-['Inter',_sans-serif] text-white overflow-hidden">
            {/* Main Agent Interface - Fixed Size Overlay */}
            <div
                className="w-full h-full bg-slate-950/90 backdrop-blur-3xl border border-white/10 rounded-[32px] shadow-[0_0_100px_rgba(0,0,0,0.5)] flex flex-col overflow-hidden animate-in zoom-in-95 duration-500 ring-1 ring-white/5"
            >
                {/* Header */}
                <div className="px-6 py-4 flex items-center justify-between bg-white/5 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#0080FF] to-[#00C2FF] flex items-center justify-center shadow-[0_0_15px_rgba(0,128,255,0.3)]">
                                <Cpu className="w-5 h-5 text-white" />
                            </div>
                            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-green-500 border-2 border-slate-950" />
                        </div>
                        <div>
                            <h1 className="font-bold text-sm tracking-tight">HyperOS Agent</h1>
                            <p className="text-[9px] text-white/40 font-bold uppercase tracking-widest">Autonomous Engine</p>
                        </div>
                    </div>
                </div>

                {/* Progress Content */}
                <div
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto p-5 space-y-6 scrollbar-hide"
                >
                    {history.length === 0 && !isProcessing && (
                        <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                            <Command className="w-12 h-12 text-[#0080FF] mb-2" />
                            <h2 className="text-lg font-medium">Ready for Task</h2>
                            <p className="text-xs max-w-[200px] mx-auto leading-relaxed">I will analyze your screen and perform actions automatically.</p>
                        </div>
                    )}

                    {history.map((step, i) => (
                        <div key={i} className="space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-black text-white/20 uppercase tracking-widest">Step {step.step}</span>
                                <div className="h-px flex-1 bg-white/5" />
                            </div>

                            {/* Analysis */}
                            <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                                <div className="flex items-center gap-2 mb-2 text-[9px] font-bold text-[#0080FF] uppercase tracking-[0.2em]">
                                    <Layout className="w-3 h-3" />
                                    <span>Analyze</span>
                                </div>
                                <p className="text-xs text-white/70 leading-relaxed font-medium">{step.analysis}</p>
                            </div>

                            {/* Plan + Action */}
                            <div className="bg-[#0080FF]/10 rounded-2xl p-4 border border-[#0080FF]/20">
                                <div className="flex items-center gap-2 mb-2 text-[9px] font-bold text-[#0080FF] uppercase tracking-[0.2em]">
                                    <Target className="w-3 h-3" />
                                    <span>Action</span>
                                </div>
                                <p className="text-xs text-white/90 mb-3 font-semibold leading-relaxed">"{step.action.reasoning}"</p>
                                <div className="flex items-center gap-3 p-2.5 bg-black/40 rounded-xl border border-white/5 group transition-all hover:border-[#0080FF]/30">
                                    <div className="p-1.5 rounded-lg bg-[#0080FF]/20 text-[#0080FF]">
                                        <MousePointer2 className="w-3.5 h-3.5" />
                                    </div>
                                    <span className="text-[10px] font-mono text-white/60 group-hover:text-white/90 transition-colors">
                                        {step.action.type.toUpperCase()}(
                                        {step.action.target || step.action.key || step.action.coords_1000?.join(', ')}
                                        )
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}

                    {currentStepInfo && (
                        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-4 animate-pulse">
                            <div className={`p-2 rounded-xl ${currentStepInfo.phase === 'analyze' ? 'bg-[#0080FF]/20 text-[#0080FF]' :
                                currentStepInfo.phase === 'plan' ? 'bg-purple-500/20 text-purple-500' :
                                    currentStepInfo.phase === 'execute' ? 'bg-green-500/20 text-green-500' :
                                        'bg-orange-500/20 text-orange-500'
                                }`}>
                                <Activity className="w-4 h-4 animate-spin" />
                            </div>
                            <div className="flex flex-col gap-0.5">
                                <span className="text-[9px] font-black uppercase tracking-widest opacity-40">{currentStepInfo.phase}</span>
                                <span className="text-xs font-semibold text-white/80">{currentStepInfo.message}</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-6 bg-black/40 border-t border-white/5">
                    <div className="relative group">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleCommand()}
                            placeholder="Enter task (e.g. Open Notepad)"
                            className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-14 py-4 text-sm text-white placeholder-white/20 focus:outline-none focus:border-[#0080FF]/50 focus:ring-4 focus:ring-[#0080FF]/10 transition-all pointer-events-auto"
                            disabled={isProcessing}
                        />
                        <Command className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20" />
                        <button
                            onClick={handleCommand}
                            disabled={isProcessing}
                            className={`absolute right-2 top-1/2 -translate-y-1/2 p-2.5 rounded-xl transition-all pointer-events-auto ${isProcessing
                                ? 'bg-white/5 text-white/20'
                                : 'bg-[#0080FF] text-white hover:bg-[#0080FF]/80 shadow-[0_0_15px_rgba(0,128,255,0.4)] hover:scale-105 active:scale-95'
                                }`}
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                    <div className="mt-4 flex justify-between items-center px-2 opacity-30">
                        <p className="text-[9px] font-bold uppercase tracking-widest">Mistral Engine</p>
                        <div className="flex gap-1">
                            <div className="w-1.5 h-1.5 rounded-full bg-white" />
                            <div className="w-1.5 h-1.5 rounded-full bg-white/50" />
                            <div className="w-1.5 h-1.5 rounded-full bg-white/20" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default App
