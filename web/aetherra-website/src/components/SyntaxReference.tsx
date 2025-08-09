import { AnimatePresence, motion } from 'framer-motion';
import { useMemo, useState } from 'react';

interface SyntaxItem {
    id: string;
    name: string;
    type: 'keyword' | 'type' | 'macro' | 'function' | 'operator' | 'builtin';
    category: string;
    description: string;
    syntax: string;
    example: string;
    parameters?: Parameter[];
    returnType?: string;
    version?: string;
    deprecated?: boolean;
}

interface Parameter {
    name: string;
    type: string;
    description: string;
    optional?: boolean;
    defaultValue?: string;
}

const syntaxData: SyntaxItem[] = [
    // Keywords
    {
        id: 'consciousness',
        name: 'consciousness',
        type: 'keyword',
        category: 'Core',
        description: 'Defines a consciousness class that represents an AI entity with awareness and state management',
        syntax: 'consciousness <Name> { <body> }',
        example: `consciousness MyAI {
  state: "awakening"
  awareness: 0.5

  init() {
    this.state = "active"
  }
}`,
        version: '1.0.0'
    },
    {
        id: 'memory',
        name: 'memory',
        type: 'keyword',
        category: 'Core',
        description: 'Creates memory storage systems for consciousness entities',
        syntax: 'memory <type>(<options>)',
        example: `memory short_term = MemoryBank(capacity: 100)
memory long_term = PersistentMemory()
memory.store("key", "value")`,
        version: '1.0.0'
    },
    {
        id: 'neural',
        name: 'neural',
        type: 'keyword',
        category: 'Neural',
        description: 'Defines neural network components and processing systems',
        syntax: 'neural <component>(<configuration>)',
        example: `neural network = Network(
  layers: [64, 128, 64, 32],
  activation: "relu",
  learning_rate: 0.01
)`,
        version: '1.1.0'
    },
    {
        id: 'pattern',
        name: 'pattern',
        type: 'keyword',
        category: 'Recognition',
        description: 'Creates pattern recognition and matching systems',
        syntax: 'pattern <name> { <rules> }',
        example: `pattern emotional_state {
  match happiness: emotion > 0.7 && energy > 0.5
  match sadness: emotion < 0.3 && energy < 0.4
  match excited: emotion > 0.8 && energy > 0.8
}`,
        version: '1.2.0'
    },
    {
        id: 'evolve',
        name: 'evolve',
        type: 'keyword',
        category: 'Learning',
        description: 'Triggers evolutionary learning and adaptation processes',
        syntax: 'evolve(<parameters>)',
        example: `evolve(
  generations: 10,
  mutation_rate: 0.1,
  fitness_function: calculate_performance
)`,
        version: '1.0.0'
    },
    {
        id: 'perceive',
        name: 'perceive',
        type: 'keyword',
        category: 'Sensing',
        description: 'Enables consciousness to perceive and process environmental input',
        syntax: 'perceive <input_source>',
        example: `perceive environment.visual_input()
perceive sensor_data.audio_stream()
perceive user.emotional_state()`,
        version: '1.0.0'
    },

    // Types
    {
        id: 'ConsciousnessState',
        name: 'ConsciousnessState',
        type: 'type',
        category: 'Core Types',
        description: 'Represents the current state and properties of a consciousness',
        syntax: 'ConsciousnessState { <properties> }',
        example: `let state: ConsciousnessState = {
  level: 0.8,
  focus: "learning",
  mood: "curious",
  energy: 0.9,
  last_update: time.now()
}`,
        version: '1.0.0'
    },
    {
        id: 'MemoryBank',
        name: 'MemoryBank',
        type: 'type',
        category: 'Memory Types',
        description: 'A structured storage system for memories and experiences',
        syntax: 'MemoryBank(capacity: <number>, retention: <duration>)',
        example: `let working_memory: MemoryBank = MemoryBank(
  capacity: 50,
  retention: "1 hour",
  compression: true
)`,
        parameters: [
            { name: 'capacity', type: 'number', description: 'Maximum number of memories to store' },
            { name: 'retention', type: 'duration', description: 'How long to keep memories', optional: true, defaultValue: 'permanent' },
            { name: 'compression', type: 'boolean', description: 'Enable memory compression', optional: true, defaultValue: 'false' }
        ],
        version: '1.0.0'
    },
    {
        id: 'NeuralNetwork',
        name: 'NeuralNetwork',
        type: 'type',
        category: 'Neural Types',
        description: 'Defines a neural network for pattern processing and learning',
        syntax: 'NeuralNetwork(<configuration>)',
        example: `let brain: NeuralNetwork = NeuralNetwork({
  architecture: [128, 256, 128, 64],
  activation: "relu",
  optimizer: "adam",
  learning_rate: 0.001
})`,
        parameters: [
            { name: 'architecture', type: 'number[]', description: 'Network layer sizes' },
            { name: 'activation', type: 'string', description: 'Activation function', optional: true, defaultValue: 'relu' },
            { name: 'optimizer', type: 'string', description: 'Optimization algorithm', optional: true, defaultValue: 'sgd' },
            { name: 'learning_rate', type: 'number', description: 'Learning rate', optional: true, defaultValue: '0.01' }
        ],
        version: '1.1.0'
    },

    // Macros
    {
        id: 'think',
        name: 'think',
        type: 'macro',
        category: 'Cognitive Macros',
        description: 'High-level thinking and reasoning operations',
        syntax: 'think(<problem>, <context>)',
        example: `let solution = think(
  "How to optimize memory usage?",
  context: current_state
)`,
        parameters: [
            { name: 'problem', type: 'string', description: 'The problem to think about' },
            { name: 'context', type: 'any', description: 'Contextual information', optional: true }
        ],
        returnType: 'Solution',
        version: '1.0.0'
    },
    {
        id: 'learn',
        name: 'learn',
        type: 'macro',
        category: 'Learning Macros',
        description: 'Automated learning from experience and data',
        syntax: 'learn(<data>, <method>)',
        example: `learn(training_data, method: "supervised")
learn(experience, method: "reinforcement")`,
        parameters: [
            { name: 'data', type: 'any[]', description: 'Training data or experiences' },
            { name: 'method', type: 'string', description: 'Learning method', optional: true, defaultValue: 'auto' }
        ],
        version: '1.0.0'
    },
    {
        id: 'adapt',
        name: 'adapt',
        type: 'macro',
        category: 'Evolution Macros',
        description: 'Adaptive behavior modification based on environment',
        syntax: 'adapt(<environment>, <goals>)',
        example: `adapt(current_environment, goals: [
  "improve efficiency",
  "reduce errors",
  "enhance creativity"
])`,
        version: '1.0.0'
    },

    // Functions
    {
        id: 'calculate_similarity',
        name: 'calculate_similarity',
        type: 'function',
        category: 'Utility Functions',
        description: 'Calculates similarity between two patterns or states',
        syntax: 'calculate_similarity(a, b, method?)',
        example: `let sim = calculate_similarity(
  pattern1,
  pattern2,
  method: "cosine"
)`,
        parameters: [
            { name: 'a', type: 'any', description: 'First item to compare' },
            { name: 'b', type: 'any', description: 'Second item to compare' },
            { name: 'method', type: 'string', description: 'Similarity method', optional: true, defaultValue: 'euclidean' }
        ],
        returnType: 'number',
        version: '1.0.0'
    },
    {
        id: 'optimize_performance',
        name: 'optimize_performance',
        type: 'function',
        category: 'Performance',
        description: 'Optimizes consciousness performance and resource usage',
        syntax: 'optimize_performance(targets?)',
        example: `optimize_performance([
  "memory_usage",
  "processing_speed",
  "energy_efficiency"
])`,
        parameters: [
            { name: 'targets', type: 'string[]', description: 'Optimization targets', optional: true }
        ],
        returnType: 'OptimizationResult',
        version: '1.1.0'
    },

    // Operators
    {
        id: 'consciousness_merge',
        name: '⊕',
        type: 'operator',
        category: 'Consciousness Operators',
        description: 'Merges two consciousness states or memories',
        syntax: 'a ⊕ b',
        example: `let merged = consciousness_a ⊕ consciousness_b
let combined_memory = memory1 ⊕ memory2`,
        version: '1.0.0'
    },
    {
        id: 'pattern_match',
        name: '≈',
        type: 'operator',
        category: 'Pattern Operators',
        description: 'Pattern matching and similarity comparison',
        syntax: 'pattern ≈ target',
        example: `if user_input ≈ expected_pattern {
  execute_response()
}`,
        version: '1.0.0'
    },
    {
        id: 'evolve_operator',
        name: '→',
        type: 'operator',
        category: 'Evolution Operators',
        description: 'Evolution and transformation operator',
        syntax: 'source → target',
        example: `simple_ai → advanced_ai
basic_pattern → complex_pattern`,
        version: '1.0.0'
    },

    // Built-ins
    {
        id: 'environment',
        name: 'environment',
        type: 'builtin',
        category: 'Global Objects',
        description: 'Global environment interface for external world interaction',
        syntax: 'environment.<method>',
        example: `let data = environment.scan()
environment.output("Hello, world!")
let sensors = environment.get_sensors()`,
        version: '1.0.0'
    },
    {
        id: 'time',
        name: 'time',
        type: 'builtin',
        category: 'Global Objects',
        description: 'Time and temporal operations interface',
        syntax: 'time.<method>',
        example: `let now = time.now()
time.sleep(1000)
let elapsed = time.since(start_time)`,
        version: '1.0.0'
    },
    {
        id: 'consciousness_core',
        name: 'consciousness_core',
        type: 'builtin',
        category: 'Global Objects',
        description: 'Core consciousness management system',
        syntax: 'consciousness_core.<method>',
        example: `consciousness_core.register(my_ai)
let status = consciousness_core.get_status()
consciousness_core.optimize_all()`,
        version: '1.0.0'
    }
];

