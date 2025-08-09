import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface ExecutionRecord {
    id: string;
    timestamp: number;
    script: string;
    duration: number;
    status: 'success' | 'error' | 'warning';
    output: string;
    memoryUsage: number;
    cpuUsage: number;
    linesExecuted: number;
    errors?: string[];
    summary: string;
}

interface ExecutionHistoryPanelProps {
    onLoadScript: (script: string) => void;
    onClearHistory: () => void;
    currentExecution?: ExecutionRecord;
}

export function ExecutionHistoryPanel({
    onLoadScript,
    onClearHistory,
    currentExecution
}: ExecutionHistoryPanelProps) {
    const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
    const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
    const [filter, setFilter] = useState<'all' | 'success' | 'error' | 'warning'>('all');
    const [sortBy, setSortBy] = useState<'timestamp' | 'duration' | 'status'>('timestamp');

    useEffect(() => {
        // Initialize with sample execution history
        const sampleExecutions: ExecutionRecord[] = [
            {
                id: 'exec-1',
                timestamp: Date.now() - 300000, // 5 minutes ago
                script: 'consciousness.initialize()\nmemory.load("neural_patterns")\nloop {\n  sense()\n  think()\n  learn()\n}',
                duration: 2.34,
                status: 'success',
                output: 'Consciousness initialized successfully\nNeural patterns loaded\nMain loop active',
                memoryUsage: 45.7,
                cpuUsage: 23.1,
                linesExecuted: 8,
                summary: 'Basic consciousness initialization with main processing loop'
            },
            {
                id: 'exec-2',
                timestamp: Date.now() - 240000, // 4 minutes ago
                script: 'pathway pattern_recognizer {\n  input: sensory_data\n  process: neural_analysis\n}\npattern_recognizer.activate()',
                duration: 1.87,
                status: 'warning',
                output: 'Pathway created with warnings\nActivation successful with reduced efficiency',
                memoryUsage: 62.3,
                cpuUsage: 34.5,
                linesExecuted: 5,
                errors: ['Pathway input validation warning: sensory_data format'],
                summary: 'Pattern recognition pathway with input format warnings'
            },
            {
                id: 'exec-3',
                timestamp: Date.now() - 180000, // 3 minutes ago
                script: 'neural network deep_learner {\n  layers: [256, 128, 64]\n  activation: invalid_function\n}',
                duration: 0.45,
                status: 'error',
                output: 'Error: Unknown activation function "invalid_function"',
                memoryUsage: 12.1,
                cpuUsage: 8.7,
                linesExecuted: 2,
                errors: ['Syntax error: invalid_function is not a valid activation function'],
                summary: 'Failed neural network creation due to invalid activation function'
            },
            {
                id: 'exec-4',
                timestamp: Date.now() - 120000, // 2 minutes ago
                script: 'memory.optimize()\nplugins.chain(["consciousness_core", "memory_manager"])\nconsole.log("System optimized")',
                duration: 3.12,
                status: 'success',
                output: 'Memory optimization complete\nPlugin chain established\nSystem optimized',
                memoryUsage: 38.9,
                cpuUsage: 45.2,
                linesExecuted: 3,
                summary: 'Memory optimization and plugin chain configuration'
            },
            {
                id: 'exec-5',
                timestamp: Date.now() - 60000, // 1 minute ago
                script: 'consciousness.evolve()\nneural.train(pattern_data)\nmemory.store("learned_patterns", results)',
                duration: 4.67,
                status: 'success',
                output: 'Consciousness evolution cycle complete\nNeural training finished\nPatterns stored successfully',
                memoryUsage: 89.4,
                cpuUsage: 67.8,
                linesExecuted: 3,
                summary: 'Advanced consciousness evolution with neural training'
            }
        ];

        setExecutions(sampleExecutions);
    }, []);

    useEffect(() => {
        if (currentExecution) {
            setExecutions(prev => [currentExecution, ...prev.slice(0, 19)]); // Keep last 20
        }
    }, [currentExecution]);

    const filteredExecutions = executions.filter(exec =>
        filter === 'all' || exec.status === filter
    );

    const sortedExecutions = [...filteredExecutions].sort((a, b) => {
        switch (sortBy) {
            case 'timestamp':
                return b.timestamp - a.timestamp;
            case 'duration':
                return b.duration - a.duration;
            case 'status':
                return a.status.localeCompare(b.status);
            default:
                return b.timestamp - a.timestamp;
        }
    });

    const getStatusIcon = (status: ExecutionRecord['status']) => {
        switch (status) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            default: return '•';
        }
    };

    const getStatusColor = (status: ExecutionRecord['status']) => {
        switch (status) {
            case 'success': return 'text-green-400';
            case 'error': return 'text-red-400';
            case 'warning': return 'text-yellow-400';
            default: return 'text-gray-400';
        }
    };

    const formatDuration = (duration: number) => {
        if (duration < 1) return `${Math.round(duration * 1000)}ms`;
        return `${duration.toFixed(2)}s`;
    };

    const formatTimestamp = (timestamp: number) => {
        const now = Date.now();
        const diff = now - timestamp;

        if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return new Date(timestamp).toLocaleDateString();
    };

    return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">Execution History</h3>
                    <div className="flex items-center space-x-2">
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value as any)}
                            className="bg-gray-700 text-white px-2 py-1 rounded text-sm border border-gray-600"
                        >
                            <option value="all">All</option>
                            <option value="success">Success</option>
                            <option value="error">Errors</option>
                            <option value="warning">Warnings</option>
                        </select>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as any)}
                            className="bg-gray-700 text-white px-2 py-1 rounded text-sm border border-gray-600"
                        >
                            <option value="timestamp">Recent</option>
                            <option value="duration">Duration</option>
                            <option value="status">Status</option>
                        </select>
                        <button
                            onClick={onClearHistory}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            </div>

            {/* Stats Bar */}
            <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
                <div className="grid grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                        <div className="text-white font-semibold">{executions.length}</div>
                        <div className="text-gray-400">Total</div>
                    </div>
                    <div className="text-center">
                        <div className="text-green-400 font-semibold">
                            {executions.filter(e => e.status === 'success').length}
                        </div>
                        <div className="text-gray-400">Success</div>
                    </div>
                    <div className="text-center">
                        <div className="text-red-400 font-semibold">
                            {executions.filter(e => e.status === 'error').length}
                        </div>
                        <div className="text-gray-400">Errors</div>
                    </div>
                    <div className="text-center">
                        <div className="text-yellow-400 font-semibold">
                            {executions.filter(e => e.status === 'warning').length}
                        </div>
                        <div className="text-gray-400">Warnings</div>
                    </div>
                </div>
            </div>

            {/* Execution List */}
            <div className="max-h-96 overflow-y-auto">
                <AnimatePresence>
                    {sortedExecutions.length > 0 ? (
                        sortedExecutions.map((execution, index) => (
                            <motion.div
                                key={execution.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ delay: index * 0.05 }}
                                className={`border-b border-gray-700 cursor-pointer transition-colors ${selectedExecution === execution.id
                                        ? 'bg-blue-500/20 border-blue-500'
                                        : 'hover:bg-gray-800'
                                    }`}
                                onClick={() => setSelectedExecution(
                                    selectedExecution === execution.id ? null : execution.id
                                )}
                            >
                                <div className="p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center space-x-2">
                                            <span className="text-lg">{getStatusIcon(execution.status)}</span>
                                            <span className={`text-sm font-medium ${getStatusColor(execution.status)}`}>
                                                {execution.status.toUpperCase()}
                                            </span>
                                            <span className="text-xs text-gray-400">
                                                {formatTimestamp(execution.timestamp)}
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-4 text-xs text-gray-400">
                                            <span>{formatDuration(execution.duration)}</span>
                                            <span>{execution.linesExecuted} lines</span>
                                            <span>{execution.memoryUsage.toFixed(1)}MB</span>
                                        </div>
                                    </div>

                                    <div className="text-sm text-gray-300 mb-2">
                                        {execution.summary}
                                    </div>

                                    {execution.errors && execution.errors.length > 0 && (
                                        <div className="text-xs text-red-400 mb-2">
                                            {execution.errors[0]}
                                        </div>
                                    )}

                                    <div className="flex items-center justify-between">
                                        <div className="flex space-x-2">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onLoadScript(execution.script);
                                                }}
                                                className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition-colors"
                                            >
                                                Load Script
                                            </button>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigator.clipboard.writeText(execution.script);
                                                }}
                                                className="px-2 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-xs transition-colors"
                                            >
                                                Copy
                                            </button>
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            ID: {execution.id}
                                        </div>
                                    </div>
                                </div>

                                {/* Expanded Details */}
                                <AnimatePresence>
                                    {selectedExecution === execution.id && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{ duration: 0.2 }}
                                            className="border-t border-gray-600 bg-gray-800/50"
                                        >
                                            <div className="p-4 space-y-3">
                                                <div>
                                                    <h5 className="text-sm font-medium text-white mb-2">Script Code</h5>
                                                    <pre className="bg-black rounded p-2 text-xs text-green-400 font-mono overflow-x-auto">
                                                        {execution.script}
                                                    </pre>
                                                </div>

                                                <div>
                                                    <h5 className="text-sm font-medium text-white mb-2">Output</h5>
                                                    <pre className="bg-black rounded p-2 text-xs text-gray-300 font-mono whitespace-pre-wrap">
                                                        {execution.output}
                                                    </pre>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <h5 className="text-sm font-medium text-white mb-2">Performance</h5>
                                                        <div className="space-y-1 text-xs">
                                                            <div className="flex justify-between">
                                                                <span className="text-gray-400">Duration:</span>
                                                                <span className="text-white">{formatDuration(execution.duration)}</span>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span className="text-gray-400">Memory:</span>
                                                                <span className="text-white">{execution.memoryUsage.toFixed(1)}MB</span>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span className="text-gray-400">CPU:</span>
                                                                <span className="text-white">{execution.cpuUsage.toFixed(1)}%</span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {execution.errors && execution.errors.length > 0 && (
                                                        <div>
                                                            <h5 className="text-sm font-medium text-white mb-2">Errors</h5>
                                                            <div className="space-y-1">
                                                                {execution.errors.map((error, idx) => (
                                                                    <div key={idx} className="text-xs text-red-400">
                                                                        {error}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        ))
                    ) : (
                        <div className="p-8 text-center text-gray-500">
                            <div className="text-4xl mb-4">📋</div>
                            <div className="text-lg font-medium mb-2">No execution history</div>
                            <div className="text-sm">Run some AetherScript to see execution history here</div>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
