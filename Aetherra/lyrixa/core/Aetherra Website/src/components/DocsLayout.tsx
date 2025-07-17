import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface DocsSection {
  id: string;
  title: string;
  icon: string;
  description: string;
  content?: string;
}

interface DocsLayoutProps {
  onClose?: () => void;
  initialSection?: string;
}

export default function DocsLayout({ onClose, initialSection = 'index' }: DocsLayoutProps) {
  const [activeSection, setActiveSection] = useState<string>(initialSection);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState<string>('');
  const [showAssistant, setShowAssistant] = useState(false);

  const docsSections: DocsSection[] = [
    {
      id: 'index',
      title: 'Welcome to Aetherra',
      icon: '🏠',
      description: 'Get started with the AI-Native Operating System'
    },
    {
      id: 'aether-lang',
      title: '.aether Language',
      icon: '⚡',
      description: 'Complete syntax and language reference'
    },
    {
      id: 'memory-system',
      title: 'Memory Architecture',
      icon: '🧠',
      description: 'Understanding Lyrixa\'s memory system'
    },
    {
      id: 'plugin-guide',
      title: 'Plugin Development',
      icon: '🔌',
      description: 'Create and submit your own plugins'
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      icon: '📚',
      description: 'Complete API documentation'
    },
    {
      id: 'neural-networks',
      title: 'Neural Networks',
      icon: '🤖',
      description: 'Building and training neural models'
    },
    {
      id: 'quantum-computing',
      title: 'Quantum Computing',
      icon: '⚛️',
      description: 'Quantum operations and circuits'
    },
    {
      id: 'deployment',
      title: 'Deployment Guide',
      icon: '🚀',
      description: 'Deploy Aetherra applications'
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      icon: '🔧',
      description: 'Common issues and solutions'
    },
    {
      id: 'community',
      title: 'Community',
      icon: '👥',
      description: 'Join the Aetherra community'
    }
  ];

  const filteredSections = docsSections.filter(section =>
    section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    section.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    loadSectionContent(activeSection);
  }, [activeSection]);

  const loadSectionContent = async (sectionId: string) => {
    setLoading(true);
    try {
      // Simulate loading documentation content
      await new Promise(resolve => setTimeout(resolve, 500));

      const sampleContent = getSampleContent(sectionId);
      setContent(sampleContent);
    } catch (error) {
      console.error('Failed to load documentation:', error);
      setContent('# Error\nFailed to load documentation content.');
    } finally {
      setLoading(false);
    }
  };

  const getSampleContent = (sectionId: string): string => {
    switch (sectionId) {
      case 'index':
        return `# Welcome to Aetherra Documentation

Welcome to the comprehensive documentation for **Aetherra**, the world's first AI-Native Operating System. This documentation will guide you through every aspect of using and developing with Aetherra.

## What is Aetherra?

Aetherra is a revolutionary operating system built from the ground up to be AI-native. Unlike traditional operating systems that treat AI as an add-on, Aetherra integrates artificial intelligence into its core architecture.

### Key Features

- **Neural-Native Architecture**: Every component is designed to work with AI
- **Lyrixa Runtime**: Advanced AI processing engine
- **Quantum Computing Support**: Built-in quantum circuit simulation
- **Plugin Ecosystem**: Extensible AI-powered plugins
- **Memory Virtualization**: Advanced memory management for AI workloads

## Getting Started

1. **Installation**: Set up your Aetherra environment
2. **First Steps**: Learn the basics of .aether scripting
3. **Neural Networks**: Build your first AI model
4. **Plugins**: Extend functionality with plugins

## Quick Start Example

\`\`\`aether
// Your first Aetherra program
lyrixa.log("Welcome to the Neural Future!");

// Create a simple neural network
const network = new NeuralNetwork();
network.addLayer(64, "relu");
network.addLayer(10, "softmax");

lyrixa.log("Neural network ready!");
\`\`\`

## Need Help?

- Use the **AI Assistant** (click the 🤖 button) for interactive help
- Browse the sidebar for specific topics
- Check out our **Community** section for support

Welcome to the future of computing! 🚀`;

      case 'aether-lang':
        return `# .aether Language Reference

The .aether language is the primary scripting language for Aetherra OS. It's designed specifically for AI-native computing with built-in support for neural networks, quantum computing, and memory management.

## Basic Syntax

### Variables and Constants

\`\`\`aether
// Constants (immutable)
const neuralPower = 42;
const systemName = "Aetherra";

// Variables (mutable)
let currentState = "initializing";
let memoryUsage = 0;
\`\`\`

### Functions

\`\`\`aether
// Function declaration
function processData(input, options) {
  lyrixa.log("Processing: " + input);
  return input.toUpperCase();
}

// Neural-optimized function
@neural
function trainModel(dataset) {
  const network = new NeuralNetwork();
  return network.train(dataset);
}
\`\`\`

## Core APIs

### Lyrixa Runtime

\`\`\`aether
// Logging and output
lyrixa.log(message);
lyrixa.warn(message);
lyrixa.error(message);

// Memory management
const buffer = lyrixa.allocateMemory(1024);
const info = lyrixa.getMemoryInfo();
buffer.deallocate();

// Plugin system
const plugin = lyrixa.loadPlugin("neural_optimizer");
const plugins = lyrixa.listPlugins();
\`\`\`

### Neural Networks

\`\`\`aether
// Create network
const network = new NeuralNetwork();

// Add layers
network.addLayer(128, "relu");
network.addLayer(64, "relu");
network.addLayer(10, "softmax");

// Configure training
network.setLearningRate(0.001);
network.setOptimizer("adam");
network.setBatchSize(32);

// Train
network.train(trainingData);
\`\`\`

### Quantum Computing

\`\`\`aether
// Create qubits
const qubits = quantum.createQubits(4);

// Apply gates
quantum.hadamard(qubits[0]);
quantum.pauli_x(qubits[1]);
quantum.cnot(qubits[0], qubits[2]);

// Entanglement
quantum.entangle(qubits[0], qubits[1]);

// Measurement
const results = quantum.measure(qubits);
\`\`\`

## Advanced Features

### Macros and Annotations

\`\`\`aether
// Neural optimization
@neural
function complexCalculation(data) {
  return neuralTransform(data);
}

// Quantum-enabled function
@quantum
function quantumSort(array) {
  return quantum.sort(array);
}

// Memory-optimized
@memory_efficient
function processLargeDataset(dataset) {
  // Automatically optimized memory usage
}
\`\`\`

### Error Handling

\`\`\`aether
try {
  const result = riskyOperation();
  lyrixa.log("Success: " + result);
} catch (error) {
  lyrixa.error("Operation failed: " + error.message);
} finally {
  cleanup();
}
\`\`\`

## Best Practices

1. **Use type annotations** for better performance
2. **Leverage neural macros** for AI-heavy computations
3. **Manage memory explicitly** for large datasets
4. **Use quantum operations** for suitable algorithms
5. **Handle errors gracefully** with try-catch blocks

## Next Steps

- Explore the [Memory System](memory-system) documentation
- Learn about [Plugin Development](plugin-guide)
- Check out [Neural Networks](neural-networks) guide`;

      case 'memory-system':
        return `# Memory Architecture

Lyrixa's memory system is designed specifically for AI workloads, providing advanced features like persistent memory, vectorized storage, and automatic optimization.

## Memory Types

### Standard Memory
Traditional RAM-based memory for general computations.

\`\`\`aether
// Allocate standard memory
const buffer = lyrixa.allocateMemory(1024);
lyrixa.log("Allocated: " + buffer.size + " bytes");

// Use memory
buffer.write(0, "Hello Neural World");
const data = buffer.read(0, 18);

// Cleanup
buffer.deallocate();
\`\`\`

### Persistent Memory
Memory that survives between sessions, perfect for AI model storage.

\`\`\`aether
// Create persistent memory
const persistent = lyrixa.createPersistentMemory("model_weights", 1024 * 1024);

// Store neural network weights
persistent.store("network_v1", networkWeights);

// Retrieve in later session
const weights = persistent.retrieve("network_v1");
\`\`\`

### Vectorized Memory
Optimized storage for high-dimensional data and embeddings.

\`\`\`aether
// Create vector store
const vectorStore = lyrixa.createVectorMemory(512); // 512-dimensional

// Store embeddings
vectorStore.addVector("concept_1", embedding1);
vectorStore.addVector("concept_2", embedding2);

// Similarity search
const similar = vectorStore.findSimilar(queryEmbedding, 5);
\`\`\`

## Memory Management

### Automatic Management

\`\`\`aether
// Enable automatic memory management
lyrixa.enableAutoMemory();

// Memory will be automatically managed
const largeDataset = processHugeFile("data.bin");
// No need to manually deallocate
\`\`\`

### Manual Management

\`\`\`aether
// Fine-grained control
const buffer1 = lyrixa.allocateMemory(1024);
const buffer2 = lyrixa.allocateMemory(2048);

// Check memory usage
const info = lyrixa.getMemoryInfo();
lyrixa.log("Free: " + info.free + " bytes");
lyrixa.log("Used: " + info.allocated + " bytes");

// Manual cleanup
buffer1.deallocate();
buffer2.deallocate();
\`\`\`

## Memory Optimization

### Compression

\`\`\`aether
// Enable memory compression
const compressedBuffer = lyrixa.allocateCompressedMemory(1024);
compressedBuffer.setCompressionLevel(9); // Maximum compression

// Data is automatically compressed/decompressed
compressedBuffer.write(0, largeDataArray);
const decompressed = compressedBuffer.read(0, largeDataArray.length);
\`\`\`

### Memory Pools

\`\`\`aether
// Create memory pool for neural networks
const neuralPool = lyrixa.createMemoryPool("neural", {
  blockSize: 1024,
  maxBlocks: 100,
  autoExpand: true
});

// Allocate from pool (faster)
const networkMemory = neuralPool.allocate();
\`\`\`

## Advanced Features

### Memory Mapping

\`\`\`aether
// Map file to memory for efficient access
const mappedFile = lyrixa.mapFileToMemory("large_dataset.bin");

// Access file data as memory
const firstByte = mappedFile.read(0, 1);
mappedFile.write(1000, newData);

// Changes are automatically synced to file
\`\`\`

### Shared Memory

\`\`\`aether
// Create shared memory between processes
const shared = lyrixa.createSharedMemory("neural_cache", 1024 * 1024);

// Process A writes
shared.write(0, trainingResults);

// Process B reads (different .aether script)
const results = shared.read(0, trainingResults.length);
\`\`\`

## Memory Monitoring

### Real-time Monitoring

\`\`\`aether
// Set up memory monitoring
lyrixa.onMemoryWarning(function(info) {
  lyrixa.warn("Low memory: " + info.free + " bytes remaining");

  // Trigger cleanup
  lyrixa.garbageCollect();
});

// Memory usage callbacks
lyrixa.onMemoryThreshold(0.8, function() {
  lyrixa.log("Memory usage at 80%");
});
\`\`\`

### Memory Profiling

\`\`\`aether
// Start memory profiling
lyrixa.startMemoryProfiler();

// Your memory-intensive code
trainLargeNeuralNetwork();

// Get profiling results
const profile = lyrixa.getMemoryProfile();
lyrixa.log("Peak usage: " + profile.peak + " bytes");
lyrixa.log("Allocations: " + profile.allocations);
\`\`\`

## Best Practices

1. **Use persistent memory** for AI models and large datasets
2. **Enable auto-management** for prototyping
3. **Manual management** for production systems
4. **Monitor memory usage** in long-running applications
5. **Use memory pools** for frequent allocations
6. **Leverage compression** for large, infrequently accessed data

## Troubleshooting

### Common Issues

- **Memory leaks**: Always deallocate manual allocations
- **Out of memory**: Monitor usage and implement cleanup
- **Slow access**: Consider memory pools or compression
- **Fragmentation**: Use consistent allocation sizes

### Debugging Commands

\`\`\`aether
// Debug memory state
lyrixa.debugMemory();
lyrixa.listAllocations();
lyrixa.checkMemoryIntegrity();
\`\`\``;

      case 'plugin-guide':
        return `# Plugin Development Guide

Aetherra plugins are modular AI components that extend the functionality of the operating system. This guide will walk you through creating, testing, and submitting your own plugins.

## Plugin Architecture

### Basic Structure

Every Aetherra plugin follows this structure:

\`\`\`
my-plugin/
├── plugin.manifest.json
├── main.aether
├── neural/
│   ├── models/
│   └── weights/
├── quantum/
│   └── circuits/
├── docs/
│   └── README.md
└── tests/
    └── test.aether
\`\`\`

### Plugin Manifest

\`\`\`json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "description": "An awesome AI-powered plugin",
  "author": "Your Name",
  "license": "MIT",
  "aether_version": ">=2.1.0",
  "capabilities": [
    "neural_processing",
    "quantum_computing",
    "memory_management"
  ],
  "entry_point": "main.aether",
  "dependencies": [
    "neural_toolkit@1.5.0",
    "quantum_utils@0.8.0"
  ],
  "resources": {
    "max_memory": "1GB",
    "gpu_required": false,
    "quantum_circuits": 10
  }
}
\`\`\`

## Creating Your First Plugin

### Step 1: Initialize Plugin

\`\`\`aether
// main.aether
const plugin = {
  name: "my-awesome-plugin",
  version: "1.0.0",

  // Plugin initialization
  initialize: function() {
    lyrixa.log("Plugin initialized: " + this.name);
    return true;
  },

  // Main plugin functionality
  process: function(input, options) {
    // Your plugin logic here
    return this.enhanceData(input);
  },

  // Helper methods
  enhanceData: function(data) {
    // AI enhancement logic
    const enhanced = this.neuralEnhance(data);
    return enhanced;
  },

  // Neural processing
  neuralEnhance: function(data) {
    const network = new NeuralNetwork();
    network.addLayer(256, "relu");
    network.addLayer(128, "relu");
    network.addLayer(64, "sigmoid");

    return network.process(data);
  },

  // Cleanup
  cleanup: function() {
    lyrixa.log("Plugin cleanup completed");
  }
};

// Export plugin
module.exports = plugin;
\`\`\`

### Step 2: Add Neural Networks

\`\`\`aether
// neural/classifier.aether
@neural
function createClassifier() {
  const network = new NeuralNetwork();

  // Input layer
  network.addLayer(784, "relu"); // 28x28 image input

  // Hidden layers
  network.addLayer(512, "relu");
  network.addLayer(256, "relu");
  network.addLayer(128, "relu");

  // Output layer
  network.addLayer(10, "softmax"); // 10 classes

  // Configure training
  network.setLearningRate(0.001);
  network.setOptimizer("adam");
  network.setBatchSize(32);

  return network;
}

function trainClassifier(network, trainingData) {
  lyrixa.log("Starting neural network training...");

  // Training loop with progress reporting
  network.onEpochComplete = function(epoch, metrics) {
    lyrixa.log("Epoch " + epoch + " - Accuracy: " + metrics.accuracy.toFixed(4));
  };

  return network.train(trainingData);
}
\`\`\`

### Step 3: Add Quantum Features

\`\`\`aether
// quantum/optimizer.aether
@quantum
function quantumOptimize(parameters) {
  // Create quantum circuit for optimization
  const qubits = quantum.createQubits(8);

  // Initialize superposition
  for (let i = 0; i < qubits.length; i++) {
    quantum.hadamard(qubits[i]);
  }

  // Apply optimization algorithm
  quantumAnneal(qubits, parameters);

  // Measure results
  const results = quantum.measure(qubits);
  return results;
}

function quantumAnneal(qubits, parameters) {
  // Quantum annealing implementation
  for (let step = 0; step < 100; step++) {
    // Apply parameterized gates
    for (let i = 0; i < qubits.length - 1; i++) {
      quantum.rz(qubits[i], parameters[i] * step / 100);
      quantum.cnot(qubits[i], qubits[i + 1]);
    }
  }
}
\`\`\`

## Plugin APIs

### Core Plugin API

\`\`\`aether
// Plugin lifecycle
plugin.initialize();    // Called when plugin loads
plugin.activate();      // Called when plugin becomes active
plugin.deactivate();    // Called when plugin is disabled
plugin.cleanup();       // Called when plugin unloads

// Plugin communication
plugin.sendMessage(targetPlugin, message);
plugin.onMessage(function(sender, message) {
  // Handle messages from other plugins
});

// Resource management
plugin.requestResource("gpu", 1);
plugin.releaseResource("gpu");
\`\`\`

### Storage API

\`\`\`aether
// Plugin-specific storage
plugin.storage.set("key", value);
const value = plugin.storage.get("key");
plugin.storage.remove("key");

// Persistent data
plugin.persistentStorage.save("model_weights", weights);
const weights = plugin.persistentStorage.load("model_weights");
\`\`\`

### UI Integration

\`\`\`aether
// Add plugin to system UI
plugin.ui.addMenuItem("My Plugin", function() {
  plugin.showInterface();
});

// Create plugin window
plugin.ui.createWindow({
  title: "My Awesome Plugin",
  width: 800,
  height: 600,
  content: pluginHTML
});

// System notifications
plugin.ui.notify("Plugin operation completed", "success");
\`\`\`

## Testing Your Plugin

### Unit Tests

\`\`\`aether
// tests/test.aether
const testSuite = {
  name: "My Plugin Tests",

  testInitialization: function() {
    const result = plugin.initialize();
    assert(result === true, "Plugin should initialize successfully");
  },

  testProcessing: function() {
    const input = [1, 2, 3, 4, 5];
    const output = plugin.process(input);
    assert(output.length === input.length, "Output should match input length");
  },

  testNeuralEnhancement: function() {
    const data = generateTestData();
    const enhanced = plugin.neuralEnhance(data);
    assert(enhanced !== null, "Neural enhancement should return result");
  }
};

// Run tests
lyrixa.runTests(testSuite);
\`\`\`

### Integration Tests

\`\`\`aether
// Test plugin with real Aetherra system
function integrationTest() {
  // Load plugin
  const loadedPlugin = lyrixa.loadPlugin("./my-awesome-plugin");

  // Test with system resources
  const result = loadedPlugin.process(systemData);

  // Verify integration
  assert(result.success === true, "Plugin should integrate successfully");

  // Cleanup
  lyrixa.unloadPlugin("my-awesome-plugin");
}
\`\`\`

## Publishing Your Plugin

### Step 1: Prepare for Submission

\`\`\`bash
# Validate plugin
aether validate-plugin ./my-awesome-plugin

# Run security scan
aether security-scan ./my-awesome-plugin

# Generate documentation
aether generate-docs ./my-awesome-plugin
\`\`\`

### Step 2: Submit to Repository

\`\`\`bash
# Login to Aetherra Hub
aether login

# Publish plugin
aether publish ./my-awesome-plugin

# Update existing plugin
aether update my-awesome-plugin --version 1.1.0
\`\`\`

### Step 3: Community Guidelines

1. **Code Quality**: Follow .aether coding standards
2. **Documentation**: Provide comprehensive README and API docs
3. **Testing**: Include unit and integration tests
4. **Security**: No malicious code or data collection
5. **Performance**: Optimize for speed and memory usage
6. **Compatibility**: Support latest Aetherra version

## Advanced Topics

### Plugin Dependencies

\`\`\`aether
// Depend on other plugins
const neuralUtils = lyrixa.requirePlugin("neural_utilities@2.0.0");
const quantumLib = lyrixa.requirePlugin("quantum_library@1.5.0");

// Use dependency functionality
const enhanced = neuralUtils.enhanceData(rawData);
const optimized = quantumLib.optimize(enhanced);
\`\`\`

### Performance Optimization

\`\`\`aether
// Use memory pools
const memoryPool = lyrixa.createMemoryPool("plugin_pool", {
  blockSize: 1024,
  maxBlocks: 50
});

// Optimize neural networks
@neural @memory_efficient
function optimizedProcessing(data) {
  // Automatically optimized by Aetherra
  return processLargeDataset(data);
}
\`\`\`

### Error Handling

\`\`\`aether
// Robust error handling
plugin.process = function(input, options) {
  try {
    return this.safeProcess(input, options);
  } catch (error) {
    lyrixa.error("Plugin error: " + error.message);

    // Report to system
    lyrixa.reportError("my-awesome-plugin", error);

    // Graceful fallback
    return this.fallbackProcess(input);
  }
};
\`\`\`

## Resources

- [Plugin API Reference](api-reference)
- [GitHub Repository](https://github.com/Zyonic88/Aetherra)
- [Discord Community](https://discord.gg/9Xw28xgEQ3)
- [Development Discord](https://discord.gg/9Xw28xgEQ3)

Happy plugin development! 🚀`;

      default:
        return `# ${sectionId}

Documentation for this section is coming soon. Stay tuned for updates!

## Quick Links

- [Welcome](index)
- [.aether Language](aether-lang)
- [Memory System](memory-system)
- [Plugin Guide](plugin-guide)

## Need Help?

Use the AI Assistant (🤖) for interactive help with any Aetherra topic.`;
    }
  };

  const markdownComponents = {
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';

      return !inline && language ? (
        <SyntaxHighlighter
          style={atomDark}
          language={language === 'aether' ? 'javascript' : language}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className="bg-gray-800 px-1 py-0.5 rounded text-green-400 font-mono text-sm" {...props}>
          {children}
        </code>
      );
    },
    h1: ({ children }: any) => (
      <h1 className="text-3xl font-bold text-white mb-6 border-b border-gray-700 pb-3">
        {children}
      </h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-2xl font-semibold text-white mb-4 mt-8">
        {children}
      </h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-xl font-medium text-white mb-3 mt-6">
        {children}
      </h3>
    ),
    p: ({ children }: any) => (
      <p className="text-gray-300 mb-4 leading-relaxed">
        {children}
      </p>
    ),
    ul: ({ children }: any) => (
      <ul className="list-disc list-inside text-gray-300 mb-4 space-y-1">
        {children}
      </ul>
    ),
    ol: ({ children }: any) => (
      <ol className="list-decimal list-inside text-gray-300 mb-4 space-y-1">
        {children}
      </ol>
    ),
    li: ({ children }: any) => (
      <li className="text-gray-300">
        {children}
      </li>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-green-400 pl-4 py-2 bg-gray-800 rounded-r mb-4">
        {children}
      </blockquote>
    ),
    a: ({ href, children }: any) => (
      <button
        onClick={() => {
          if (href && docsSections.find(s => s.id === href)) {
            setActiveSection(href);
          }
        }}
        className="text-green-400 hover:text-green-300 underline cursor-pointer"
      >
        {children}
      </button>
    )
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-gray-900 z-50 flex"
    >
      {/* Sidebar */}
      <motion.div
        initial={{ width: sidebarCollapsed ? 60 : 320 }}
        animate={{ width: sidebarCollapsed ? 60 : 320 }}
        className="bg-gray-800 border-r border-gray-700 flex flex-col"
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-700">
          {!sidebarCollapsed ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">📚</span>
                <h1 className="text-lg font-bold text-white">Aetherra Docs</h1>
              </div>
              <button
                onClick={() => setSidebarCollapsed(true)}
                className="text-gray-400 hover:text-white"
                title="Collapse sidebar"
              >
                ◀
              </button>
            </div>
          ) : (
            <button
              onClick={() => setSidebarCollapsed(false)}
              className="w-full flex justify-center text-gray-400 hover:text-white"
              title="Expand sidebar"
            >
              📚
            </button>
          )}
        </div>

        {/* Search */}
        {!sidebarCollapsed && (
          <div className="p-4 border-b border-gray-700">
            <input
              type="text"
              placeholder="Search documentation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-green-400"
            />
          </div>
        )}

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto">
          {!sidebarCollapsed ? (
            <div className="p-4 space-y-2">
              {filteredSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${activeSection === section.id
                      ? 'bg-green-400/20 text-green-400 border border-green-400/30'
                      : 'text-gray-300 hover:bg-gray-700'
                    }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{section.icon}</span>
                    <div>
                      <div className="font-medium">{section.title}</div>
                      <div className="text-xs text-gray-400">{section.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="p-2 space-y-2">
              {docsSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full p-2 rounded text-center transition-colors ${activeSection === section.id
                      ? 'bg-green-400/20 text-green-400'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  title={section.title}
                >
                  {section.icon}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>v2.1.0</span>
              <span>{filteredSections.length} sections</span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">
              {docsSections.find(s => s.id === activeSection)?.icon}
            </span>
            <div>
              <h1 className="text-lg font-bold text-white">
                {docsSections.find(s => s.id === activeSection)?.title}
              </h1>
              <p className="text-sm text-gray-400">
                {docsSections.find(s => s.id === activeSection)?.description}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAssistant(!showAssistant)}
              className={`px-3 py-2 rounded-lg transition-colors ${showAssistant
                  ? 'bg-green-400/20 text-green-400 border border-green-400/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              title="Toggle AI Assistant"
            >
              🤖 AI Help
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg"
                title="Close Documentation"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex">
          {/* Documentation Content */}
          <div className={`flex-1 overflow-y-auto ${showAssistant ? 'pr-4' : ''}`}>
            <div className="p-8 max-w-4xl">
              {loading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="text-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full mx-auto mb-4"
                    />
                    <p className="text-gray-400">Loading documentation...</p>
                  </div>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown components={markdownComponents}>
                    {content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>

          {/* AI Assistant Panel */}
          <AnimatePresence>
            {showAssistant && (
              <motion.div
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 400, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                className="w-96 border-l border-gray-700 bg-gray-800"
              >
                {/* AI Assistant will be rendered here */}
                <div className="p-4 border-b border-gray-700">
                  <h3 className="font-semibold text-white">AI Assistant</h3>
                  <p className="text-xs text-gray-400">Ask me anything about Aetherra</p>
                </div>
                <div className="p-4">
                  <div className="bg-gray-700 rounded p-3 mb-4">
                    <p className="text-sm text-gray-300">
                      👋 Hi! I'm your AI documentation assistant. I can help you understand Aetherra concepts, provide code examples, and answer questions about the platform.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
                      How do I create a neural network?
                    </button>
                    <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
                      What is the .aether language?
                    </button>
                    <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
                      How does memory management work?
                    </button>
                    <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
                      Guide me through plugin development
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
