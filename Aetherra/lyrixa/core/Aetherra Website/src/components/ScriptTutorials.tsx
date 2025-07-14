import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface ScriptExample {
  id: string;
  title: string;
  description: string;
  category: 'basic' | 'neural' | 'memory' | 'quantum' | 'plugins';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  code: string;
  output?: string;
}

interface ScriptTutorialsProps {
  onRunExample?: (code: string) => void;
  onClose?: () => void;
}

export default function ScriptTutorials({ onRunExample, onClose }: ScriptTutorialsProps) {
  const [selectedCategory, setSelectedCategory] = useState<ScriptExample['category']>('basic');
  const [selectedExample, setSelectedExample] = useState<ScriptExample | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const examples: ScriptExample[] = [
    // Basic Examples
    {
      id: 'hello_world',
      title: 'Hello Neural World',
      description: 'Your first AetherScript program with basic logging',
      category: 'basic',
      difficulty: 'beginner',
      code: `// Your first AetherScript program
lyrixa.log("Hello, Neural World!");
lyrixa.log("Welcome to Aetherra AI Operating System");

// Variables and basic operations
const message = "Neural computing is the future";
lyrixa.log(message);

// Simple calculations
const neuralPower = 42 * 1337;
lyrixa.log("Neural power level: " + neuralPower);`,
      output: `[LOG] Hello, Neural World!
[LOG] Welcome to Aetherra AI Operating System
[RUNTIME] Variable 'message' declared
[LOG] Neural computing is the future
[RUNTIME] Variable 'neuralPower' declared
[LOG] Neural power level: 56154`
    },
    {
      id: 'variables_functions',
      title: 'Variables and Functions',
      description: 'Learn variable declarations and function definitions',
      category: 'basic',
      difficulty: 'beginner',
      code: `// Variable declarations
const userName = "Neural Developer";
let systemStatus = "Online";

// Function definition
function greetUser(name) {
  lyrixa.log("Greetings, " + name + "!");
  return "Welcome to Aetherra";
}

// Function calls
const welcomeMessage = greetUser(userName);
lyrixa.log(welcomeMessage);

// Conditional logic
if (systemStatus === "Online") {
  lyrixa.log("All systems operational");
} else {
  lyrixa.log("System requires attention");
}`,
      output: `[RUNTIME] Variable 'userName' declared
[RUNTIME] Variable 'systemStatus' declared
[LOG] Greetings, Neural Developer!
[RUNTIME] Variable 'welcomeMessage' declared
[LOG] Welcome to Aetherra
[LOG] All systems operational`
    },

    // Neural Examples
    {
      id: 'neural_network',
      title: 'Basic Neural Network',
      description: 'Create and configure a simple neural network',
      category: 'neural',
      difficulty: 'intermediate',
      code: `// Create a neural network
const network = new NeuralNetwork();

// Add layers
network.addLayer(128, 'relu');
network.addLayer(64, 'relu');
network.addLayer(32, 'relu');
network.addLayer(10, 'softmax');

lyrixa.log("Network created with " + network.layers.length + " layers");

// Configure training parameters
network.setLearningRate(0.001);
network.setOptimizer('adam');

lyrixa.log("Network configured for training");

// Display network architecture
lyrixa.log("Input layer: 128 neurons (ReLU)");
lyrixa.log("Hidden layer 1: 64 neurons (ReLU)");
lyrixa.log("Hidden layer 2: 32 neurons (ReLU)");
lyrixa.log("Output layer: 10 neurons (Softmax)");`,
      output: `[NEURAL] Neural network operation executed
[LOG] Network created with 4 layers
[NEURAL] Neural network operation executed
[NEURAL] Neural network operation executed
[LOG] Network configured for training
[LOG] Input layer: 128 neurons (ReLU)
[LOG] Hidden layer 1: 64 neurons (ReLU)
[LOG] Hidden layer 2: 32 neurons (ReLU)
[LOG] Output layer: 10 neurons (Softmax)`
    },
    {
      id: 'neural_training',
      title: 'Neural Network Training',
      description: 'Train a neural network with data and monitor progress',
      category: 'neural',
      difficulty: 'advanced',
      code: `// Load training data
const trainingData = lyrixa.loadDataset("neural_patterns");
lyrixa.log("Training data loaded: " + trainingData.size + " samples");

// Create and configure network
const network = new NeuralNetwork();
network.addLayer(256, 'relu');
network.addLayer(128, 'relu');
network.addLayer(64, 'relu');
network.addLayer(3, 'softmax');

// Set training parameters
network.setBatchSize(32);
network.setEpochs(100);
network.setValidationSplit(0.2);

// Monitor training progress
network.onEpochComplete = function(epoch, metrics) {
  lyrixa.log("Epoch " + epoch + " - Loss: " + metrics.loss.toFixed(4));
};

// Start training
lyrixa.log("Beginning neural network training...");
network.train(trainingData);`,
      output: `[LOG] Training data loaded: 10000 samples
[NEURAL] Neural network operation executed
[NEURAL] Neural network operation executed
[NEURAL] Neural network operation executed
[NEURAL] Neural network operation executed
[LOG] Beginning neural network training...
[NEURAL] Neural network operation executed
[LOG] Epoch 1 - Loss: 0.8543
[LOG] Epoch 2 - Loss: 0.7291
[LOG] Epoch 3 - Loss: 0.6847`
    },

    // Memory Examples
    {
      id: 'memory_basic',
      title: 'Memory Management',
      description: 'Basic memory allocation and deallocation',
      category: 'memory',
      difficulty: 'beginner',
      code: `// Allocate memory blocks
const buffer1 = lyrixa.allocateMemory(1024);
lyrixa.log("Allocated " + buffer1.size + " bytes");

const buffer2 = lyrixa.allocateMemory(2048);
lyrixa.log("Allocated " + buffer2.size + " bytes");

// Check memory usage
const memoryInfo = lyrixa.getMemoryInfo();
lyrixa.log("Total allocated: " + memoryInfo.allocated + " bytes");
lyrixa.log("Free memory: " + memoryInfo.free + " bytes");

// Deallocate memory
buffer1.deallocate();
lyrixa.log("Buffer 1 deallocated");

// Final memory check
const finalInfo = lyrixa.getMemoryInfo();
lyrixa.log("Final allocated: " + finalInfo.allocated + " bytes");`,
      output: `[MEMORY] Allocated 1024 bytes
[LOG] Allocated 1024 bytes
[MEMORY] Allocated 2048 bytes
[LOG] Allocated 2048 bytes
[LOG] Total allocated: 3072 bytes
[LOG] Free memory: 1021952 bytes
[LOG] Buffer 1 deallocated
[LOG] Final allocated: 2048 bytes`
    },

    // Quantum Examples
    {
      id: 'quantum_basic',
      title: 'Quantum Operations',
      description: 'Basic quantum computing operations',
      category: 'quantum',
      difficulty: 'intermediate',
      code: `// Create quantum qubits
const qubits = quantum.createQubits(4);
lyrixa.log("Created " + qubits.length + " qubits");

// Apply quantum gates
quantum.hadamard(qubits[0]);
quantum.pauli_x(qubits[1]);
quantum.cnot(qubits[0], qubits[2]);

lyrixa.log("Applied quantum gates");

// Create entanglement
quantum.entangle(qubits[0], qubits[1]);
quantum.entangle(qubits[2], qubits[3]);

lyrixa.log("Qubits entangled");

// Measure quantum states
const measurements = quantum.measure(qubits);
lyrixa.log("Quantum measurements: " + measurements.join(", "));

// Display quantum circuit
lyrixa.log("Quantum circuit complete");`,
      output: `[QUANTUM] Quantum operation completed
[LOG] Created 4 qubits
[QUANTUM] Quantum operation completed
[QUANTUM] Quantum operation completed
[QUANTUM] Quantum operation completed
[LOG] Applied quantum gates
[QUANTUM] Quantum operation completed
[QUANTUM] Quantum operation completed
[LOG] Qubits entangled
[QUANTUM] Quantum operation completed
[LOG] Quantum measurements: 0, 1, 1, 0
[LOG] Quantum circuit complete`
    },

    // Plugin Examples
    {
      id: 'plugin_loading',
      title: 'Plugin Management',
      description: 'Load and use plugins to extend functionality',
      category: 'plugins',
      difficulty: 'intermediate',
      code: `// Load core plugins
const optimizer = lyrixa.loadPlugin("performance_optimizer");
const visualizer = lyrixa.loadPlugin("neural_visualizer");
const analyzer = lyrixa.loadPlugin("code_analyzer");

lyrixa.log("Loaded 3 plugins successfully");

// Use optimizer plugin
optimizer.setTarget("memory");
optimizer.setLevel("aggressive");
const optimizationResult = optimizer.optimize();

lyrixa.log("Optimization complete: " + optimizationResult.improvement + "% faster");

// Use visualizer plugin
visualizer.setTheme("neural_dark");
visualizer.renderGraph("network_topology");

lyrixa.log("Neural network visualization rendered");

// Use analyzer plugin
const codeMetrics = analyzer.analyze("current_script");
lyrixa.log("Code complexity: " + codeMetrics.complexity);
lyrixa.log("Performance score: " + codeMetrics.performance);`,
      output: `[PLUGIN] Loaded 'performance_optimizer' successfully
[PLUGIN] Loaded 'neural_visualizer' successfully
[PLUGIN] Loaded 'code_analyzer' successfully
[LOG] Loaded 3 plugins successfully
[EXEC] optimizer.setTarget("memory");
[EXEC] optimizer.setLevel("aggressive");
[EXEC] const optimizationResult = optimizer.optimize();
[LOG] Optimization complete: 23% faster
[EXEC] visualizer.setTheme("neural_dark");
[EXEC] visualizer.renderGraph("network_topology");
[LOG] Neural network visualization rendered
[EXEC] const codeMetrics = analyzer.analyze("current_script");
[LOG] Code complexity: 4.2
[LOG] Performance score: 87`
    }
  ];

  const categories = [
    { id: 'basic' as const, name: 'Basic', icon: '📚', description: 'Fundamental concepts' },
    { id: 'neural' as const, name: 'Neural', icon: '🧠', description: 'Neural networks' },
    { id: 'memory' as const, name: 'Memory', icon: '💾', description: 'Memory management' },
    { id: 'quantum' as const, name: 'Quantum', icon: '⚛️', description: 'Quantum computing' },
    { id: 'plugins' as const, name: 'Plugins', icon: '🔌', description: 'Plugin system' }
  ];

  const difficulties = [
    { id: 'beginner', name: 'Beginner', color: 'text-green-400' },
    { id: 'intermediate', name: 'Intermediate', color: 'text-yellow-400' },
    { id: 'advanced', name: 'Advanced', color: 'text-red-400' }
  ];

  const filteredExamples = examples.filter(example => {
    const matchesCategory = example.category === selectedCategory;
    const matchesSearch = example.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         example.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleRunExample = (example: ScriptExample) => {
    if (onRunExample) {
      onRunExample(example.code);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-4 bg-gray-900 rounded-xl border border-gray-700 shadow-2xl z-40 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">📖</div>
          <div>
            <h1 className="text-lg font-bold text-white">AetherScript Tutorials</h1>
            <p className="text-sm text-gray-400">Interactive code examples and documentation</p>
          </div>
        </div>
        
        {onClose && (
          <button
            onClick={onClose}
            className="px-3 py-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Close"
          >
            ✕
          </button>
        )}
      </div>

      <div className="flex h-full">
        {/* Sidebar */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
          {/* Search */}
          <div className="p-4 border-b border-gray-700">
            <input
              type="text"
              placeholder="Search tutorials..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-400"
            />
          </div>

          {/* Categories */}
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Categories</h3>
            <div className="space-y-1">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-green-400/20 text-green-400 border border-green-400/30'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <span className="text-lg">{category.icon}</span>
                  <div className="text-left">
                    <div className="font-medium">{category.name}</div>
                    <div className="text-xs text-gray-400">{category.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Examples List */}
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">
              Examples ({filteredExamples.length})
            </h3>
            <div className="space-y-2">
              {filteredExamples.map((example) => (
                <motion.button
                  key={example.id}
                  onClick={() => setSelectedExample(example)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedExample?.id === example.id
                      ? 'bg-green-400/10 border-green-400/30 text-green-400'
                      : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{example.title}</span>
                    <span className={`text-xs ${difficulties.find(d => d.id === example.difficulty)?.color}`}>
                      {example.difficulty}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">{example.description}</p>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {selectedExample ? (
            <>
              {/* Example Header */}
              <div className="p-6 border-b border-gray-700 bg-gray-850">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-white mb-1">{selectedExample.title}</h2>
                    <p className="text-gray-400">{selectedExample.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${difficulties.find(d => d.id === selectedExample.difficulty)?.color} bg-gray-700`}>
                      {selectedExample.difficulty}
                    </span>
                    <button
                      onClick={() => handleRunExample(selectedExample)}
                      className="px-4 py-2 bg-green-400 text-black rounded-lg font-medium hover:bg-green-300 transition-colors"
                    >
                      ▶ Run Example
                    </button>
                  </div>
                </div>
              </div>

              {/* Code Display */}
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="space-y-6">
                  {/* Source Code */}
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3">Source Code</h3>
                    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                      <div className="flex items-center justify-between px-4 py-2 bg-gray-750 border-b border-gray-700">
                        <span className="text-sm text-gray-400">AetherScript</span>
                        <button
                          onClick={() => navigator.clipboard.writeText(selectedExample.code)}
                          className="text-xs text-gray-400 hover:text-white"
                        >
                          Copy
                        </button>
                      </div>
                      <pre className="p-4 text-sm text-gray-300 overflow-x-auto">
                        <code>{selectedExample.code}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Expected Output */}
                  {selectedExample.output && (
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Expected Output</h3>
                      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                        <div className="px-4 py-2 bg-gray-750 border-b border-gray-700">
                          <span className="text-sm text-gray-400">Terminal Output</span>
                        </div>
                        <pre className="p-4 text-sm text-green-400 overflow-x-auto font-mono">
                          <code>{selectedExample.output}</code>
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            /* No Example Selected */
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="text-6xl mb-4">📚</div>
                <h3 className="text-xl font-semibold mb-2">Select a Tutorial</h3>
                <p>Choose an example from the sidebar to view code and documentation</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
