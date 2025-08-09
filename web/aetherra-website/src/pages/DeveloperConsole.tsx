import { motion } from 'framer-motion';
import { useState } from 'react';
import { AetherScriptEditor } from '../components/AetherScriptEditor';
import { MemoryTraceViewer } from '../components/MemoryTraceViewer';
import { PluginTraceViewer } from '../components/PluginTraceViewer';
import ScriptExecutionPanel from '../components/ScriptExecutionPanel';

type TabType = 'editor' | 'plugins' | 'memory';

export default function DeveloperConsole() {
    const [activeTab, setActiveTab] = useState<TabType>('editor');
    const [scriptCode, setScriptCode] = useState(`// AetherScript Development Console
consciousness.initialize()
memory.load('neural_patterns')

// Define a consciousness pathway
pathway awareness_loop {
  input: sensory_data
  process: pattern_recognition
  output: conscious_thought

  // Learning feedback loop
  feedback: learning_signals
  adaptation: weight_updates
}

// Execute the awareness loop
loop {
  // Sense the environment
  data = sense()

  // Process through consciousness
  thought = awareness_loop.process(data)

  // Learn from the experience
  learn(thought, data)

  // Evolve understanding
  evolve_patterns()
}

// Memory operations
memory.store('current_experience', thought)
memory.recall('similar_patterns')

// Plugin interaction
plugins.activate('pattern_learner')
plugins.chain(['consciousness_core', 'memory_manager', 'thought_synthesizer'])

console.log("Consciousness loop active...")`);
    const [isExecuting, setIsExecuting] = useState(false);

    const tabs = [
        { id: 'editor' as TabType, name: 'Script Editor', icon: '📝' },
        { id: 'plugins' as TabType, name: 'Plugin Tracer', icon: '🔌' },
        { id: 'memory' as TabType, name: 'Memory Tracer', icon: '🧠' }
    ];

    const executeScript = () => {
        setIsExecuting(true);
        // Simulate execution completion after 5 seconds
        setTimeout(() => {
            setIsExecuting(false);
        }, 5000);
    };

    return (
        <div className="min-h-screen bg-black text-white p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-7xl mx-auto"
            >
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                        Aetherra Developer Console
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Advanced development and debugging tools for AetherScript and consciousness plugins
                    </p>
                </div>

                {/* Navigation Tabs */}
                <div className="flex space-x-1 mb-6 bg-gray-900 rounded-lg p-1">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-md transition-colors ${activeTab === tab.id
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                                }`}
                        >
                            <span className="text-lg">{tab.icon}</span>
                            <span className="font-medium">{tab.name}</span>
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                >
                    {activeTab === 'editor' && (
                        <div className="space-y-6">
                            {/* Editor Section */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <h2 className="text-2xl font-bold text-white">AetherScript Editor</h2>
                                        <button
                                            onClick={executeScript}
                                            disabled={isExecuting}
                                            className={`px-6 py-2 rounded-lg font-semibold transition-colors ${isExecuting
                                                    ? 'bg-gray-600 cursor-not-allowed text-gray-400'
                                                    : 'bg-green-600 hover:bg-green-700 text-white'
                                                }`}
                                        >
                                            {isExecuting ? '⚡ Executing...' : '▶️ Execute Script'}
                                        </button>
                                    </div>
                                    <AetherScriptEditor
                                        value={scriptCode}
                                        onChange={setScriptCode}
                                        language="aether"
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h2 className="text-2xl font-bold text-white">Execution Output</h2>
                                    <ScriptExecutionPanel
                                        script={scriptCode}
                                        isExecuting={isExecuting}
                                        onExecutionComplete={() => setIsExecuting(false)}
                                    />
                                </div>
                            </div>

                            {/* Features Overview */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1 }}
                                    className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                                >
                                    <div className="text-2xl mb-3">🧠</div>
                                    <h3 className="text-lg font-semibold text-white mb-2">Consciousness APIs</h3>
                                    <p className="text-gray-400 text-sm">
                                        Access neural pathways, consciousness loops, and awareness mechanisms
                                    </p>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                    className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                                >
                                    <div className="text-2xl mb-3">💾</div>
                                    <h3 className="text-lg font-semibold text-white mb-2">Memory System</h3>
                                    <p className="text-gray-400 text-sm">
                                        Store, recall, and manage neural patterns and learned experiences
                                    </p>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 }}
                                    className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                                >
                                    <div className="text-2xl mb-3">🔌</div>
                                    <h3 className="text-lg font-semibold text-white mb-2">Plugin System</h3>
                                    <p className="text-gray-400 text-sm">
                                        Chain plugins, trace execution, and debug consciousness flows
                                    </p>
                                </motion.div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'plugins' && (
                        <PluginTraceViewer />
                    )}

                    {activeTab === 'memory' && (
                        <MemoryTraceViewer />
                    )}
                </motion.div>

                {/* Footer Info */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="mt-12 pt-8 border-t border-gray-800"
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-sm">
                        <div>
                            <h4 className="text-white font-semibold mb-2">Documentation</h4>
                            <div className="space-y-1 text-gray-400">
                                <div>• AetherScript Language Guide</div>
                                <div>• Consciousness API Reference</div>
                                <div>• Plugin Development Kit</div>
                            </div>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-2">Debugging Tools</h4>
                            <div className="space-y-1 text-gray-400">
                                <div>• Memory Trace Viewer</div>
                                <div>• Plugin Chain Analyzer</div>
                                <div>• Neural Pattern Inspector</div>
                            </div>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-2">Performance</h4>
                            <div className="space-y-1 text-gray-400">
                                <div>• Real-time Monitoring</div>
                                <div>• Resource Usage Analytics</div>
                                <div>• Latency Optimization</div>
                            </div>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-2">Community</h4>
                            <div className="space-y-1 text-gray-400">
                                <div>• Developer Forums</div>
                                <div>• Code Examples</div>
                                <div>• Best Practices</div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
}
