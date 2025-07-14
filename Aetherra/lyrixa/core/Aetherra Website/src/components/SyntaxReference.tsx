import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface SyntaxItem {
  name: string;
  type: 'keyword' | 'function' | 'method' | 'type' | 'macro';
  category: string;
  description: string;
  syntax: string;
  example: string;
  parameters?: { name: string; type: string; description: string }[];
  returns?: string;
}

interface SyntaxReferenceProps {
  onInsertCode?: (code: string) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function SyntaxReference({ 
  onInsertCode, 
  isCollapsed = false, 
  onToggleCollapse 
}: SyntaxReferenceProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('core');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItem, setSelectedItem] = useState<SyntaxItem | null>(null);

  const syntaxItems: SyntaxItem[] = [
    // Core Language
    {
      name: 'lyrixa.log',
      type: 'function',
      category: 'core',
      description: 'Output a message to the terminal',
      syntax: 'lyrixa.log(message)',
      example: 'lyrixa.log("Hello Neural World!");',
      parameters: [
        { name: 'message', type: 'string', description: 'The message to display' }
      ],
      returns: 'void'
    },
    {
      name: 'const',
      type: 'keyword',
      category: 'core',
      description: 'Declare a constant variable',
      syntax: 'const variableName = value;',
      example: 'const neuralPower = 42;'
    },
    {
      name: 'let',
      type: 'keyword',
      category: 'core',
      description: 'Declare a mutable variable',
      syntax: 'let variableName = value;',
      example: 'let systemStatus = "Online";'
    },
    {
      name: 'function',
      type: 'keyword',
      category: 'core',
      description: 'Define a function',
      syntax: 'function functionName(parameters) { ... }',
      example: 'function greetUser(name) {\n  lyrixa.log("Hello " + name);\n}'
    },

    // Memory Management
    {
      name: 'lyrixa.allocateMemory',
      type: 'function',
      category: 'memory',
      description: 'Allocate a block of memory',
      syntax: 'lyrixa.allocateMemory(size)',
      example: 'const buffer = lyrixa.allocateMemory(1024);',
      parameters: [
        { name: 'size', type: 'number', description: 'Size in bytes to allocate' }
      ],
      returns: 'MemoryBuffer'
    },
    {
      name: 'lyrixa.getMemoryInfo',
      type: 'function',
      category: 'memory',
      description: 'Get current memory usage information',
      syntax: 'lyrixa.getMemoryInfo()',
      example: 'const info = lyrixa.getMemoryInfo();\nlyrixa.log("Free: " + info.free);',
      returns: 'MemoryInfo'
    },
    {
      name: 'MemoryBuffer',
      type: 'type',
      category: 'memory',
      description: 'Represents an allocated memory buffer',
      syntax: 'buffer.deallocate()',
      example: 'buffer.deallocate();'
    },

    // Neural Networks
    {
      name: 'NeuralNetwork',
      type: 'type',
      category: 'neural',
      description: 'Create a new neural network',
      syntax: 'new NeuralNetwork()',
      example: 'const network = new NeuralNetwork();'
    },
    {
      name: 'addLayer',
      type: 'method',
      category: 'neural',
      description: 'Add a layer to the neural network',
      syntax: 'network.addLayer(neurons, activation)',
      example: 'network.addLayer(128, "relu");',
      parameters: [
        { name: 'neurons', type: 'number', description: 'Number of neurons in the layer' },
        { name: 'activation', type: 'string', description: 'Activation function (relu, sigmoid, tanh, softmax)' }
      ]
    },
    {
      name: 'train',
      type: 'method',
      category: 'neural',
      description: 'Train the neural network with data',
      syntax: 'network.train(data)',
      example: 'network.train(trainingData);',
      parameters: [
        { name: 'data', type: 'Dataset', description: 'Training data' }
      ]
    },
    {
      name: 'setLearningRate',
      type: 'method',
      category: 'neural',
      description: 'Set the learning rate for training',
      syntax: 'network.setLearningRate(rate)',
      example: 'network.setLearningRate(0.001);',
      parameters: [
        { name: 'rate', type: 'number', description: 'Learning rate (0.0 to 1.0)' }
      ]
    },

    // Quantum Computing
    {
      name: 'quantum.createQubits',
      type: 'function',
      category: 'quantum',
      description: 'Create quantum qubits',
      syntax: 'quantum.createQubits(count)',
      example: 'const qubits = quantum.createQubits(4);',
      parameters: [
        { name: 'count', type: 'number', description: 'Number of qubits to create' }
      ],
      returns: 'Qubit[]'
    },
    {
      name: 'quantum.hadamard',
      type: 'function',
      category: 'quantum',
      description: 'Apply Hadamard gate to a qubit',
      syntax: 'quantum.hadamard(qubit)',
      example: 'quantum.hadamard(qubits[0]);',
      parameters: [
        { name: 'qubit', type: 'Qubit', description: 'Target qubit' }
      ]
    },
    {
      name: 'quantum.entangle',
      type: 'function',
      category: 'quantum',
      description: 'Entangle two qubits',
      syntax: 'quantum.entangle(qubit1, qubit2)',
      example: 'quantum.entangle(qubits[0], qubits[1]);',
      parameters: [
        { name: 'qubit1', type: 'Qubit', description: 'First qubit' },
        { name: 'qubit2', type: 'Qubit', description: 'Second qubit' }
      ]
    },
    {
      name: 'quantum.measure',
      type: 'function',
      category: 'quantum',
      description: 'Measure quantum states',
      syntax: 'quantum.measure(qubits)',
      example: 'const results = quantum.measure(qubits);',
      parameters: [
        { name: 'qubits', type: 'Qubit[]', description: 'Qubits to measure' }
      ],
      returns: 'number[]'
    },

    // Plugin System
    {
      name: 'lyrixa.loadPlugin',
      type: 'function',
      category: 'plugins',
      description: 'Load a plugin module',
      syntax: 'lyrixa.loadPlugin(name)',
      example: 'const optimizer = lyrixa.loadPlugin("performance_optimizer");',
      parameters: [
        { name: 'name', type: 'string', description: 'Plugin name' }
      ],
      returns: 'Plugin'
    },
    {
      name: 'lyrixa.listPlugins',
      type: 'function',
      category: 'plugins',
      description: 'List all available plugins',
      syntax: 'lyrixa.listPlugins()',
      example: 'const plugins = lyrixa.listPlugins();',
      returns: 'string[]'
    },

    // Data Types
    {
      name: 'Dataset',
      type: 'type',
      category: 'data',
      description: 'Represents a data collection for training',
      syntax: 'lyrixa.loadDataset(name)',
      example: 'const data = lyrixa.loadDataset("neural_patterns");'
    },
    {
      name: '@neural',
      type: 'macro',
      category: 'macros',
      description: 'Mark a function as neural-optimized',
      syntax: '@neural function functionName() { ... }',
      example: '@neural function processData(input) {\n  return neuralTransform(input);\n}'
    },
    {
      name: '@quantum',
      type: 'macro',
      category: 'macros',
      description: 'Enable quantum computing features',
      syntax: '@quantum function functionName() { ... }',
      example: '@quantum function quantumSort(array) {\n  return quantum.sort(array);\n}'
    }
  ];

