import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

interface LogEntry {
    id: string;
    timestamp: number;
    level: 'info' | 'warn' | 'error' | 'debug' | 'consciousness';
    message: string;
    source: string;
    data?: any;
}

interface MemoryDelta {
    address: string;
    before: any;
    after: any;
    operation: 'read' | 'write' | 'allocate' | 'deallocate';
    timestamp: number;
    size?: number;
}

interface ScriptIOPanelProps {
    isExecuting: boolean;
    script: string;
    onInput?: (input: string) => void;
}

export function ScriptIOPanel({ isExecuting, script, onInput }: ScriptIOPanelProps) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [memoryDeltas, setMemoryDeltas] = useState<MemoryDelta[]>([]);
    const [activeTab, setActiveTab] = useState<'logs' | 'memory' | 'variables'>('logs');
    const [filter, setFilter] = useState<'all' | 'info' | 'warn' | 'error' | 'consciousness'>('all');
    const [autoScroll, setAutoScroll] = useState(true);
    const [variables, setVariables] = useState<Record<string, any>>({});
    const logsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isExecuting) {
            simulateExecution();
        }
    }, [isExecuting, script]);

    useEffect(() => {
        if (autoScroll && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, autoScroll]);

    const simulateExecution = async () => {
        // Clear previous execution data
        setLogs([]);
        setMemoryDeltas([]);
        setVariables({});

        const scriptLines = script.split('\n').filter(line => line.trim() && !line.trim().startsWith('//'));

        for (let i = 0; i < scriptLines.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));

            const line = scriptLines[i].trim();
            processScriptLine(line, i + 1);
        }

        // Add final log
        addLog('info', 'Script execution completed', 'AetherScript Runtime');
    };

    const processScriptLine = (line: string, lineNumber: number) => {
        // Simulate different types of operations based on script content

        if (line.includes('consciousness.initialize()')) {
            addLog('consciousness', 'Initializing consciousness framework...', 'Consciousness Core');
            addMemoryDelta('0x7ffd1a2b3000', null, { status: 'initialized', pathways: 0 }, 'allocate', 2048);
            setVariables(prev => ({ ...prev, consciousness_state: 'initialized' }));

            setTimeout(() => {
                addLog('info', 'Consciousness framework initialized successfully', 'Consciousness Core');
                addLog('debug', `Neural pathway allocation: 2048 bytes at 0x7ffd1a2b3000`, 'Memory Manager');
            }, 100);
        }

        else if (line.includes('memory.load(')) {
            const match = line.match(/memory\.load\(['"]([^'"]*)['"]\)/);
            const dataType = match ? match[1] : 'unknown';

            addLog('info', `Loading memory data: ${dataType}`, 'Memory Manager');
            addMemoryDelta('0x7ffd2c3d4000', null, { type: dataType, loaded: true }, 'allocate', 4096);
            setVariables(prev => ({ ...prev, [dataType]: 'loaded' }));

            setTimeout(() => {
                addLog('info', `Memory data loaded successfully: ${dataType}`, 'Memory Manager');
                addLog('debug', `Memory allocation: 4096 bytes for ${dataType}`, 'Memory Manager');
            }, 150);
        }

        else if (line.includes('pathway')) {
            const match = line.match(/pathway\s+(\w+)/);
            const pathwayName = match ? match[1] : 'unnamed_pathway';

            addLog('consciousness', `Creating neural pathway: ${pathwayName}`, 'Neural Engine');
            addMemoryDelta('0x7ffd3d4e5000', null, { name: pathwayName, connections: 0 }, 'allocate', 1024);
            setVariables(prev => ({ ...prev, [`pathway_${pathwayName}`]: 'created' }));

            setTimeout(() => {
                addLog('info', `Neural pathway created: ${pathwayName}`, 'Neural Engine');
                addLog('debug', `Pathway memory allocated: 1024 bytes`, 'Memory Manager');
            }, 200);
        }

        else if (line.includes('loop {')) {
            addLog('consciousness', 'Starting main consciousness loop', 'Loop Controller');
            setVariables(prev => ({ ...prev, main_loop: 'active', loop_iterations: 0 }));

            // Simulate loop iterations
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    addLog('debug', `Loop iteration ${i + 1}`, 'Loop Controller');
                    setVariables(prev => ({ ...prev, loop_iterations: i + 1 }));
                }, 300 * (i + 1));
            }
        }

        else if (line.includes('sense()')) {
            addLog('info', 'Gathering sensory input...', 'Sensory System');
            const sensorData = { visual: 847, auditory: 234, tactile: 156 };
            addMemoryDelta('0x7ffd4e5f6000', null, sensorData, 'write', 512);
            setVariables(prev => ({ ...prev, sensory_data: sensorData }));

            setTimeout(() => {
                addLog('info', `Sensory data collected: ${Object.values(sensorData).reduce((a, b) => a + b, 0)} data points`, 'Sensory System');
            }, 100);
        }

        else if (line.includes('think(') || line.includes('process(')) {
            addLog('consciousness', 'Processing thoughts...', 'Thought Processor');
            addMemoryDelta('0x7ffd5f607000', null, { thoughts: 12, complexity: 'high' }, 'write', 2048);
            setVariables(prev => ({ ...prev, thought_process: 'active', thoughts_generated: 12 }));

            setTimeout(() => {
                addLog('info', 'Thought processing complete: 12 thoughts generated', 'Thought Processor');
                addLog('debug', 'Memory usage: 2048 bytes for thought storage', 'Memory Manager');
            }, 250);
        }

        else if (line.includes('learn(')) {
            addLog('consciousness', 'Learning from experience...', 'Learning Engine');
            addMemoryDelta('0x7ffd60718000', { patterns: 42 }, { patterns: 67 }, 'write', 0);
            setVariables(prev => ({ ...prev, learned_patterns: 67, learning_rate: 0.85 }));

            setTimeout(() => {
                addLog('info', 'Learning complete: 25 new patterns acquired', 'Learning Engine');
                addLog('debug', 'Pattern database updated: 42 -> 67 patterns', 'Memory Manager');
            }, 180);
        }

        else if (line.includes('plugins.')) {
            const match = line.match(/plugins\.(\w+)\(['"]?([^'"]*?)['"]?\)/);
            const action = match ? match[1] : 'unknown';
            const pluginName = match ? match[2] : 'unknown';

            addLog('info', `Plugin ${action}: ${pluginName}`, 'Plugin Manager');
            setVariables(prev => ({ ...prev, [`plugin_${pluginName}`]: action }));

            if (action === 'activate') {
                addMemoryDelta('0x7ffd70829000', null, { plugin: pluginName, status: 'active' }, 'allocate', 1536);
                setTimeout(() => {
                    addLog('info', `Plugin activated successfully: ${pluginName}`, 'Plugin Manager');
                }, 120);
            }
        }

        else if (line.includes('console.log')) {
            const match = line.match(/console\.log\(['"]([^'"]*)['"]\)/);
            const message = match ? match[1] : line;
            addLog('info', message, 'Console');
        }

        else if (line.includes('evolve()')) {
            addLog('consciousness', 'Evolving consciousness patterns...', 'Evolution Engine');
            addMemoryDelta('0x7ffd8093a000', { evolution_level: 1 }, { evolution_level: 2 }, 'write', 0);
            setVariables(prev => ({ ...prev, evolution_level: 2, adaptations: 15 }));

            setTimeout(() => {
                addLog('info', 'Evolution cycle complete: Level 2 achieved', 'Evolution Engine');
                addLog('debug', '15 new adaptations integrated', 'Evolution Engine');
            }, 300);
        }

        else {
            // Generic processing for unknown lines
            addLog('debug', `Executing: ${line}`, `Line ${lineNumber}`);
        }
    };

    const addLog = (level: LogEntry['level'], message: string, source: string, data?: any) => {
        const newLog: LogEntry = {
            id: `log-${Date.now()}-${Math.random()}`,
            timestamp: Date.now(),
            level,
            message,
            source,
            data
        };

        setLogs(prev => [...prev, newLog]);
    };

    const addMemoryDelta = (address: string, before: any, after: any, operation: MemoryDelta['operation'], size?: number) => {
        const delta: MemoryDelta = {
            address,
            before,
            after,
            operation,
            timestamp: Date.now(),
            size
        };

        setMemoryDeltas(prev => [...prev, delta]);
    };

    const filteredLogs = logs.filter(log => filter === 'all' || log.level === filter);

    const getLevelIcon = (level: LogEntry['level']) => {
        switch (level) {
            case 'info': return 'ℹ️';
            case 'warn': return '⚠️';
            case 'error': return '❌';
            case 'debug': return '🔍';
            case 'consciousness': return '🧠';
            default: return '•';
        }
    };

    const getLevelColor = (level: LogEntry['level']) => {
        switch (level) {
            case 'info': return 'text-blue-400';
            case 'warn': return 'text-yellow-400';
            case 'error': return 'text-red-400';
            case 'debug': return 'text-gray-400';
            case 'consciousness': return 'text-purple-400';
            default: return 'text-gray-400';
        }
    };

    const getOperationColor = (operation: MemoryDelta['operation']) => {
        switch (operation) {
            case 'read': return 'text-blue-400';
            case 'write': return 'text-green-400';
            case 'allocate': return 'text-purple-400';
            case 'deallocate': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    const formatBytes = (bytes?: number) => {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center justify-between">
                    <div className="flex space-x-1">
                        {['logs', 'memory', 'variables'].map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab as any)}
                                className={`px-3 py-1 rounded text-sm transition-colors ${activeTab === tab
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                                    }`}
                            >
                                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center space-x-2">
                        {activeTab === 'logs' && (
                            <>
                                <select
                                    value={filter}
                                    onChange={(e) => setFilter(e.target.value as any)}
                                    className="bg-gray-700 text-white px-2 py-1 rounded text-xs border border-gray-600"
                                >
                                    <option value="all">All</option>
                                    <option value="info">Info</option>
                                    <option value="warn">Warnings</option>
                                    <option value="error">Errors</option>
                                    <option value="debug">Debug</option>
                                    <option value="consciousness">Consciousness</option>
                                </select>
                                <button
                                    onClick={() => setAutoScroll(!autoScroll)}
                                    className={`px-2 py-1 rounded text-xs transition-colors ${autoScroll
                                            ? 'bg-green-600 text-white'
                                            : 'bg-gray-600 text-gray-300'
                                        }`}
                                >
                                    Auto-scroll
                                </button>
                            </>
                        )}

                        <button
                            onClick={() => {
                                setLogs([]);
                                setMemoryDeltas([]);
                                setVariables({});
                            }}
                            className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="h-80 overflow-hidden">
                {activeTab === 'logs' && (
                    <div className="h-full overflow-y-auto p-4 space-y-2 font-mono text-sm">
                        <AnimatePresence>
                            {filteredLogs.map((log, index) => (
                                <motion.div
                                    key={log.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.02 }}
                                    className="flex items-start space-x-2 py-1"
                                >
                                    <span className="text-xs text-gray-500 w-16 flex-shrink-0">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </span>
                                    <span className="text-sm">{getLevelIcon(log.level)}</span>
                                    <span className={`text-xs w-20 flex-shrink-0 ${getLevelColor(log.level)}`}>
                                        {log.level.toUpperCase()}
                                    </span>
                                    <span className="text-xs text-gray-400 w-32 flex-shrink-0 truncate">
                                        {log.source}
                                    </span>
                                    <span className="text-gray-300 flex-1">{log.message}</span>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        <div ref={logsEndRef} />
                    </div>
                )}

                {activeTab === 'memory' && (
                    <div className="h-full overflow-y-auto p-4 space-y-2 font-mono text-sm">
                        <AnimatePresence>
                            {memoryDeltas.map((delta, index) => (
                                <motion.div
                                    key={`${delta.address}-${delta.timestamp}`}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.03 }}
                                    className="border border-gray-700 rounded p-3"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-green-400 font-mono">{delta.address}</span>
                                        <div className="flex items-center space-x-2">
                                            <span className={`text-xs px-2 py-1 rounded ${getOperationColor(delta.operation)}`}>
                                                {delta.operation.toUpperCase()}
                                            </span>
                                            {delta.size && (
                                                <span className="text-xs text-gray-400">{formatBytes(delta.size)}</span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 text-xs">
                                        <div>
                                            <div className="text-gray-400 mb-1">Before:</div>
                                            <div className="bg-black rounded p-2 text-red-300">
                                                {delta.before ? JSON.stringify(delta.before, null, 2) : 'null'}
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-gray-400 mb-1">After:</div>
                                            <div className="bg-black rounded p-2 text-green-300">
                                                {JSON.stringify(delta.after, null, 2)}
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}

                {activeTab === 'variables' && (
                    <div className="h-full overflow-y-auto p-4 space-y-2">
                        <AnimatePresence>
                            {Object.entries(variables).map(([name, value], index) => (
                                <motion.div
                                    key={name}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className="flex items-center justify-between p-3 border border-gray-700 rounded"
                                >
                                    <span className="text-blue-400 font-mono">{name}</span>
                                    <span className="text-gray-300 font-mono text-sm">
                                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                    </span>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {Object.keys(variables).length === 0 && (
                            <div className="text-center text-gray-500 py-8">
                                <div className="text-2xl mb-2">📊</div>
                                <div>No variables defined yet</div>
                                <div className="text-sm">Variables will appear here during script execution</div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
