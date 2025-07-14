import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: string;
}

interface HelpAssistantProps {
  currentSection?: string;
  documentationContent?: string;
  isVisible?: boolean;
  onClose?: () => void;
}

export default function HelpAssistant({ 
  currentSection = 'index',
  documentationContent = '',
  isVisible = true,
  onClose 
}: HelpAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [conversationContext, setConversationContext] = useState<string[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    initializeAssistant();
  }, [currentSection]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isVisible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isVisible]);

  const initializeAssistant = () => {
    const welcomeMessage: Message = {
      id: `msg_${Date.now()}`,
      type: 'assistant',
      content: getWelcomeMessage(currentSection),
      timestamp: new Date(),
      context: currentSection
    };

    setMessages([welcomeMessage]);
    setSuggestedQuestions(getSuggestedQuestions(currentSection));
    setConversationContext([currentSection]);
  };

  const getWelcomeMessage = (section: string): string => {
    switch (section) {
      case 'index':
        return `👋 Welcome to Aetherra! I'm your AI documentation assistant. I can help you understand the AI-Native OS, explain concepts, provide code examples, and guide you through getting started. What would you like to learn about?`;
      
      case 'aether-lang':
        return `⚡ I'm here to help with the .aether language! I can explain syntax, provide examples, help with neural network code, quantum computing operations, and memory management. What aspect of .aether programming interests you?`;
      
      case 'memory-system':
        return `🧠 Let's explore Lyrixa's memory architecture! I can explain persistent memory, vectorized storage, memory optimization techniques, and help you write efficient memory management code. What memory topic would you like to dive into?`;
      
      case 'plugin-guide':
        return `🔌 Ready to build some plugins? I can guide you through plugin architecture, help you create neural-powered extensions, explain the plugin API, and walk you through the submission process. What kind of plugin are you thinking of building?`;
      
      default:
        return `🤖 I'm your AI assistant for Aetherra documentation. I have deep knowledge about this section and can help explain concepts, provide examples, and answer your questions. How can I assist you today?`;
    }
  };

  const getSuggestedQuestions = (section: string): string[] => {
    switch (section) {
      case 'index':
        return [
          "What makes Aetherra different from other operating systems?",
          "How do I get started with .aether programming?",
          "What are the key features of Aetherra?",
          "Show me a simple neural network example"
        ];
      
      case 'aether-lang':
        return [
          "How do I create a neural network in .aether?",
          "What are the basic data types in .aether?",
          "Show me quantum computing examples",
          "How does memory management work?",
          "What are neural macros and how do I use them?"
        ];
      
      case 'memory-system':
        return [
          "How do I allocate persistent memory?",
          "What's the difference between standard and vectorized memory?",
          "How do I optimize memory usage for large datasets?",
          "Show me memory profiling examples",
          "How does automatic memory management work?"
        ];
      
      case 'plugin-guide':
        return [
          "How do I create my first plugin?",
          "What's the plugin manifest format?",
          "How do I add neural networks to my plugin?",
          "How do I test and debug plugins?",
          "What are the submission requirements?"
        ];
      
      default:
        return [
          "Explain this concept in simple terms",
          "Show me a code example",
          "What are the best practices?",
          "How does this relate to other Aetherra features?"
        ];
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
      context: currentSection
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setIsTyping(true);

    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // Generate AI response
    const aiResponse = await generateAIResponse(content, currentSection, conversationContext);
    
    const assistantMessage: Message = {
      id: `msg_${Date.now() + 1}`,
      type: 'assistant',
      content: aiResponse,
      timestamp: new Date(),
      context: currentSection
    };

    setMessages(prev => [...prev, assistantMessage]);
    setConversationContext(prev => [...prev, content, aiResponse]);
    setIsTyping(false);

    // Update suggested questions based on conversation
    setSuggestedQuestions(getContextualSuggestions(content, currentSection));
  };

  const generateAIResponse = async (
    question: string, 
    section: string, 
    context: string[]
  ): Promise<string> => {
    // Simulate AI processing with contextual responses
    const lowerQuestion = question.toLowerCase();

    // Neural network related questions
    if (lowerQuestion.includes('neural network') || lowerQuestion.includes('network')) {
      return `🧠 **Creating Neural Networks in Aetherra**

Here's how you can create and train neural networks using .aether:

\`\`\`aether
// Create a basic neural network
const network = new NeuralNetwork();

// Add layers with neurons and activation functions
network.addLayer(128, "relu");    // Input layer
network.addLayer(64, "relu");     // Hidden layer
network.addLayer(32, "relu");     // Hidden layer
network.addLayer(10, "softmax");  // Output layer

// Configure training parameters
network.setLearningRate(0.001);
network.setOptimizer("adam");
network.setBatchSize(32);

// Train the network
const trainingData = lyrixa.loadDataset("my_data");
network.train(trainingData);

lyrixa.log("Neural network training complete!");
\`\`\`

**Key Points:**
- Use appropriate activation functions (relu for hidden, softmax/sigmoid for output)
- Configure learning rate and optimizer for best results
- Monitor training progress with callbacks
- Save trained models for later use

Would you like me to explain any specific part of this process?`;
    }

    // Memory related questions
    if (lowerQuestion.includes('memory') || lowerQuestion.includes('allocate')) {
      return `💾 **Memory Management in Aetherra**

Aetherra provides several types of memory for different use cases:

\`\`\`aether
// Standard memory allocation
const buffer = lyrixa.allocateMemory(1024);
lyrixa.log("Allocated: " + buffer.size + " bytes");

// Persistent memory (survives between sessions)
const persistent = lyrixa.createPersistentMemory("model_cache", 1024 * 1024);
persistent.store("my_model", modelWeights);

// Vectorized memory for embeddings
const vectorStore = lyrixa.createVectorMemory(512);
vectorStore.addVector("concept1", embedding);

// Memory monitoring
const info = lyrixa.getMemoryInfo();
lyrixa.log("Free memory: " + info.free + " bytes");

// Cleanup
buffer.deallocate();
\`\`\`

**Best Practices:**
- Use persistent memory for AI models and large datasets
- Enable auto-management for prototyping
- Monitor memory usage in production
- Use vectorized memory for similarity search

Need help with a specific memory operation?`;
    }

    // Plugin related questions
    if (lowerQuestion.includes('plugin') || lowerQuestion.includes('develop')) {
      return `🔌 **Plugin Development Guide**

Creating plugins in Aetherra is straightforward! Here's a minimal plugin:

\`\`\`aether
// main.aether
const plugin = {
  name: "my-awesome-plugin",
  version: "1.0.0",
  
  initialize: function() {
    lyrixa.log("Plugin " + this.name + " initialized!");
    return true;
  },
  
  process: function(input, options) {
    // Your plugin logic here
    const result = this.enhanceData(input);
    return result;
  },
  
  enhanceData: function(data) {
    // Example: neural enhancement
    const network = new NeuralNetwork();
    network.addLayer(256, "relu");
    network.addLayer(128, "relu");
    
    return network.process(data);
  },
  
  cleanup: function() {
    lyrixa.log("Plugin cleanup completed");
  }
};

module.exports = plugin;
\`\`\`

**Plugin Manifest (plugin.manifest.json):**
\`\`\`json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "description": "An AI-powered enhancement plugin",
  "author": "Your Name",
  "entry_point": "main.aether",
  "capabilities": ["neural_processing"]
}
\`\`\`

Want me to explain plugin testing or submission process?`;
    }

    // Quantum computing questions
    if (lowerQuestion.includes('quantum') || lowerQuestion.includes('qubit')) {
      return `⚛️ **Quantum Computing in Aetherra**

Aetherra provides built-in quantum computing capabilities:

\`\`\`aether
// Create quantum qubits
const qubits = quantum.createQubits(4);
lyrixa.log("Created " + qubits.length + " qubits");

// Apply quantum gates
quantum.hadamard(qubits[0]);        // Superposition
quantum.pauli_x(qubits[1]);         // NOT gate
quantum.cnot(qubits[0], qubits[2]); // Controlled-NOT

// Create entanglement
quantum.entangle(qubits[0], qubits[1]);
lyrixa.log("Qubits entangled!");

// Measure quantum states
const measurements = quantum.measure(qubits);
lyrixa.log("Measurements: " + measurements.join(", "));

// Quantum algorithms
@quantum
function quantumSearch(database, target) {
  // Grover's algorithm implementation
  return quantum.grovers(database, target);
}
\`\`\`

**Quantum Features:**
- Qubit creation and manipulation
- Standard quantum gates (Hadamard, Pauli, CNOT)
- Entanglement operations
- Measurement and state collapse
- Built-in quantum algorithms

Interested in a specific quantum algorithm or operation?`;
    }

    // Getting started questions
    if (lowerQuestion.includes('start') || lowerQuestion.includes('begin') || lowerQuestion.includes('first')) {
      return `🚀 **Getting Started with Aetherra**

Welcome to the AI-Native future! Here's your quickstart guide:

**1. Your First .aether Program:**
\`\`\`aether
// Hello Neural World!
lyrixa.log("Welcome to Aetherra OS!");

const message = "AI-Native computing is here";
lyrixa.log(message);
\`\`\`

**2. Basic Neural Network:**
\`\`\`aether
// Create a simple classifier
const network = new NeuralNetwork();
network.addLayer(64, "relu");
network.addLayer(10, "softmax");

lyrixa.log("Your first neural network is ready!");
\`\`\`

**3. Memory Management:**
\`\`\`aether
// Allocate some memory
const buffer = lyrixa.allocateMemory(1024);
lyrixa.log("Memory allocated: " + buffer.size + " bytes");
\`\`\`

**4. Load a Plugin:**
\`\`\`aether
// Enhance your capabilities
const optimizer = lyrixa.loadPlugin("performance_optimizer");
optimizer.optimize();
\`\`\`

**Next Steps:**
- Explore the [.aether Language Reference](aether-lang)
- Learn about [Memory Architecture](memory-system)
- Try building your first [Plugin](plugin-guide)

What would you like to explore first?`;
    }

    // Syntax questions
    if (lowerQuestion.includes('syntax') || lowerQuestion.includes('language') || lowerQuestion.includes('aether')) {
      return `⚡ **.aether Language Syntax**

The .aether language is designed for AI-native programming. Here are the key concepts:

**Variables & Functions:**
\`\`\`aether
// Constants and variables
const neuralPower = 42;
let systemState = "active";

// Function definition
function processData(input) {
  return input.transform();
}

// Neural-optimized function
@neural
function aiEnhance(data) {
  return neuralTransform(data);
}
\`\`\`

**Core APIs:**
\`\`\`aether
// Logging
lyrixa.log("Debug message");
lyrixa.warn("Warning message");
lyrixa.error("Error message");

// Memory operations
const buffer = lyrixa.allocateMemory(size);
const info = lyrixa.getMemoryInfo();

// Plugin system
const plugin = lyrixa.loadPlugin("plugin_name");
\`\`\`

**Neural Networks:**
\`\`\`aether
const network = new NeuralNetwork();
network.addLayer(neurons, activation);
network.train(data);
\`\`\`

**Quantum Operations:**
\`\`\`aether
const qubits = quantum.createQubits(count);
quantum.hadamard(qubit);
quantum.measure(qubits);
\`\`\`

Need help with a specific syntax element?`;
    }

    // Default contextual response
    return generateContextualResponse(question, section);
  };

  const generateContextualResponse = (question: string, section: string): string => {
    const responses = [
      `That's a great question about ${section}! Let me break this down for you:

Based on the current documentation section, here are the key points to consider:

• **Core Concept**: The fundamental idea behind this feature
• **Implementation**: How to actually use it in your code
• **Best Practices**: Recommended approaches for optimal results
• **Common Pitfalls**: What to avoid when working with this

Would you like me to elaborate on any of these aspects?`,

      `Excellent question! In the context of ${section}, this is particularly important because:

**Understanding the Basics:**
The core principle here involves understanding how Aetherra's AI-native architecture handles this specific functionality.

**Practical Application:**
Here's how you'd typically approach this in a real-world scenario:

1. Start with the basic implementation
2. Consider performance optimizations
3. Think about integration with other Aetherra features
4. Plan for scalability and maintenance

What specific aspect would you like me to focus on?`,

      `I'd be happy to help you understand this better! This is actually one of the more interesting aspects of ${section}.

**Key Insight:**
What makes this special in Aetherra is how it integrates with the neural-native architecture.

**Example Scenario:**
Let me give you a practical example of how this might be used:

\`\`\`aether
// Example implementation
const example = new AetherraFeature();
example.configure(options);
const result = example.process(data);
lyrixa.log("Result: " + result);
\`\`\`

This demonstrates the typical pattern you'll see throughout Aetherra's API design.

Would you like me to show you more advanced examples or explain the underlying concepts?`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  const getContextualSuggestions = (lastQuestion: string, section: string): string[] => {
    const suggestions = [
      "Can you show me a more advanced example?",
      "What are the performance considerations?",
      "How does this integrate with other Aetherra features?",
      "What are common mistakes to avoid?",
      "Are there any alternatives to this approach?",
      "Can you explain the underlying concepts?"
    ];

    return suggestions.slice(0, 4);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(currentInput);
    }
  };

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="h-full bg-gray-800 border-l border-gray-700 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <motion.span 
            className="text-2xl"
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            🤖
          </motion.span>
          <div>
            <h3 className="font-semibold text-white">AI Assistant</h3>
            <p className="text-xs text-gray-400">Context-aware help for {currentSection}</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            title="Close Assistant"
          >
            ✕
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-green-400/20 text-green-100 border border-green-400/30'
                    : 'bg-gray-700 text-gray-100'
                }`}
              >
                <div className="prose prose-sm prose-invert max-w-none">
                  {message.content.split('```').map((part, index) => {
                    if (index % 2 === 1) {
                      // Code block
                      const lines = part.split('\n');
                      const language = lines[0];
                      const code = lines.slice(1).join('\n');
                      
                      return (
                        <div key={index} className="my-2">
                          <div className="bg-gray-900 rounded-lg border border-gray-600 overflow-hidden">
                            <div className="px-3 py-1 bg-gray-800 border-b border-gray-600 text-xs text-gray-400">
                              {language || 'code'}
                            </div>
                            <pre className="p-3 text-sm text-gray-300 overflow-x-auto">
                              <code>{code}</code>
                            </pre>
                          </div>
                        </div>
                      );
                    } else {
                      // Regular text
                      return (
                        <div key={index} className="whitespace-pre-wrap text-sm">
                          {part.split('**').map((textPart, textIndex) => 
                            textIndex % 2 === 1 ? (
                              <strong key={textIndex} className="font-semibold text-white">
                                {textPart}
                              </strong>
                            ) : (
                              textPart
                            )
                          )}
                        </div>
                      );
                    }
                  })}
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex justify-start"
            >
              <div className="bg-gray-700 p-3 rounded-lg">
                <div className="flex space-x-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{
                        duration: 0.6,
                        repeat: Infinity,
                        delay: i * 0.2
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {suggestedQuestions.length > 0 && (
        <div className="p-4 border-t border-gray-700">
          <p className="text-xs text-gray-400 mb-2">Suggested questions:</p>
          <div className="space-y-1">
            {suggestedQuestions.slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(question)}
                className="w-full text-left text-xs text-gray-300 hover:text-white hover:bg-gray-700 p-2 rounded transition-colors"
              >
                💡 {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about Aetherra..."
            className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-green-400 text-sm"
            disabled={isTyping}
          />
          <button
            onClick={() => handleSendMessage(currentInput)}
            disabled={!currentInput.trim() || isTyping}
            className="px-3 py-2 bg-green-400 text-black rounded font-medium hover:bg-green-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ➤
          </button>
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>Press Enter to send</span>
          <span>{messages.length} messages</span>
        </div>
      </div>
    </motion.div>
  );
}