  const categories = [
    { id: 'core', name: 'Core', icon: '⚡', description: 'Basic language features' },
    { id: 'memory', name: 'Memory', icon: '💾', description: 'Memory management' },
    { id: 'neural', name: 'Neural', icon: '🧠', description: 'Neural networks' },
    { id: 'quantum', name: 'Quantum', icon: '⚛️', description: 'Quantum computing' },
    { id: 'plugins', name: 'Plugins', icon: '🔌', description: 'Plugin system' },
    { id: 'data', name: 'Data', icon: '📊', description: 'Data types' },
    { id: 'macros', name: 'Macros', icon: '🔧', description: 'Special annotations' }
  ];

  const typeColors = {
    keyword: 'text-blue-400',
    function: 'text-green-400',
    method: 'text-yellow-400',
    type: 'text-purple-400',
    macro: 'text-pink-400'
  };

  const filteredItems = syntaxItems.filter(item => {
    const matchesCategory = item.category === selectedCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleInsertCode = (code: string) => {
    if (onInsertCode) {
      onInsertCode(code);
    }
  };

  if (isCollapsed) {
    return (
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: 'auto' }}
        className="h-full bg-gray-800 border-l border-gray-700 flex flex-col"
      >
        <button
          onClick={onToggleCollapse}
          className="h-12 px-3 text-gray-400 hover:text-white hover:bg-gray-700 transition-colors border-b border-gray-700"
          title="Expand Syntax Reference"
        >
          📖
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ width: 0, opacity: 0 }}
      animate={{ width: 400, opacity: 1 }}
      exit={{ width: 0, opacity: 0 }}
      className="w-96 h-full bg-gray-800 border-l border-gray-700 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <span className="text-lg">📖</span>
          <h2 className="font-semibold text-white">Syntax Reference</h2>
        </div>
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="text-gray-400 hover:text-white transition-colors"
            title="Collapse"
          >
            ◀
          </button>
        )}
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-700">
        <input
          type="text"
          placeholder="Search syntax..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-green-400"
        />
      </div>

      {/* Categories */}
      <div className="p-4 border-b border-gray-700">
        <div className="grid grid-cols-2 gap-1">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center space-x-1 px-2 py-1 rounded text-xs transition-colors ${
                selectedCategory === category.id
                  ? 'bg-green-400/20 text-green-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              title={category.description}
            >
              <span>{category.icon}</span>
              <span>{category.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Items List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-2">
          {filteredItems.map((item) => (
            <div key={item.name} className="border border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setSelectedItem(selectedItem?.name === item.name ? null : item)}
                className="w-full text-left p-3 hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`font-mono text-sm ${typeColors[item.type]}`}>
                    {item.name}
                  </span>
                  <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                    {item.type}
                  </span>
                </div>
                <p className="text-xs text-gray-400">{item.description}</p>
              </button>

              {selectedItem?.name === item.name && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="border-t border-gray-700 bg-gray-750"
                >
                  <div className="p-3 space-y-3">
                    {/* Syntax */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-300 mb-1">Syntax</h4>
                      <div className="bg-gray-800 rounded p-2">
                        <code className="text-xs text-green-400 font-mono">
                          {item.syntax}
                        </code>
                      </div>
                    </div>

                    {/* Parameters */}
                    {item.parameters && (
                      <div>
                        <h4 className="text-xs font-semibold text-gray-300 mb-1">Parameters</h4>
                        <div className="space-y-1">
                          {item.parameters.map((param) => (
                            <div key={param.name} className="text-xs">
                              <span className="text-yellow-400 font-mono">{param.name}</span>
                              <span className="text-gray-400"> ({param.type})</span>
                              <span className="text-gray-300"> - {param.description}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Returns */}
                    {item.returns && (
                      <div>
                        <h4 className="text-xs font-semibold text-gray-300 mb-1">Returns</h4>
                        <span className="text-xs text-purple-400 font-mono">{item.returns}</span>
                      </div>
                    )}

                    {/* Example */}
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="text-xs font-semibold text-gray-300">Example</h4>
                        <button
                          onClick={() => handleInsertCode(item.example)}
                          className="text-xs text-green-400 hover:text-green-300"
                        >
                          Insert
                        </button>
                      </div>
                      <div className="bg-gray-800 rounded p-2">
                        <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                          {item.example}
                        </pre>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <div className="p-8 text-center text-gray-400">
            <div className="text-3xl mb-2">🔍</div>
            <p>No syntax items found</p>
            <p className="text-xs">Try a different search term or category</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <span>{filteredItems.length} items</span>
          <span>AetherScript v2.1</span>
        </div>
      </div>
    </motion.div>
  );
}
