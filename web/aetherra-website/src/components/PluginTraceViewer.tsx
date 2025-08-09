import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface PluginTrace {
    id: string;
    name: string;
    type: 'consciousness' | 'memory' | 'learning' | 'synthesis';
    status: 'active' | 'inactive' | 'processing' | 'error';
    activationTime: number;
    dependencies: string[];
    outputs: string[];
    performance: {
        cpu: number;
        memory: number;
        latency: number;
    };
}

interface PluginChain {
    id: string;
    plugins: string[];
    data: any;
    timestamp: number;
}

export function PluginTraceViewer() {
    const [plugins, setPlugins] = useState<PluginTrace[]>([]);
    const [chains, setChains] = useState<PluginChain[]>([]);
    const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);
    const [isMonitoring, setIsMonitoring] = useState(false);

    useEffect(() => {
        // Initialize with sample plugin data
        const samplePlugins: PluginTrace[] = [
            {
                id: 'consciousness-core',
                name: 'Consciousness Core',
                type: 'consciousness',
                status: 'active',
                activationTime: Date.now() - 5000,
                dependencies: [],
                outputs: ['thought-stream', 'awareness-level'],
                performance: { cpu: 15.2, memory: 45.8, latency: 12 }
            },
            {
                id: 'memory-manager',
                name: 'Memory Manager',
                type: 'memory',
                status: 'active',
                activationTime: Date.now() - 3000,
                dependencies: ['consciousness-core'],
                outputs: ['memory-patterns', 'recall-data'],
                performance: { cpu: 8.7, memory: 78.3, latency: 8 }
            },
            {
                id: 'pattern-learner',
                name: 'Pattern Learning Engine',
                type: 'learning',
                status: 'processing',
                activationTime: Date.now() - 2000,
                dependencies: ['memory-manager', 'consciousness-core'],
                outputs: ['learned-patterns', 'adaptation-signals'],
                performance: { cpu: 23.4, memory: 156.7, latency: 25 }
            },
            {
                id: 'thought-synthesizer',
                name: 'Thought Synthesizer',
                type: 'synthesis',
                status: 'active',
                activationTime: Date.now() - 1000,
                dependencies: ['pattern-learner', 'memory-manager'],
                outputs: ['synthesized-thoughts', 'decision-vectors'],
                performance: { cpu: 12.1, memory: 89.2, latency: 18 }
            }
        ];

        setPlugins(samplePlugins);

        // Simulate plugin chains
        const sampleChains: PluginChain[] = [
            {
                id: 'chain-1',
                plugins: ['consciousness-core', 'memory-manager', 'pattern-learner'],
                data: { input: 'sensory-data', confidence: 0.87 },
                timestamp: Date.now() - 2500
            },
            {
                id: 'chain-2',
                plugins: ['memory-manager', 'thought-synthesizer'],
                data: { input: 'memory-recall', confidence: 0.94 },
                timestamp: Date.now() - 1800
            }
        ];

        setChains(sampleChains);
    }, []);

    useEffect(() => {
        if (isMonitoring) {
            const interval = setInterval(() => {
                setPlugins(prev => prev.map(plugin => ({
                    ...plugin,
                    performance: {
                        cpu: Math.max(0, plugin.performance.cpu + (Math.random() - 0.5) * 5),
                        memory: Math.max(0, plugin.performance.memory + (Math.random() - 0.5) * 10),
                        latency: Math.max(0, plugin.performance.latency + (Math.random() - 0.5) * 8)
                    }
                })));
            }, 1000);

            return () => clearInterval(interval);
        }
    }, [isMonitoring]);

    const getStatusColor = (status: PluginTrace['status']) => {
        switch (status) {
            case 'active': return 'text-green-400';
            case 'processing': return 'text-blue-400';
            case 'inactive': return 'text-gray-400';
            case 'error': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    const getTypeColor = (type: PluginTrace['type']) => {
        switch (type) {
            case 'consciousness': return 'bg-purple-600';
            case 'memory': return 'bg-blue-600';
            case 'learning': return 'bg-green-600';
            case 'synthesis': return 'bg-orange-600';
            default: return 'bg-gray-600';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Plugin Trace Viewer</h2>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setIsMonitoring(!isMonitoring)}
                        className={`px-4 py-2 rounded transition-colors ${isMonitoring
                                ? 'bg-red-600 hover:bg-red-700'
                                : 'bg-green-600 hover:bg-green-700'
                            } text-white font-semibold`}
                    >
                        {isMonitoring ? '⏸️ Stop Monitor' : '▶️ Start Monitor'}
                    </button>
                    <div className="text-sm text-gray-400">
                        {plugins.filter(p => p.status === 'active').length} active plugins
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Plugin List */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Active Plugins</h3>
                    <div className="space-y-3">
                        {plugins.map((plugin) => (
                            <motion.div
                                key={plugin.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedPlugin === plugin.id
                                        ? 'border-blue-500 bg-blue-500/10'
                                        : 'border-gray-600 hover:border-gray-500'
                                    }`}
                                onClick={() => setSelectedPlugin(plugin.id)}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className={`w-3 h-3 rounded-full ${getTypeColor(plugin.type)}`} />
                                        <div>
                                            <div className="font-medium text-white">{plugin.name}</div>
                                            <div className="text-xs text-gray-400">{plugin.type}</div>
                                        </div>
                                    </div>
                                    <div className={`text-sm font-medium ${getStatusColor(plugin.status)}`}>
                                        {plugin.status.toUpperCase()}
                                    </div>
                                </div>

                                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                                    <div>
                                        <span className="text-gray-400">CPU:</span>
                                        <span className="ml-1 text-white">{plugin.performance.cpu.toFixed(1)}%</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">MEM:</span>
                                        <span className="ml-1 text-white">{plugin.performance.memory.toFixed(1)}MB</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">LAT:</span>
                                        <span className="ml-1 text-white">{plugin.performance.latency.toFixed(0)}ms</span>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Plugin Details */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Plugin Details</h3>
                    {selectedPlugin ? (
                        <div className="space-y-4">
                            {(() => {
                                const plugin = plugins.find(p => p.id === selectedPlugin);
                                if (!plugin) return null;

                                return (
                                    <>
                                        <div>
                                            <h4 className="font-medium text-white mb-2">{plugin.name}</h4>
                                            <div className="text-sm text-gray-400 space-y-1">
                                                <div>Type: <span className="text-white">{plugin.type}</span></div>
                                                <div>Status: <span className={getStatusColor(plugin.status)}>{plugin.status}</span></div>
                                                <div>Active for: <span className="text-white">{Math.floor((Date.now() - plugin.activationTime) / 1000)}s</span></div>
                                            </div>
                                        </div>

                                        <div>
                                            <h5 className="font-medium text-white mb-2">Dependencies</h5>
                                            <div className="flex flex-wrap gap-2">
                                                {plugin.dependencies.length > 0 ? (
                                                    plugin.dependencies.map(dep => (
                                                        <span key={dep} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
                                                            {dep}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-gray-500 text-sm">No dependencies</span>
                                                )}
                                            </div>
                                        </div>

                                        <div>
                                            <h5 className="font-medium text-white mb-2">Outputs</h5>
                                            <div className="flex flex-wrap gap-2">
                                                {plugin.outputs.map(output => (
                                                    <span key={output} className="px-2 py-1 bg-green-700 rounded text-xs text-green-300">
                                                        {output}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        <div>
                                            <h5 className="font-medium text-white mb-2">Performance Metrics</h5>
                                            <div className="space-y-2">
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">CPU Usage:</span>
                                                    <span className="text-white">{plugin.performance.cpu.toFixed(1)}%</span>
                                                </div>
                                                <div className="w-full bg-gray-700 rounded-full h-2">
                                                    <div
                                                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                                        style={{ width: `${Math.min(100, plugin.performance.cpu)}%` }}
                                                    />
                                                </div>

                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">Memory:</span>
                                                    <span className="text-white">{plugin.performance.memory.toFixed(1)}MB</span>
                                                </div>
                                                <div className="w-full bg-gray-700 rounded-full h-2">
                                                    <div
                                                        className="bg-green-500 h-2 rounded-full transition-all duration-300"
                                                        style={{ width: `${Math.min(100, plugin.performance.memory / 2)}%` }}
                                                    />
                                                </div>

                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-400">Latency:</span>
                                                    <span className="text-white">{plugin.performance.latency.toFixed(0)}ms</span>
                                                </div>
                                                <div className="w-full bg-gray-700 rounded-full h-2">
                                                    <div
                                                        className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                                                        style={{ width: `${Math.min(100, plugin.performance.latency)}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </>
                                );
                            })()}
                        </div>
                    ) : (
                        <div className="text-gray-500 text-center py-8">
                            Select a plugin to view details
                        </div>
                    )}
                </div>
            </div>

            {/* Plugin Chains */}
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Plugin Chains</h3>
                <div className="space-y-3">
                    {chains.map((chain) => (
                        <motion.div
                            key={chain.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="p-3 border border-gray-600 rounded-lg"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-white font-medium">Chain {chain.id}</span>
                                <span className="text-xs text-gray-400">
                                    {new Date(chain.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm">
                                {chain.plugins.map((pluginId, index) => (
                                    <div key={pluginId} className="flex items-center">
                                        <span className="px-2 py-1 bg-blue-600 rounded text-xs text-white">
                                            {pluginId.split('-')[0]}
                                        </span>
                                        {index < chain.plugins.length - 1 && (
                                            <span className="mx-2 text-gray-400">→</span>
                                        )}
                                    </div>
                                ))}
                            </div>
                            <div className="mt-2 text-xs text-gray-400">
                                Confidence: <span className="text-green-400">{(chain.data.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
