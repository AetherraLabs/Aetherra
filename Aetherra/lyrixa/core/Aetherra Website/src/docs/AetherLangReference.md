# .aether Language Reference

**Complete Syntax and API Documentation**

The .aether language is the primary programming language for Aetherra OS, designed specifically for AI-native computing. It provides native support for neural networks, quantum computing, memory management, and plugin development.

## Table of Contents

- [Basic Syntax](#basic-syntax)
- [Data Types](#data-types)
- [Control Flow](#control-flow)
- [Functions](#functions)
- [Neural Networks](#neural-networks)
- [Quantum Computing](#quantum-computing)
- [Memory Management](#memory-management)
- [Plugin System](#plugin-system)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)

## Basic Syntax

### Variables and Constants

```aether
// Constants (immutable values)
const neuralPower = 42;
const systemName = "Aetherra";
const pi = 3.14159;

// Variables (mutable values)
let currentState = "initializing";
let memoryUsage = 0;
let isTraining = false;

// Type annotations (optional but recommended)
const iterations: number = 1000;
const modelName: string = "classifier_v1";
const isReady: boolean = true;
```

### Comments

```aether
// Single-line comment

/*
Multi-line comment
for detailed explanations
*/

/**
 * Documentation comment
 * @param input The input data to process
 * @returns Processed neural data
 */
```

### String Operations

```aether
// String concatenation
const greeting = "Hello, " + "Neural World!";
const message = `Welcome to ${systemName}`;

// String methods
const upperCase = message.toUpperCase();
const length = message.length;
const contains = message.includes("Neural");
```

## Data Types

### Primitive Types

```aether
// Numbers
const integer = 42;
const decimal = 3.14159;
const scientific = 1.23e-4;

// Strings
const text = "Neural computing";
const multiline = `Multi-line
string content`;

// Booleans
const isActive = true;
const isComplete = false;

// Null and undefined
const empty = null;
const notDefined = undefined;
```

### Arrays and Collections

```aether
// Arrays
const numbers = [1, 2, 3, 4, 5];
const names = ["Alice", "Bob", "Charlie"];
const mixed = [42, "text", true, null];

// Array operations
numbers.push(6);
const length = numbers.length;
const first = numbers[0];
const last = numbers[numbers.length - 1];

// Array methods
const doubled = numbers.map(x => x * 2);
const filtered = numbers.filter(x => x > 3);
const sum = numbers.reduce((a, b) => a + b, 0);
```

### Objects

```aether
// Object literals
const neuralConfig = {
  layers: 3,
  activation: "relu",
  learningRate: 0.001,
  batchSize: 32
};

// Access properties
lyrixa.log(neuralConfig.layers);
lyrixa.log(neuralConfig["activation"]);

// Modify properties
neuralConfig.learningRate = 0.0005;
neuralConfig.epochs = 100;
```

## Control Flow

### Conditional Statements

```aether
// If statements
if (systemState === "ready") {
  lyrixa.log("System is ready for neural processing");
} else if (systemState === "training") {
  lyrixa.log("Neural network training in progress");
} else {
  lyrixa.log("System initializing...");
}

// Ternary operator
const status = isTraining ? "Training" : "Idle";

// Switch statements
switch (networkType) {
  case "classifier":
    setupClassificationNetwork();
    break;
  case "regression":
    setupRegressionNetwork();
    break;
  default:
    setupGenericNetwork();
}
```

### Loops

```aether
// For loops
for (let i = 0; i < epochs; i++) {
  trainNetwork(i);
  lyrixa.log("Epoch " + i + " completed");
}

// While loops
let converged = false;
let iteration = 0;
while (!converged && iteration < maxIterations) {
  const loss = trainStep();
  converged = loss < threshold;
  iteration++;
}

// For-in loops (objects)
for (const key in neuralConfig) {
  lyrixa.log(key + ": " + neuralConfig[key]);
}

// For-of loops (arrays)
for (const value of trainingData) {
  processDataPoint(value);
}
```

## Functions

### Function Declaration

```aether
// Basic function
function greetUser(name) {
  lyrixa.log("Hello, " + name + "!");
  return "Greeting sent";
}

// Function with type annotations
function calculateAccuracy(correct: number, total: number): number {
  return (correct / total) * 100;
}

// Function with default parameters
function createNetwork(layers = 3, activation = "relu") {
  const network = new NeuralNetwork();
  for (let i = 0; i < layers; i++) {
    network.addLayer(64, activation);
  }
  return network;
}
```

### Arrow Functions

```aether
// Arrow function syntax
const square = (x) => x * x;
const add = (a, b) => a + b;

// Arrow function with block body
const processData = (data) => {
  const cleaned = cleanData(data);
  const normalized = normalizeData(cleaned);
  return normalized;
};

// Array methods with arrow functions
const predictions = inputs.map(x => network.predict(x));
const accurateResults = predictions.filter(p => p.confidence > 0.8);
```

### Higher-Order Functions

```aether
// Functions that return functions
function createOptimizer(learningRate) {
  return function(gradients) {
    return gradients.map(g => g * learningRate);
  };
}

// Functions that accept functions
function trainWithCallback(network, data, onEpochComplete) {
  for (let epoch = 0; epoch < 100; epoch++) {
    const loss = network.trainEpoch(data);
    onEpochComplete(epoch, loss);
  }
}

// Usage
const optimizer = createOptimizer(0.001);
trainWithCallback(network, data, (epoch, loss) => {
  lyrixa.log(`Epoch ${epoch}: Loss = ${loss}`);
});
```

## Neural Networks

### Creating Neural Networks

```aether
// Basic network creation
const network = new NeuralNetwork();

// Add layers with different configurations
network.addLayer(784, "relu");     // Input layer: 784 neurons, ReLU activation
network.addLayer(128, "relu");     // Hidden layer: 128 neurons, ReLU activation
network.addLayer(64, "relu");      // Hidden layer: 64 neurons, ReLU activation
network.addLayer(10, "softmax");   // Output layer: 10 neurons, Softmax activation

lyrixa.log("Neural network created with " + network.layers.length + " layers");
```

### Network Configuration

```aether
// Configure training parameters
network.setLearningRate(0.001);
network.setOptimizer("adam");       // Options: sgd, adam, rmsprop
network.setBatchSize(32);
network.setEpochs(100);
network.setValidationSplit(0.2);

// Advanced configuration
network.setRegularization("l2", 0.001);
network.setDropout(0.5);
network.setEarlyStopping({
  patience: 10,
  minDelta: 0.001
});
```

### Training Networks

```aether
// Load training data
const trainingData = lyrixa.loadDataset("mnist_digits");
const testData = lyrixa.loadDataset("mnist_test");

// Set up training callbacks
network.onEpochComplete = function(epoch, metrics) {
  lyrixa.log(`Epoch ${epoch}:`);
  lyrixa.log(`  Loss: ${metrics.loss.toFixed(4)}`);
  lyrixa.log(`  Accuracy: ${metrics.accuracy.toFixed(4)}`);
  lyrixa.log(`  Val Loss: ${metrics.valLoss.toFixed(4)}`);
  lyrixa.log(`  Val Accuracy: ${metrics.valAccuracy.toFixed(4)}`);
};

network.onTrainingComplete = function(finalMetrics) {
  lyrixa.log("Training completed!");
  lyrixa.log("Final accuracy: " + finalMetrics.accuracy.toFixed(4));
};

// Start training
lyrixa.log("Beginning neural network training...");
const history = network.train(trainingData);

// Evaluate on test data
const testResults = network.evaluate(testData);
lyrixa.log("Test accuracy: " + testResults.accuracy.toFixed(4));
```

### Model Persistence

```aether
// Save trained model
const modelData = network.serialize();
lyrixa.persistentStorage.save("trained_classifier", modelData);
lyrixa.log("Model saved successfully");

// Load saved model
const savedModelData = lyrixa.persistentStorage.load("trained_classifier");
const loadedNetwork = NeuralNetwork.deserialize(savedModelData);
lyrixa.log("Model loaded successfully");

// Export model for deployment
const exportedModel = network.export("tensorflow");
lyrixa.fileSystem.write("model.tf", exportedModel);
```

## Quantum Computing

### Qubit Operations

```aether
// Create quantum qubits
const qubits = quantum.createQubits(4);
lyrixa.log("Created " + qubits.length + " qubits");

// Initialize qubit states
quantum.reset(qubits[0]);           // |0⟩ state
quantum.setOne(qubits[1]);          // |1⟩ state

// Single-qubit gates
quantum.hadamard(qubits[0]);        // Create superposition
quantum.pauli_x(qubits[1]);         // NOT gate
quantum.pauli_y(qubits[2]);         // Y rotation
quantum.pauli_z(qubits[3]);         // Z rotation

// Parameterized gates
quantum.rx(qubits[0], Math.PI / 4); // X rotation by π/4
quantum.ry(qubits[1], Math.PI / 2); // Y rotation by π/2
quantum.rz(qubits[2], Math.PI);     // Z rotation by π
```

### Quantum Circuits

```aether
// Create quantum circuit
const circuit = new QuantumCircuit(4); // 4-qubit circuit

// Add gates to circuit
circuit.h(0);                       // Hadamard on qubit 0
circuit.cnot(0, 1);                 // CNOT gate
circuit.cnot(1, 2);                 // CNOT gate
circuit.cnot(2, 3);                 // CNOT gate

// Measure all qubits
circuit.measureAll();

// Execute circuit
const results = quantum.execute(circuit, {
  shots: 1000,
  backend: "simulator"
});

lyrixa.log("Quantum circuit results:");
for (const state in results.counts) {
  lyrixa.log(`|${state}⟩: ${results.counts[state]} times`);
}
```

### Quantum Algorithms

```aether
// Grover's search algorithm
@quantum
function groversSearch(database, target) {
  const n = Math.log2(database.length);
  const qubits = quantum.createQubits(n);
  
  // Initialize superposition
  for (let i = 0; i < n; i++) {
    quantum.hadamard(qubits[i]);
  }
  
  // Grover iterations
  const iterations = Math.floor(Math.PI / 4 * Math.sqrt(database.length));
  for (let i = 0; i < iterations; i++) {
    // Oracle
    oracle(qubits, target);
    
    // Diffusion operator
    diffusionOperator(qubits);
  }
  
  // Measure result
  const result = quantum.measure(qubits);
  return database[result];
}

// Quantum Fourier Transform
@quantum
function quantumFourierTransform(qubits) {
  const n = qubits.length;
  
  for (let i = 0; i < n; i++) {
    quantum.hadamard(qubits[i]);
    
    for (let j = i + 1; j < n; j++) {
      const angle = Math.PI / Math.pow(2, j - i);
      quantum.controlledPhase(qubits[j], qubits[i], angle);
    }
  }
  
  // Reverse qubit order
  for (let i = 0; i < n / 2; i++) {
    quantum.swap(qubits[i], qubits[n - 1 - i]);
  }
}
```

## Memory Management

### Memory Allocation

```aether
// Basic memory allocation
const buffer = lyrixa.allocateMemory(1024);  // 1KB
lyrixa.log("Allocated: " + buffer.size + " bytes");

// Typed memory allocation
const floatBuffer = lyrixa.allocateTypedMemory("float32", 256);
const intBuffer = lyrixa.allocateTypedMemory("int32", 128);

// Large memory allocation
const bigBuffer = lyrixa.allocateMemory(1024 * 1024 * 100); // 100MB
lyrixa.log("Large buffer allocated: " + bigBuffer.size + " bytes");
```

### Persistent Memory

```aether
// Create persistent memory space
const modelStorage = lyrixa.createPersistentMemory("neural_models", 1024 * 1024 * 10); // 10MB

// Store data persistently
modelStorage.store("classifier_weights", networkWeights);
modelStorage.store("training_history", trainingMetrics);

// Retrieve persistent data
const weights = modelStorage.retrieve("classifier_weights");
const history = modelStorage.retrieve("training_history");

// List stored items
const items = modelStorage.listItems();
lyrixa.log("Stored items: " + items.join(", "));
```

### Vectorized Memory

```aether
// Create vector memory for embeddings
const vectorStore = lyrixa.createVectorMemory(512); // 512-dimensional vectors

// Add vectors with labels
vectorStore.addVector("concept_ai", aiEmbedding);
vectorStore.addVector("concept_neural", neuralEmbedding);
vectorStore.addVector("concept_quantum", quantumEmbedding);

// Similarity search
const queryEmbedding = generateEmbedding("machine learning");
const similarConcepts = vectorStore.findSimilar(queryEmbedding, 5);

for (const match of similarConcepts) {
  lyrixa.log(`${match.label}: similarity = ${match.score.toFixed(3)}`);
}
```

### Memory Monitoring

```aether
// Get memory information
const memInfo = lyrixa.getMemoryInfo();
lyrixa.log("Total memory: " + memInfo.total + " bytes");
lyrixa.log("Free memory: " + memInfo.free + " bytes");
lyrixa.log("Used memory: " + memInfo.allocated + " bytes");
lyrixa.log("Memory usage: " + (memInfo.allocated / memInfo.total * 100).toFixed(1) + "%");

// Set memory warnings
lyrixa.onMemoryWarning(function(info) {
  lyrixa.warn("Low memory warning!");
  lyrixa.warn("Free memory: " + info.free + " bytes");
  
  // Trigger cleanup
  lyrixa.garbageCollect();
});

// Memory threshold monitoring
lyrixa.onMemoryThreshold(0.8, function() {
  lyrixa.log("Memory usage exceeded 80%");
  // Implement memory optimization
});

lyrixa.onMemoryThreshold(0.9, function() {
  lyrixa.warn("Memory usage exceeded 90%");
  // Emergency cleanup
});
```

## Plugin System

### Loading Plugins

```aether
// Load plugins by name
const optimizer = lyrixa.loadPlugin("performance_optimizer");
const visualizer = lyrixa.loadPlugin("neural_visualizer");
const analyzer = lyrixa.loadPlugin("code_analyzer");

lyrixa.log("Loaded plugins: optimizer, visualizer, analyzer");

// List available plugins
const availablePlugins = lyrixa.listPlugins();
lyrixa.log("Available plugins:");
for (const plugin of availablePlugins) {
  lyrixa.log(`  - ${plugin.name} v${plugin.version}: ${plugin.description}`);
}
```

### Using Plugin Features

```aether
// Configure optimizer plugin
optimizer.setTarget("neural_processing");
optimizer.setLevel("aggressive");
optimizer.setMetrics(["speed", "memory", "accuracy"]);

// Run optimization
const optimizationResult = optimizer.optimize();
lyrixa.log("Optimization complete:");
lyrixa.log("  Speed improvement: " + optimizationResult.speedGain + "%");
lyrixa.log("  Memory reduction: " + optimizationResult.memoryReduction + "%");
lyrixa.log("  Accuracy maintained: " + optimizationResult.accuracyChange + "%");

// Use visualizer plugin
visualizer.setTheme("neural_dark");
visualizer.setLayout("hierarchical");

// Visualize neural network
visualizer.renderNetwork(network, {
  showWeights: true,
  showActivations: true,
  highlightPath: true
});

// Visualize training progress
visualizer.renderTrainingHistory(trainingHistory, {
  metrics: ["loss", "accuracy", "val_loss", "val_accuracy"],
  smoothing: 0.1
});
```

### Plugin Communication

```aether
// Send data between plugins
const analysisResults = analyzer.analyzeCode(sourceCode);
visualizer.renderAnalysis(analysisResults);

// Plugin event handling
optimizer.onOptimizationComplete = function(results) {
  lyrixa.log("Optimization finished!");
  visualizer.showOptimizationResults(results);
};

visualizer.onVisualizationReady = function(chartData) {
  lyrixa.log("Visualization generated");
  // Save or export visualization
};
```

## Advanced Features

### Neural Macros

```aether
// Neural-optimized functions
@neural
function neuralTransform(inputData) {
  // This function will be automatically optimized for neural processing
  const processed = inputData.map(x => x * 2 + 1);
  return processed;
}

// Quantum-enabled functions
@quantum
function quantumOptimize(parameters) {
  // This function can use quantum algorithms for optimization
  return quantum.anneal(parameters);
}

// Memory-efficient functions
@memory_efficient
function processLargeDataset(dataset) {
  // Automatic memory optimization for large data processing
  return dataset.process();
}
```

### Error Handling

```aether
// Try-catch for error handling
try {
  const result = riskyNeuralOperation();
  lyrixa.log("Operation successful: " + result);
} catch (error) {
  lyrixa.error("Neural operation failed: " + error.message);
  
  // Fallback strategy
  const fallbackResult = safeFallbackOperation();
  lyrixa.log("Fallback completed: " + fallbackResult);
} finally {
  // Cleanup code
  cleanupResources();
}

// Custom error types
class NeuralNetworkError extends Error {
  constructor(message, networkState) {
    super(message);
    this.name = "NeuralNetworkError";
    this.networkState = networkState;
  }
}

// Throw custom errors
function validateNetwork(network) {
  if (network.layers.length === 0) {
    throw new NeuralNetworkError("Network has no layers", network.getState());
  }
}
```

### Async Operations

```aether
// Async function declaration
async function trainNetworkAsync(network, data) {
  lyrixa.log("Starting asynchronous training...");
  
  try {
    const result = await network.trainAsync(data);
    lyrixa.log("Training completed successfully");
    return result;
  } catch (error) {
    lyrixa.error("Training failed: " + error.message);
    throw error;
  }
}

// Promise handling
const trainingPromise = trainNetworkAsync(network, trainingData);

trainingPromise
  .then(result => {
    lyrixa.log("Training result: " + result.accuracy);
  })
  .catch(error => {
    lyrixa.error("Training error: " + error.message);
  });

// Parallel operations
async function parallelTraining() {
  const networks = [network1, network2, network3];
  const datasets = [data1, data2, data3];
  
  const trainingPromises = networks.map((net, i) => 
    trainNetworkAsync(net, datasets[i])
  );
  
  const results = await Promise.all(trainingPromises);
  lyrixa.log("All networks trained successfully");
  return results;
}
```

## Best Practices

### Code Organization

```aether
// Use meaningful variable names
const neuralNetworkClassifier = new NeuralNetwork();
const trainingDatasetImages = lyrixa.loadDataset("images");
const modelAccuracyThreshold = 0.95;

// Group related functionality
const NetworkConfig = {
  DEFAULT_LEARNING_RATE: 0.001,
  DEFAULT_BATCH_SIZE: 32,
  DEFAULT_EPOCHS: 100,
  
  createStandardNetwork: function() {
    const network = new NeuralNetwork();
    network.setLearningRate(this.DEFAULT_LEARNING_RATE);
    network.setBatchSize(this.DEFAULT_BATCH_SIZE);
    return network;
  }
};

// Use constants for magic numbers
const IMAGE_WIDTH = 28;
const IMAGE_HEIGHT = 28;
const NUM_CLASSES = 10;
const INPUT_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT;
```

### Performance Optimization

```aether
// Efficient memory usage
function processDataEfficiently(largeDataset) {
  // Process data in chunks to avoid memory overflow
  const chunkSize = 1000;
  const results = [];
  
  for (let i = 0; i < largeDataset.length; i += chunkSize) {
    const chunk = largeDataset.slice(i, i + chunkSize);
    const processedChunk = processChunk(chunk);
    results.push(...processedChunk);
    
    // Allow garbage collection
    if (i % (chunkSize * 10) === 0) {
      lyrixa.garbageCollect();
    }
  }
  
  return results;
}

// Use neural macros for AI-heavy operations
@neural
function optimizedNeuralProcessing(data) {
  // This will be automatically optimized
  return data.neuralTransform();
}

// Cache expensive computations
const computationCache = new Map();

function expensiveComputation(input) {
  const cacheKey = JSON.stringify(input);
  
  if (computationCache.has(cacheKey)) {
    return computationCache.get(cacheKey);
  }
  
  const result = performExpensiveCalculation(input);
  computationCache.set(cacheKey, result);
  return result;
}
```

### Error Prevention

```aether
// Input validation
function validateTrainingData(data) {
  if (!data || data.length === 0) {
    throw new Error("Training data cannot be empty");
  }
  
  if (!Array.isArray(data)) {
    throw new Error("Training data must be an array");
  }
  
  // Validate data structure
  for (let i = 0; i < data.length; i++) {
    if (!data[i].input || !data[i].output) {
      throw new Error(`Invalid data point at index ${i}`);
    }
  }
}

// Defensive programming
function safeNetworkOperation(network, operation) {
  if (!network) {
    lyrixa.error("Network is null or undefined");
    return null;
  }
  
  if (network.layers.length === 0) {
    lyrixa.warn("Network has no layers");
    return null;
  }
  
  try {
    return operation(network);
  } catch (error) {
    lyrixa.error("Network operation failed: " + error.message);
    return null;
  }
}
```

### Documentation

```aether
/**
 * Creates and trains a neural network classifier
 * @param {Array} trainingData - Array of {input, output} objects
 * @param {Object} config - Network configuration options
 * @param {number} config.learningRate - Learning rate for training (default: 0.001)
 * @param {number} config.batchSize - Batch size for training (default: 32)
 * @param {number} config.epochs - Number of training epochs (default: 100)
 * @returns {NeuralNetwork} Trained neural network
 */
function createAndTrainClassifier(trainingData, config = {}) {
  // Apply default configuration
  const finalConfig = {
    learningRate: 0.001,
    batchSize: 32,
    epochs: 100,
    ...config
  };
  
  // Validate inputs
  validateTrainingData(trainingData);
  
  // Create network
  const network = new NeuralNetwork();
  network.setLearningRate(finalConfig.learningRate);
  network.setBatchSize(finalConfig.batchSize);
  
  // Train network
  lyrixa.log(`Training classifier with ${trainingData.length} samples`);
  const history = network.train(trainingData);
  
  lyrixa.log(`Training completed. Final accuracy: ${history.accuracy.toFixed(4)}`);
  return network;
}
```

---

This comprehensive reference covers the essential aspects of .aether programming. For more advanced topics and specific use cases, refer to the specialized documentation sections:

- [Memory Architecture](memory-system) - Deep dive into memory management
- [Plugin Development](plugin-guide) - Creating custom AI-powered plugins
- [Neural Networks](neural-networks) - Advanced neural network techniques
- [Quantum Computing](quantum-computing) - Quantum algorithm implementation

**Happy coding in the neural future!** 🚀
