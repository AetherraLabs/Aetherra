import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface CodeExample {
  id: string;
  title: string;
  description: string;
  category: 'basic' | 'neural' | 'memory' | 'quantum' | 'advanced';
  code: string;
  explanation: string;
}

interface InteractiveExamplesProps {
  onRunCode?: (code: string) => void;
  isVisible?: boolean;
}

export default function InteractiveExamples({ 
  onRunCode,
  isVisible = true 
}: InteractiveExamplesProps) {
  const [selectedExample, setSelectedExample] = useState<CodeExample | null>(null);
  const [hoveredExample, setHoveredExample] = useState<string | null>(null);
  const [executedExamples, setExecutedExamples] = useState<Set<string>>(new Set());

  const examples: CodeExample[] = [
    {
      id: 'hello_neural',
      title: 'Hello Neural World',
      description: 'Your first neural greeting',
      category: 'basic',
      code: 'lyrixa.log("Hello Neural World!");',
      explanation: 'The most basic AetherScript command. This outputs a message to the neural terminal.'
    },
    {
      id: 'variable_demo',
      title: 'Variables & Types',
      description: 'Declare and use variables',
      category: 'basic',
      code: `const neuralPower = 42;
const message = "Neural computing";
lyrixa.log(message + " power: " + neuralPower);`,
      explanation: 'Demonstrates variable declaration and string concatenation in AetherScript.'
    },
    {
      id: 'memory_allocation',
      title: 'Memory Allocation',
      description: 'Allocate and manage memory',
      category: 'memory',
      code: `const buffer = lyrixa.allocateMemory(1024);
lyrixa.log("Allocated: " + buffer.size + " bytes");
buffer.deallocate();`,
      explanation: 'Shows how to allocate memory buffers and clean them up when done.'
    },
    {
      id: 'neural_network_quick',
      title: 'Quick Neural Network',
      description: 'Create a simple neural network',
      category: 'neural',
      code: `const network = new NeuralNetwork();
network.addLayer(64, "relu");
network.addLayer(10, "softmax");
lyrixa.log("Network ready with " + network.layers.length + " layers");`,
      explanation: 'Creates a basic neural network with an input layer (64 neurons, ReLU) and output layer (10 neurons, softmax).'
    },
    {
      id: 'quantum_demo',
      title: 'Quantum Qubits',
      description: 'Basic quantum operations',
      category: 'quantum',
      code: `const qubits = quantum.createQubits(2);
quantum.hadamard(qubits[0]);
quantum.entangle(qubits[0], qubits[1]);
lyrixa.log("Quantum entanglement created");`,
      explanation: 'Demonstrates quantum computing basics: creating qubits, applying gates, and entanglement.'
    },
    {
      id: 'plugin_loader',
      title: 'Load Plugin',
      description: 'Load and use a plugin',
      category: 'advanced',
      code: `const optimizer = lyrixa.loadPlugin("performance_optimizer");
optimizer.setTarget("memory");
const result = optimizer.optimize();
lyrixa.log("Optimization: " + result.improvement + "% faster");`,
      explanation: 'Shows how to load plugins and use their functionality to enhance system performance.'
    },
    {
      id: 'neural_training_mini',
      title: 'Neural Training',
      description: 'Train a neural network',
      category: 'neural',
      code: `const network = new NeuralNetwork();
network.addLayer(32, "relu");
network.addLayer(2, "sigmoid");
network.setLearningRate(0.01);
lyrixa.log("Training configuration complete");`,
      explanation: 'Sets up a neural network for training with proper configuration parameters.'
    },
    {
      id: 'memory_info',
      title: 'Memory Monitoring',
      description: 'Check system memory status',
      category: 'memory',
      code: `const info = lyrixa.getMemoryInfo();
lyrixa.log("Free memory: " + info.free + " bytes");
lyrixa.log("Used memory: " + info.allocated + " bytes");
lyrixa.log("Total memory: " + info.total + " bytes");`,
      explanation: 'Monitors system memory usage and displays detailed memory statistics.'
    },
    {
      id: 'function_demo',
      title: 'Custom Functions',
      description: 'Define and call functions',
      category: 'basic',
      code: `function calculateNeuralPower(base, multiplier) {
  return base * multiplier * 1.337;
}

const power = calculateNeuralPower(10, 5);
lyrixa.log("Neural power calculated: " + power);`,
      explanation: 'Demonstrates function definition, parameters, return values, and function calls.'
    },
    {
      id: 'quantum_measurement',
      title: 'Quantum Measurement',
      description: 'Measure quantum states',
      category: 'quantum',
      code: `const qubits = quantum.createQubits(3);
quantum.hadamard(qubits[0]);
quantum.pauli_x(qubits[1]);
const results = quantum.measure(qubits);
lyrixa.log("Measured states: " + results.join(", "));`,
      explanation: 'Creates qubits, applies quantum gates, and measures the resulting quantum states.'
    },
    {
      id: 'neural_layers',
      title: 'Multi-Layer Network',
      description: 'Complex neural architecture',
      category: 'neural',
      code: `const network = new NeuralNetwork();
network.addLayer(128, "relu");
network.addLayer(64, "relu");
network.addLayer(32, "relu");
network.addLayer(16, "relu");
network.addLayer(3, "softmax");
lyrixa.log("Deep network with " + network.layers.length + " layers created");`,
      explanation: 'Builds a deep neural network with multiple hidden layers and different activation functions.'
    },
    {
      id: 'advanced_optimization',
      title: 'System Optimization',
      description: 'Advanced performance tuning',
      category: 'advanced',
      code: `const optimizer = lyrixa.loadPlugin("performance_optimizer");
const visualizer = lyrixa.loadPlugin("neural_visualizer");

optimizer.setTarget("neural_processing");
const result = optimizer.optimize();

visualizer.renderPerformanceChart(result);
lyrixa.log("System optimized: " + result.improvement + "% improvement");`,
      explanation: 'Advanced example combining multiple plugins for system optimization and visualization.'
    }
  ];

  const categories = [
    { id: 'basic', name: 'Basic', color: 'bg-blue-500', icon: '📚' },
    { id: 'neural', name: 'Neural', color: 'bg-purple-500', icon: '🧠' },
    { id: 'memory', name: 'Memory', color: 'bg-green-500', icon: '💾' },
    { id: 'quantum', name: 'Quantum', color: 'bg-cyan-500', icon: '⚛️' },
    { id: 'advanced', name: 'Advanced', color: 'bg-red-500', icon: '🚀' }
  ];

  const handleRunExample = (example: CodeExample) => {
    if (onRunCode) {
      onRunCode(example.code);
      setExecutedExamples(prev => new Set([...prev, example.id]));
    }
  };

  const getCategoryInfo = (category: string) => {
    return categories.find(cat => cat.id === category) || categories[0];
  };

  const groupedExamples = categories.map(category => ({
    ...category,
    examples: examples.filter(example => example.category === category.id)
  }));

  if (!isVisible) return null;

  return (
    <div className="h-full bg-gray-900 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 z-10">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">⚡</span>
          <div>
            <h2 className="text-lg font-semibold text-white">Interactive Examples</h2>
            <p className="text-sm text-gray-400">Click any example to run it instantly</p>
          </div>
        </div>
      </div>

      {/* Examples Grid */}
      <div className="p-6 space-y-8">
        {groupedExamples.map(category => (
          <div key={category.id}>
            {/* Category Header */}
            <div className="flex items-center space-x-3 mb-4">
              <div className={`w-8 h-8 ${category.color} rounded-lg flex items-center justify-center`}>
                <span className="text-white text-sm">{category.icon}</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">{category.name}</h3>
                <p className="text-sm text-gray-400">{category.examples.length} examples</p>
              </div>
            </div>

            {/* Category Examples */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {category.examples.map(example => (
                <motion.div
                  key={example.id}
                  className="group relative"
                  onHoverStart={() => setHoveredExample(example.id)}
                  onHoverEnd={() => setHoveredExample(null)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div 
                    className={`border rounded-lg overflow-hidden transition-all duration-200 cursor-pointer ${
                      executedExamples.has(example.id)
                        ? 'border-green-400 bg-green-400/5'
                        : hoveredExample === example.id
                        ? 'border-gray-500 bg-gray-800'
                        : 'border-gray-700 bg-gray-800/50'
                    }`}
                    onClick={() => handleRunExample(example)}
                  >
                    {/* Example Header */}
                    <div className="p-4 border-b border-gray-700">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-white">{example.title}</h4>
                        {executedExamples.has(example.id) && (
                          <span className="text-green-400 text-sm">✓ Executed</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-400">{example.description}</p>
                    </div>

                    {/* Code Preview */}
                    <div className="p-4">
                      <div className="bg-gray-900 rounded border border-gray-700 overflow-hidden">
                        <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
                          <span className="text-xs text-gray-400">AetherScript</span>
                          <div className="flex items-center space-x-1">
                            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                            <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                          </div>
                        </div>
                        <pre className="p-3 text-xs text-gray-300 overflow-x-auto">
                          <code>{example.code}</code>
                        </pre>
                      </div>
                    </div>

                    {/* Run Button Overlay */}
                    <AnimatePresence>
                      {hoveredExample === example.id && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          className="absolute inset-0 bg-black/20 flex items-center justify-center"
                        >
                          <motion.button
                            initial={{ scale: 0.8 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.8 }}
                            className="px-6 py-3 bg-green-400 text-black rounded-lg font-semibold flex items-center space-x-2 shadow-lg"
                          >
                            <span>▶</span>
                            <span>Run Code</span>
                          </motion.button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Explanation Tooltip */}
                  <AnimatePresence>
                    {hoveredExample === example.id && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute bottom-full left-0 right-0 mb-2 p-3 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-20"
                      >
                        <div className="text-sm text-gray-300">{example.explanation}</div>
                        <div className="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="sticky bottom-0 bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-400">
            {examples.length} examples available
          </div>
          <div className="flex items-center space-x-4 text-gray-400">
            <span>{executedExamples.size} executed</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Example Detail Modal */}
      <AnimatePresence>
        {selectedExample && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedExample(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-800 rounded-xl border border-gray-700 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-700">
                <div>
                  <h3 className="text-xl font-semibold text-white">{selectedExample.title}</h3>
                  <p className="text-gray-400">{selectedExample.description}</p>
                </div>
                <button
                  onClick={() => setSelectedExample(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 space-y-4">
                <div>
                  <h4 className="font-medium text-white mb-2">Code</h4>
                  <div className="bg-gray-900 rounded border border-gray-700 p-4">
                    <pre className="text-sm text-gray-300">
                      <code>{selectedExample.code}</code>
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-white mb-2">Explanation</h4>
                  <p className="text-gray-300">{selectedExample.explanation}</p>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedExample(null)}
                    className="px-4 py-2 text-gray-400 hover:text-white"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => handleRunExample(selectedExample)}
                    className="px-6 py-2 bg-green-400 text-black rounded-lg font-medium hover:bg-green-300"
                  >
                    ▶ Run Code
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
