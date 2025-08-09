import { motion } from 'framer-motion';
import { useRef, useState } from 'react';
import { AetherScriptEditor } from '../components/AetherScriptEditor';
import { AutoCompleteHelper } from '../components/AutoCompleteHelper';
import { ExecutionHistoryPanel } from '../components/ExecutionHistoryPanel';
import { ScriptIOPanel } from '../components/ScriptIOPanel';
import { ScriptValidator, ValidationResult } from '../utils/ScriptValidator';

export default function AetherScriptConsole() {
    const [script, setScript] = useState(`// Advanced AetherScript Development Console
// This is a comprehensive environment for consciousness development

// Initialize the consciousness framework
consciousness.initialize()
memory.load("neural_patterns")
memory.load("consciousness_state")

// Define advanced neural pathways
pathway awareness_processor {
  input: sensory_data
  process: pattern_recognition
  output: conscious_thought

  // Advanced features
  feedback: learning_signals
  adaptation: weight_updates
  optimization: gradient_descent
}

pathway memory_consolidator {
  input: short_term_memory
  process: pattern_integration
  output: long_term_storage

  feedback: recall_accuracy
  adaptation: consolidation_strength
}

// Create a sophisticated neural network
neural network deep_consciousness {
  layers: [
    input(1024),    // Sensory input layer
    hidden(512),    // Pattern recognition
    hidden(256),    // Abstract thinking
    hidden(128),    // Decision making
    output(64)      // Conscious output
  ]
  activation: advanced_relu
  learning_rate: 0.001
  dropout: 0.2
}

// Main consciousness processing loop
loop {
  // Gather comprehensive sensory input
  sensory_data = sense()

  // Process through awareness pathway
  conscious_thought = awareness_processor.process(sensory_data)

  // Enhance through neural network
  enhanced_thought = deep_consciousness.predict(conscious_thought)

  // Learn from the experience
  learning_signal = learn(enhanced_thought, sensory_data)

  // Consolidate memories
  memory_consolidator.process(enhanced_thought)

  // Evolve consciousness patterns
  if (learning_signal.confidence > 0.8) {
    consciousness.evolve()
    deep_consciousness.update_weights(learning_signal)
  }

  // Store significant experiences
  if (enhanced_thought.significance > 0.9) {
    memory.store("significant_experiences", enhanced_thought)
  }
}

// Plugin ecosystem integration
plugins.activate("advanced_pattern_learner")
plugins.activate("consciousness_optimizer")
plugins.activate("memory_compressor")

// Chain plugins for complex processing
plugins.chain([
  "consciousness_core",
  "advanced_pattern_learner",
  "memory_consolidator",
  "consciousness_optimizer"
])

// Performance monitoring
console.log("Advanced consciousness system initialized")
console.log("Neural pathways: active")
console.log("Memory systems: optimized")
console.log("Plugin ecosystem: integrated")`);

    const [isExecuting, setIsExecuting] = useState(false);
    const [validation, setValidation] = useState<ValidationResult | null>(null);
    const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
    const [showAutoComplete, setShowAutoComplete] = useState(false);
    const [executionHistory, setExecutionHistory] = useState<any[]>([]);

    const editorRef = useRef<HTMLTextAreaElement>(null);

    const handleScriptChange = (newScript: string) => {
        setScript(newScript);

        // Validate script in real-time
        const validationResult = ScriptValidator.validate(newScript);
        setValidation(validationResult);
    };

    const handleExecuteScript = () => {
        if (isExecuting) return;

        setIsExecuting(true);

        // Add to execution history
        const executionRecord = {
            id: `exec-${Date.now()}`,
            timestamp: Date.now(),
            script: script,
            duration: 0, // Will be calculated
            status: 'success' as const,
            output: '',
            memoryUsage: Math.random() * 100 + 20,
            cpuUsage: Math.random() * 80 + 10,
            linesExecuted: script.split('\n').filter(line => line.trim() && !line.trim().startsWith('//')).length,
            summary: 'Advanced consciousness script execution'
        };

        // Simulate execution time
        setTimeout(() => {
            setIsExecuting(false);
            executionRecord.duration = 3.5 + Math.random() * 2;
            setExecutionHistory(prev => [executionRecord, ...prev.slice(0, 19)]);
        }, 3500);
    };

    const handleFormatScript = () => {
        const formatted = ScriptValidator.formatScript(script);
        setScript(formatted);
    };

    const handleCursorChange = (line: number, column: number) => {
        setCursorPosition({ line, column });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.ctrlKey && e.key === ' ') {
            e.preventDefault();
            setShowAutoComplete(true);
        }

        if (e.key === 'Escape') {
            setShowAutoComplete(false);
        }
    };

    const insertTextAtCursor = (text: string) => {
        if (!editorRef.current) return;

        const textarea = editorRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const newScript = script.substring(0, start) + text + script.substring(end);

        setScript(newScript);

        // Set cursor position after inserted text
        setTimeout(() => {
            textarea.selectionStart = textarea.selectionEnd = start + text.length;
            textarea.focus();
        }, 0);
    };

    const loadScriptFromHistory = (historyScript: string) => {
        setScript(historyScript);
    };

    const clearExecutionHistory = () => {
        setExecutionHistory([]);
    };

    return (
        <div className="min-h-screen bg-black text-white p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-7xl mx-auto"
            >
                {/* Header */}
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                                AetherScript Console
                            </h1>
                            <p className="text-gray-400 mt-1">
                                Advanced development environment for consciousness programming
                            </p>
                        </div>

                        <div className="flex items-center space-x-3">
                            <button
                                onClick={handleFormatScript}
                                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                            >
                                🎨 Format
                            </button>

                            <button
                                onClick={handleExecuteScript}
                                disabled={isExecuting || (validation?.isValid === false)}
                                className={`px-6 py-2 rounded-lg font-semibold transition-colors ${isExecuting || (validation && !validation.isValid)
                                        ? 'bg-gray-600 cursor-not-allowed text-gray-400'
                                        : 'bg-green-600 hover:bg-green-700 text-white'
                                    }`}
                            >
                                {isExecuting ? '⚡ Executing...' : '▶️ Execute Script'}
                            </button>
                        </div>
                    </div>

                    {/* Validation Status */}
                    {validation && (
                        <div className="mb-4">
                            {validation.errors.length > 0 && (
                                <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 mb-2">
                                    <div className="font-medium text-red-400 mb-2">❌ Errors ({validation.errors.length})</div>
                                    {validation.errors.slice(0, 3).map((error, index) => (
                                        <div key={index} className="text-sm text-red-300 mb-1">
                                            Line {error.line}: {error.message}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {validation.warnings.length > 0 && (
                                <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3 mb-2">
                                    <div className="font-medium text-yellow-400 mb-2">⚠️ Warnings ({validation.warnings.length})</div>
                                    {validation.warnings.slice(0, 2).map((warning, index) => (
                                        <div key={index} className="text-sm text-yellow-300 mb-1">
                                            Line {warning.line}: {warning.message}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {validation.suggestions.length > 0 && (
                                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3">
                                    <div className="font-medium text-blue-400 mb-2">💡 Suggestions ({validation.suggestions.length})</div>
                                    {validation.suggestions.slice(0, 2).map((suggestion, index) => (
                                        <div key={index} className="text-sm text-blue-300 mb-1">
                                            {suggestion.message}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Main Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column - Editor */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="relative">
                            <AetherScriptEditor
                                value={script}
                                onChange={handleScriptChange}
                                language="aether"
                            />

                            <AutoCompleteHelper
                                script={script}
                                cursorPosition={cursorPosition}
                                onInsert={insertTextAtCursor}
                                isVisible={showAutoComplete}
                                onClose={() => setShowAutoComplete(false)}
                            />
                        </div>

                        <ScriptIOPanel
                            isExecuting={isExecuting}
                            script={script}
                        />
                    </div>

                    {/* Right Column - History and Tools */}
                    <div className="space-y-6">
                        <ExecutionHistoryPanel
                            onLoadScript={loadScriptFromHistory}
                            onClearHistory={clearExecutionHistory}
                            currentExecution={executionHistory[0]}
                        />

                        {/* Quick Actions */}
                        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-white mb-3">Quick Actions</h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => setShowAutoComplete(true)}
                                    className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
                                >
                                    🔤 Show Auto-Complete (Ctrl+Space)
                                </button>

                                <button
                                    onClick={() => {
                                        const validationResult = ScriptValidator.validate(script);
                                        setValidation(validationResult);
                                    }}
                                    className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm transition-colors"
                                >
                                    🔍 Validate Script
                                </button>

                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(script);
                                    }}
                                    className="w-full px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                                >
                                    📋 Copy Script
                                </button>

                                <button
                                    onClick={() => {
                                        setScript('// New AetherScript\nconsciousness.initialize()\n\n');
                                    }}
                                    className="w-full px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                                >
                                    🗒️ New Script
                                </button>
                            </div>
                        </div>

                        {/* Script Stats */}
                        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-white mb-3">Script Statistics</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Total Lines:</span>
                                    <span className="text-white">{script.split('\n').length}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Code Lines:</span>
                                    <span className="text-white">
                                        {script.split('\n').filter(line => line.trim() && !line.trim().startsWith('//')).length}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Characters:</span>
                                    <span className="text-white">{script.length}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Pathways:</span>
                                    <span className="text-white">
                                        {(script.match(/pathway\s+\w+/g) || []).length}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Neural Networks:</span>
                                    <span className="text-white">
                                        {(script.match(/neural\s+network/g) || []).length}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Validation:</span>
                                    <span className={validation?.isValid ? 'text-green-400' : 'text-red-400'}>
                                        {validation?.isValid ? '✅ Valid' : '❌ Invalid'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
