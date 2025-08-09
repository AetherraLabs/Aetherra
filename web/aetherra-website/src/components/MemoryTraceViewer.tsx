import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface MemoryTrace {
    id: string;
    type: 'allocation' | 'deallocation' | 'access' | 'modification';
    timestamp: number;
    address: string;
    size: number;
    plugin: string;
    operation: string;
    stackTrace: string[];
    data?: any;
}

interface MemoryRegion {
    id: string;
    start: string;
    end: string;
    size: number;
    type: 'heap' | 'stack' | 'neural' | 'cache';
    usage: number;
    plugin: string;
}

export function MemoryTraceViewer() {
    const [traces, setTraces] = useState<MemoryTrace[]>([]);
    const [regions, setRegions] = useState<MemoryRegion[]>([]);
    const [selectedTrace, setSelectedTrace] = useState<string | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [filter, setFilter] = useState<'all' | 'allocation' | 'access' | 'modification'>('all');

    useEffect(() => {
        // Initialize with sample memory data
        const sampleTraces: MemoryTrace[] = [
            {
                id: 'trace-1',
                type: 'allocation',
                timestamp: Date.now() - 5000,
                address: '0x7ffd1a2b3c4d',
                size: 1024,
                plugin: 'consciousness-core',
                operation: 'neural_pathway_init',
                stackTrace: ['consciousness_init()', 'pathway_allocate()', 'memory_alloc()'],
                data: { patterns: 42, connections: 128 }
            },
            {
                id: 'trace-2',
                type: 'access',
                timestamp: Date.now() - 4500,
                address: '0x7ffd1a2b3c4d',
                size: 256,
                plugin: 'memory-manager',
                operation: 'pattern_lookup',
                stackTrace: ['memory_recall()', 'pattern_search()', 'memory_access()'],
                data: { hit: true, latency: 12 }
            },
            {
                id: 'trace-3',
                type: 'modification',
                timestamp: Date.now() - 4000,
                address: '0x7ffd1a2b3c4d',
                size: 512,
                plugin: 'pattern-learner',
                operation: 'pattern_update',
                stackTrace: ['learn_pattern()', 'update_weights()', 'memory_write()'],
                data: { confidence: 0.87, delta: 0.23 }
            },
            {
                id: 'trace-4',
                type: 'allocation',
                timestamp: Date.now() - 3500,
                address: '0x7ffd2b3c4d5e',
                size: 2048,
                plugin: 'thought-synthesizer',
                operation: 'thought_buffer_alloc',
                stackTrace: ['synthesize_thought()', 'buffer_allocate()', 'memory_alloc()'],
                data: { thoughts: 8, complexity: 'high' }
            },
            {
                id: 'trace-5',
                type: 'deallocation',
                timestamp: Date.now() - 3000,
                address: '0x7ffd0a1b2c3d',
                size: 768,
                plugin: 'consciousness-core',
                operation: 'temp_pattern_cleanup',
                stackTrace: ['cleanup_temp()', 'pattern_free()', 'memory_free()'],
                data: { freed_patterns: 15 }
            }
        ];

        const sampleRegions: MemoryRegion[] = [
            {
                id: 'region-1',
                start: '0x7ffd00000000',
                end: '0x7ffd0fffffff',
                size: 268435456, // 256MB
                type: 'neural',
                usage: 65.4,
                plugin: 'consciousness-core'
            },
            {
                id: 'region-2',
                start: '0x7ffd10000000',
                end: '0x7ffd1fffffff',
                size: 134217728, // 128MB
                type: 'heap',
                usage: 42.8,
                plugin: 'memory-manager'
            },
            {
                id: 'region-3',
                start: '0x7ffd20000000',
                end: '0x7ffd2fffffff',
                size: 67108864, // 64MB
                type: 'cache',
                usage: 78.9,
                plugin: 'pattern-learner'
            },
            {
                id: 'region-4',
                start: '0x7ffd30000000',
                end: '0x7ffd3fffffff',
                size: 33554432, // 32MB
                type: 'stack',
                usage: 23.1,
                plugin: 'thought-synthesizer'
            }
        ];

        setTraces(sampleTraces);
        setRegions(sampleRegions);
    }, []);

    useEffect(() => {
        if (isRecording) {
            const interval = setInterval(() => {
                // Simulate new memory traces
                const operations = ['allocation', 'access', 'modification', 'deallocation'] as const;
                const plugins = ['consciousness-core', 'memory-manager', 'pattern-learner', 'thought-synthesizer'];

                const newTrace: MemoryTrace = {
                    id: `trace-${Date.now()}`,
                    type: operations[Math.floor(Math.random() * operations.length)],
                    timestamp: Date.now(),
                    address: `0x7ffd${Math.floor(Math.random() * 0xffffffff).toString(16).padStart(8, '0')}`,
                    size: Math.floor(Math.random() * 2048) + 64,
                    plugin: plugins[Math.floor(Math.random() * plugins.length)],
                    operation: 'runtime_operation',
                    stackTrace: ['runtime()', 'execute()', 'memory_op()'],
                    data: { runtime: true }
                };

                setTraces(prev => [newTrace, ...prev.slice(0, 19)]); // Keep last 20 traces

                // Update region usage
                setRegions(prev => prev.map(region => ({
                    ...region,
                    usage: Math.max(0, Math.min(100, region.usage + (Math.random() - 0.5) * 10))
                })));
            }, 2000);

            return () => clearInterval(interval);
        }
    }, [isRecording]);

    const getTypeColor = (type: MemoryTrace['type']) => {
        switch (type) {
            case 'allocation': return 'text-green-400';
            case 'deallocation': return 'text-red-400';
            case 'access': return 'text-blue-400';
            case 'modification': return 'text-yellow-400';
            default: return 'text-gray-400';
        }
    };

    const getTypeIcon = (type: MemoryTrace['type']) => {
        switch (type) {
            case 'allocation': return '📦';
            case 'deallocation': return '🗑️';
            case 'access': return '👁️';
            case 'modification': return '✏️';
            default: return '•';
        }
    };

    const getRegionColor = (type: MemoryRegion['type']) => {
        switch (type) {
            case 'neural': return 'bg-purple-600';
            case 'heap': return 'bg-blue-600';
            case 'cache': return 'bg-green-600';
            case 'stack': return 'bg-orange-600';
            default: return 'bg-gray-600';
        }
    };

    const formatBytes = (bytes: number) => {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    };

    const filteredTraces = traces.filter(trace =>
        filter === 'all' || trace.type === filter
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Memory Trace Viewer</h2>
                <div className="flex items-center space-x-4">
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value as any)}
                        className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                    >
                        <option value="all">All Operations</option>
                        <option value="allocation">Allocations</option>
                        <option value="access">Access</option>
                        <option value="modification">Modifications</option>
                    </select>
                    <button
                        onClick={() => setIsRecording(!isRecording)}
                        className={`px-4 py-2 rounded transition-colors ${isRecording
                                ? 'bg-red-600 hover:bg-red-700'
                                : 'bg-green-600 hover:bg-green-700'
                            } text-white font-semibold`}
                    >
                        {isRecording ? '⏹️ Stop Recording' : '🔴 Start Recording'}
                    </button>
                    <div className="text-sm text-gray-400">
                        {traces.length} total traces
                    </div>
                </div>
            </div>

            {/* Memory Regions */}
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">Memory Regions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {regions.map((region) => (
                        <motion.div
                            key={region.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="p-3 border border-gray-600 rounded-lg"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <div className={`w-3 h-3 rounded-full ${getRegionColor(region.type)}`} />
                                <span className="text-xs text-gray-400">{region.type.toUpperCase()}</span>
                            </div>
                            <div className="text-sm text-white font-medium mb-1">{region.plugin}</div>
                            <div className="text-xs text-gray-400 mb-2">{formatBytes(region.size)}</div>
                            <div className="w-full bg-gray-700 rounded-full h-2 mb-1">
                                <div
                                    className={`h-2 rounded-full transition-all duration-300 ${region.usage > 80 ? 'bg-red-500' :
                                            region.usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                                        }`}
                                    style={{ width: `${region.usage}%` }}
                                />
                            </div>
                            <div className="text-xs text-gray-400">{region.usage.toFixed(1)}% used</div>
                        </motion.div>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Trace List */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Memory Traces</h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {filteredTraces.map((trace) => (
                            <motion.div
                                key={trace.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedTrace === trace.id
                                        ? 'border-blue-500 bg-blue-500/10'
                                        : 'border-gray-600 hover:border-gray-500'
                                    }`}
                                onClick={() => setSelectedTrace(trace.id)}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-lg">{getTypeIcon(trace.type)}</span>
                                        <div>
                                            <div className={`text-sm font-medium ${getTypeColor(trace.type)}`}>
                                                {trace.type.toUpperCase()}
                                            </div>
                                            <div className="text-xs text-gray-400">{trace.operation}</div>
                                        </div>
                                    </div>
                                    <div className="text-right text-xs">
                                        <div className="text-white">{formatBytes(trace.size)}</div>
                                        <div className="text-gray-400">
                                            {new Date(trace.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                </div>
                                <div className="mt-2 text-xs">
                                    <span className="text-gray-400">Plugin:</span>
                                    <span className="ml-1 text-white">{trace.plugin}</span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Trace Details */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Trace Details</h3>
                    {selectedTrace ? (
                        <div className="space-y-4">
                            {(() => {
                                const trace = traces.find(t => t.id === selectedTrace);
                                if (!trace) return null;

                                return (
                                    <>
                                        <div>
                                            <h4 className="font-medium text-white mb-2 flex items-center space-x-2">
                                                <span>{getTypeIcon(trace.type)}</span>
                                                <span>{trace.type.toUpperCase()}</span>
                                            </h4>
                                            <div className="text-sm text-gray-400 space-y-1">
                                                <div>Operation: <span className="text-white">{trace.operation}</span></div>
                                                <div>Plugin: <span className="text-white">{trace.plugin}</span></div>
                                                <div>Address: <span className="text-green-400 font-mono">{trace.address}</span></div>
                                                <div>Size: <span className="text-white">{formatBytes(trace.size)}</span></div>
                                                <div>Time: <span className="text-white">{new Date(trace.timestamp).toLocaleString()}</span></div>
                                            </div>
                                        </div>

                                        <div>
                                            <h5 className="font-medium text-white mb-2">Stack Trace</h5>
                                            <div className="bg-black rounded p-3 font-mono text-sm">
                                                {trace.stackTrace.map((frame, index) => (
                                                    <div key={index} className="text-gray-300">
                                                        <span className="text-gray-500">#{index}</span> {frame}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {trace.data && (
                                            <div>
                                                <h5 className="font-medium text-white mb-2">Additional Data</h5>
                                                <div className="bg-black rounded p-3 font-mono text-sm">
                                                    <pre className="text-green-400 whitespace-pre-wrap">
                                                        {JSON.stringify(trace.data, null, 2)}
                                                    </pre>
                                                </div>
                                            </div>
                                        )}

                                        <div>
                                            <h5 className="font-medium text-white mb-2">Memory Layout</h5>
                                            <div className="space-y-2">
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">Start Address:</span>
                                                    <span className="text-green-400 font-mono">{trace.address}</span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">End Address:</span>
                                                    <span className="text-green-400 font-mono">
                                                        0x{(parseInt(trace.address, 16) + trace.size).toString(16)}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">Size:</span>
                                                    <span className="text-white">{trace.size} bytes ({formatBytes(trace.size)})</span>
                                                </div>
                                            </div>
                                        </div>
                                    </>
                                );
                            })()}
                        </div>
                    ) : (
                        <div className="text-gray-500 text-center py-8">
                            Select a trace to view details
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
