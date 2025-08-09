import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

interface ConsoleLine {
    id: string;
    type: 'input' | 'output' | 'error' | 'system';
    content: string;
    timestamp: Date;
}

interface AetherScriptOutput {
    success: boolean;
    result?: any;
    error?: string;
    executionTime?: number;
    memoryUsage?: number;
}

export function LiveAetherConsole() {
    const [lines, setLines] = useState<ConsoleLine[]>([
        {
            id: '1',
            type: 'system',
            content: 'AetherScript Live Console v2.1.0 - Consciousness Development Environment',
            timestamp: new Date()
        },
        {
            id: '2',
            type: 'system',
            content: 'Type "help" for available commands or start writing AetherScript...',
            timestamp: new Date()
        }
    ]);

    const [currentInput, setCurrentInput] = useState('');
    const [history, setHistory] = useState<string[]>([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [isExecuting, setIsExecuting] = useState(false);
    const [autoComplete, setAutoComplete] = useState<string[]>([]);
    const [showAutoComplete, setShowAutoComplete] = useState(false);
    const [cursorVisible, setCursorVisible] = useState(true);

    const inputRef = useRef<HTMLInputElement>(null);
    const consoleRef = useRef<HTMLDivElement>(null);

    // Cursor blinking effect
    useEffect(() => {
        const interval = setInterval(() => {
            setCursorVisible(prev => !prev);
        }, 530);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [lines]);

    // Focus input on mount
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, []);

    const aetherKeywords = [
        'consciousness', 'memory', 'neural', 'pattern', 'learn', 'evolve', 'perceive',
        'think', 'decide', 'feel', 'remember', 'forget', 'associate', 'analyze',
        'synthesize', 'create', 'destroy', 'transform', 'flow', 'state', 'transition',
        'lambda', 'macro', 'define', 'let', 'if', 'then', 'else', 'loop', 'while',
        'for', 'each', 'in', 'return', 'yield', 'await', 'async', 'sync', 'parallel',
        'sequence', 'branch', 'merge', 'split', 'join', 'map', 'filter', 'reduce',
        'collect', 'emit', 'listen', 'observe', 'react', 'respond', 'adapt', 'optimize'
    ];

    const helpCommands = [
        'help - Show this help message',
        'clear - Clear the console',
        'history - Show command history',
        'examples - Load example scripts',
        'save <name> - Save current session',
        'load <name> - Load saved session',
        'export - Export session as .aether file',
        'debug - Toggle debug mode',
        'memory - Show memory usage',
        'performance - Show performance metrics'
    ];

    const executeAetherScript = async (script: string): Promise<AetherScriptOutput> => {
        // Simulate script execution with realistic processing
        await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 800));

        const startTime = performance.now();

        // Handle built-in commands
        if (script.trim() === 'help') {
            return {
                success: true,
                result: helpCommands.join('\n'),
                executionTime: performance.now() - startTime,
                memoryUsage: 1.2
            };
        }

        if (script.trim() === 'clear') {
            setLines([]);
            return {
                success: true,
                result: 'Console cleared',
                executionTime: performance.now() - startTime,
                memoryUsage: 0.1
            };
        }

        if (script.trim() === 'history') {
            return {
                success: true,
                result: history.map((cmd, i) => `${i + 1}: ${cmd}`).join('\n'),
                executionTime: performance.now() - startTime,
                memoryUsage: 0.5
            };
        }

        if (script.trim() === 'examples') {
            const examples = [
                'consciousness.state = "awakening"',
                'memory.store("key", "value")',
                'neural.pattern.learn(input_data)',
                'if consciousness.level > 0.8 then evolve()',
                'lambda x -> x.transform().optimize()'
            ];
            return {
                success: true,
                result: 'Example scripts:\n' + examples.join('\n'),
                executionTime: performance.now() - startTime,
                memoryUsage: 2.1
            };
        }

        if (script.trim() === 'memory') {
            return {
                success: true,
                result: `Memory Usage:
        Heap: 45.2 MB / 128 MB
        Neural Patterns: 12.3 MB
        Consciousness State: 8.7 MB
        Active Processes: 24`,
                executionTime: performance.now() - startTime,
                memoryUsage: 3.4
            };
        }

        // Simulate AetherScript execution
        if (script.includes('consciousness')) {
            return {
                success: true,
                result: `Consciousness state updated: ${Math.random() > 0.5 ? 'elevated' : 'focused'}`,
                executionTime: performance.now() - startTime,
                memoryUsage: Math.random() * 5 + 2
            };
        }

        if (script.includes('memory')) {
            return {
                success: true,
                result: `Memory operation completed: ${Math.floor(Math.random() * 1000)} patterns stored`,
                executionTime: performance.now() - startTime,
                memoryUsage: Math.random() * 3 + 1
            };
        }

        if (script.includes('neural')) {
            return {
                success: true,
                result: `Neural network updated: ${Math.floor(Math.random() * 100)}% efficiency`,
                executionTime: performance.now() - startTime,
                memoryUsage: Math.random() * 4 + 2
            };
        }

        if (script.includes('error') || script.includes('fail')) {
            return {
                success: false,
                error: 'Consciousness safety protocol violation: Potential memory corruption detected',
                executionTime: performance.now() - startTime,
                memoryUsage: 0.2
            };
        }

        // Default execution result
        return {
            success: true,
            result: `Script executed successfully. Result: ${Math.floor(Math.random() * 1000)}`,
            executionTime: performance.now() - startTime,
            memoryUsage: Math.random() * 2 + 0.5
        };
    };

    const addLine = (type: ConsoleLine['type'], content: string) => {
        const newLine: ConsoleLine = {
            id: Date.now().toString(),
            type,
            content,
            timestamp: new Date()
        };
        setLines(prev => [...prev, newLine]);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setCurrentInput(value);

        // Auto-complete suggestions
        if (value.length > 1) {
            const suggestions = aetherKeywords.filter(keyword =>
                keyword.toLowerCase().startsWith(value.toLowerCase())
            );
            setAutoComplete(suggestions.slice(0, 5));
            setShowAutoComplete(suggestions.length > 0);
        } else {
            setShowAutoComplete(false);
        }
    };

    const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !isExecuting) {
            e.preventDefault();

            if (currentInput.trim()) {
                // Add input to console
                addLine('input', `> ${currentInput}`);

                // Add to history
                setHistory(prev => [...prev, currentInput]);
                setHistoryIndex(-1);

                // Execute script
                setIsExecuting(true);
                try {
                    const result = await executeAetherScript(currentInput);

                    if (result.success) {
                        addLine('output', result.result || 'Execution completed');
                        if (result.executionTime && result.memoryUsage) {
                            addLine('system', `⚡ ${result.executionTime.toFixed(2)}ms | 🧠 ${result.memoryUsage.toFixed(1)}MB`);
                        }
                    } else {
                        addLine('error', `Error: ${result.error}`);
                    }
                } catch (error) {
                    addLine('error', `Execution failed: ${error}`);
                }
                setIsExecuting(false);
            }

            setCurrentInput('');
            setShowAutoComplete(false);
        }

        // History navigation
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (historyIndex < history.length - 1) {
                const newIndex = historyIndex + 1;
                setHistoryIndex(newIndex);
                setCurrentInput(history[history.length - 1 - newIndex]);
            }
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                const newIndex = historyIndex - 1;
                setHistoryIndex(newIndex);
                setCurrentInput(history[history.length - 1 - newIndex]);
            } else if (historyIndex === 0) {
                setHistoryIndex(-1);
                setCurrentInput('');
            }
        }

        // Auto-complete selection
        if (e.key === 'Tab' && showAutoComplete && autoComplete.length > 0) {
            e.preventDefault();
            setCurrentInput(autoComplete[0]);
            setShowAutoComplete(false);
        }

        if (e.key === 'Escape') {
            setShowAutoComplete(false);
        }
    };

    const getLineColor = (type: ConsoleLine['type']) => {
        switch (type) {
            case 'input': return 'text-cyan-400';
            case 'output': return 'text-green-400';
            case 'error': return 'text-red-400';
            case 'system': return 'text-yellow-400';
            default: return 'text-gray-300';
        }
    };

    const formatTimestamp = (date: Date) => {
        return date.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <div className="h-full flex flex-col bg-black border border-green-500/30 rounded-lg overflow-hidden font-mono relative">
            {/* Terminal Header */}
            <div className="bg-gray-900 border-b border-green-500/30 px-4 py-2 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-green-400 text-sm ml-4">AetherScript Live Console</span>
                </div>
                <div className="text-green-400 text-xs">
                    {isExecuting ? '🔄 Executing...' : '✓ Ready'}
                </div>
            </div>

            {/* Console Content */}
            <div
                ref={consoleRef}
                className="flex-1 p-4 overflow-y-auto bg-black text-green-400 relative"
                style={{
                    textShadow: '0 0 5px currentColor',
                    background: 'radial-gradient(ellipse at center, rgba(0,255,0,0.03) 0%, rgba(0,0,0,1) 100%)'
                }}
            >
                {/* Scanlines effect */}
                <div
                    className="absolute inset-0 pointer-events-none opacity-20"
                    style={{
                        background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,0,0.1) 2px, rgba(0,255,0,0.1) 4px)'
                    }}
                ></div>

                <AnimatePresence>
                    {lines.map((line, index) => (
                        <motion.div
                            key={line.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.2 }}
                            className={`mb-1 ${getLineColor(line.type)} relative z-10`}
                        >
                            <span className="text-gray-500 text-xs mr-2">
                                [{formatTimestamp(line.timestamp)}]
                            </span>
                            <span className="whitespace-pre-wrap">{line.content}</span>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Input Line */}
                <div className="flex items-center relative z-10">
                    <span className="text-cyan-400 mr-2">
                        [{formatTimestamp(new Date())}] &gt;
                    </span>
                    <div className="flex-1 relative">
                        <input
                            ref={inputRef}
                            type="text"
                            value={currentInput}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            disabled={isExecuting}
                            className="bg-transparent text-cyan-400 border-none outline-none w-full"
                            style={{ textShadow: '0 0 5px currentColor' }}
                            placeholder={isExecuting ? "Executing..." : "Enter AetherScript..."}
                        />
                        <span
                            className={`absolute text-cyan-400 transition-opacity ${cursorVisible ? 'opacity-100' : 'opacity-0'
                                }`}
                            style={{
                                left: `${currentInput.length * 0.6}em`,
                                textShadow: '0 0 5px currentColor'
                            }}
                        >
                            ▌
                        </span>
                    </div>
                </div>

                {/* Auto-complete */}
                <AnimatePresence>
                    {showAutoComplete && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="absolute bottom-16 left-20 bg-gray-900 border border-green-500/50 rounded p-2 z-20"
                        >
                            {autoComplete.map((suggestion, index) => (
                                <div
                                    key={suggestion}
                                    className={`text-green-400 text-sm px-2 py-1 cursor-pointer hover:bg-green-500/20 ${index === 0 ? 'bg-green-500/10' : ''
                                        }`}
                                    onClick={() => {
                                        setCurrentInput(suggestion);
                                        setShowAutoComplete(false);
                                        inputRef.current?.focus();
                                    }}
                                >
                                    {suggestion}
                                </div>
                            ))}
                            <div className="text-gray-500 text-xs mt-1 px-2">
                                Press Tab to accept
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Status Bar */}
            <div className="bg-gray-900 border-t border-green-500/30 px-4 py-1 text-xs text-green-400 flex justify-between">
                <div>Lines: {lines.length} | History: {history.length}</div>
                <div>AetherScript v2.1.0 | Consciousness-Safe</div>
            </div>
        </div>
    );
}