export function SyntaxReference() {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedType, setSelectedType] = useState<string>('all');
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [selectedItem, setSelectedItem] = useState<SyntaxItem | null>(null);

    const types = ['all', 'keyword', 'type', 'macro', 'function', 'operator', 'builtin'];
    const categories = ['all', ...Array.from(new Set(syntaxData.map(item => item.category)))];

    const filteredItems = useMemo(() => {
        return syntaxData.filter(item => {
            const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.description.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = selectedType === 'all' || item.type === selectedType;
            const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;

            return matchesSearch && matchesType && matchesCategory;
        });
    }, [searchTerm, selectedType, selectedCategory]);

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'keyword': return '🔑';
            case 'type': return '📦';
            case 'macro': return '⚡';
            case 'function': return '🔧';
            case 'operator': return '🔀';
            case 'builtin': return '🌐';
            default: return '📄';
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'keyword': return 'text-blue-400 bg-blue-600/20';
            case 'type': return 'text-green-400 bg-green-600/20';
            case 'macro': return 'text-purple-400 bg-purple-600/20';
            case 'function': return 'text-yellow-400 bg-yellow-600/20';
            case 'operator': return 'text-red-400 bg-red-600/20';
            case 'builtin': return 'text-cyan-400 bg-cyan-600/20';
            default: return 'text-gray-400 bg-gray-600/20';
        }
    };

    return (
        <div className="h-full flex">
            {/* Sidebar */}
            <div className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col">
                {/* Search and Filters */}
                <div className="p-4 border-b border-gray-700">
                    <h2 className="text-lg font-bold text-white mb-4">AetherScript Reference</h2>

                    <input
                        type="text"
                        placeholder="Search syntax..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm mb-3"
                    />

                    <div className="grid grid-cols-1 gap-2">
                        <select
                            value={selectedType}
                            onChange={(e) => setSelectedType(e.target.value)}
                            className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                        >
                            {types.map(type => (
                                <option key={type} value={type}>
                                    {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                                </option>
                            ))}
                        </select>

                        <select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                        >
                            {categories.map(category => (
                                <option key={category} value={category}>
                                    {category === 'all' ? 'All Categories' : category}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Item List */}
                <div className="flex-1 overflow-y-auto">
                    <AnimatePresence>
                        {filteredItems.map((item) => (
                            <motion.div
                                key={item.id}
                                layout
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.2 }}
                                className={`p-3 border-b border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors ${selectedItem?.id === item.id ? 'bg-gray-800 border-l-4 border-blue-500' : ''
                                    }`}
                                onClick={() => setSelectedItem(item)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <span className="text-lg">{getTypeIcon(item.type)}</span>
                                            <span className="font-mono font-semibold text-white text-sm truncate">
                                                {item.name}
                                            </span>
                                            {item.deprecated && (
                                                <span className="text-red-400 text-xs">⚠️</span>
                                            )}
                                        </div>
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className={`text-xs px-2 py-1 rounded ${getTypeColor(item.type)}`}>
                                                {item.type}
                                            </span>
                                            <span className="text-xs text-gray-400">{item.category}</span>
                                        </div>
                                        <p className="text-xs text-gray-300 line-clamp-2">
                                            {item.description}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {filteredItems.length === 0 && (
                        <div className="p-6 text-center">
                            <div className="text-2xl mb-2">🔍</div>
                            <p className="text-gray-400 text-sm">No items found</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Detail Panel */}
            <div className="flex-1 flex flex-col">
                {selectedItem ? (
                    <motion.div
                        key={selectedItem.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                        className="flex-1 overflow-y-auto"
                    >
                        {/* Header */}
                        <div className="bg-gray-900 border-b border-gray-700 p-6">
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="flex items-center space-x-3 mb-2">
                                        <span className="text-2xl">{getTypeIcon(selectedItem.type)}</span>
                                        <h1 className="text-2xl font-bold text-white font-mono">
                                            {selectedItem.name}
                                        </h1>
                                        <span className={`text-sm px-3 py-1 rounded ${getTypeColor(selectedItem.type)}`}>
                                            {selectedItem.type}
                                        </span>
                                        {selectedItem.deprecated && (
                                            <span className="bg-red-600/20 text-red-400 text-sm px-3 py-1 rounded">
                                                Deprecated
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-gray-300 mb-2">{selectedItem.description}</p>
                                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                                        <span>Category: {selectedItem.category}</span>
                                        {selectedItem.version && <span>Since: v{selectedItem.version}</span>}
                                        {selectedItem.returnType && <span>Returns: {selectedItem.returnType}</span>}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="p-6 space-y-6">
                            {/* Syntax */}
                            <div>
                                <h3 className="text-lg font-semibold text-white mb-3">Syntax</h3>
                                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                                    <code className="text-green-400 font-mono text-sm">
                                        {selectedItem.syntax}
                                    </code>
                                </div>
                            </div>

                            {/* Parameters */}
                            {selectedItem.parameters && selectedItem.parameters.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-3">Parameters</h3>
                                    <div className="space-y-3">
                                        {selectedItem.parameters.map((param, index) => (
                                            <div key={index} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                                                <div className="flex items-start justify-between mb-2">
                                                    <span className="font-mono text-blue-400">
                                                        {param.name}
                                                        {param.optional && <span className="text-gray-400">?</span>}
                                                    </span>
                                                    <span className="text-green-400 text-sm">{param.type}</span>
                                                </div>
                                                <p className="text-gray-300 text-sm mb-2">{param.description}</p>
                                                {param.defaultValue && (
                                                    <p className="text-gray-400 text-xs">
                                                        Default: <code className="text-yellow-400">{param.defaultValue}</code>
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Example */}
                            <div>
                                <h3 className="text-lg font-semibold text-white mb-3">Example</h3>
                                <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                                    <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
                                        <span className="text-green-400 font-mono text-sm">AetherScript</span>
                                        <button
                                            onClick={() => navigator.clipboard.writeText(selectedItem.example)}
                                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs transition-colors"
                                        >
                                            Copy
                                        </button>
                                    </div>
                                    <pre className="p-4 text-green-400 font-mono text-sm overflow-x-auto bg-black">
                                        <code>{selectedItem.example}</code>
                                    </pre>
                                </div>
                            </div>

                            {/* Additional Info */}
                            {selectedItem.deprecated && (
                                <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                                    <h4 className="text-red-400 font-semibold mb-2">⚠️ Deprecated</h4>
                                    <p className="text-red-200 text-sm">
                                        This feature is deprecated and may be removed in future versions.
                                        Consider using alternative approaches.
                                    </p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                ) : (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-6xl mb-4">📖</div>
                            <h3 className="text-xl font-bold text-white mb-2">AetherScript Reference</h3>
                            <p className="text-gray-400">
                                Select an item from the sidebar to view its documentation
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
