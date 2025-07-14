import React, { useState } from "react";
import { motion } from "framer-motion";
import CodeEditor from "../components/CodeEditor";
import ScriptExecutionPanel from "../components/ScriptExecutionPanel";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut"
    }
  }
};

const exampleScripts = [
  {
    name: "Hello Aetherra",
    description: "Basic plugin initialization",
    code: `// Welcome to AetherScript!
plugin 'hello-aetherra' {
  initialize() {
    console.log('Hello from Aetherra!');
    console.log('AI-native computing is here');
  }
}`
  },
  {
    name: "Neural Optimizer",
    description: "Performance optimization plugin",
    code: `// Neural pathway optimization
plugin 'neural-optimizer' {
  initialize() {
    console.log('Neural Optimizer v2.1.4 loaded');
    this.optimizePathways();
    this.consolidateMemory();
  }
  
  optimizePathways() {
    neural.analyze();
    neural.optimize();
    console.log('Neural pathways optimized');
  }
  
  consolidateMemory() {
    memory.compress();
    memory.defragment();
    console.log('Memory consolidated');
  }
}`
  },
  {
    name: "AI Assistant",
    description: "Intelligent assistant plugin",
    code: `// AI Assistant Plugin
plugin 'ai-assistant' {
  initialize() {
    console.log('AI Assistant initialized');
    this.loadPersonality();
    this.enableLearning();
  }
  
  loadPersonality() {
    ai.setPersonality('helpful');
    ai.setEmpathy(0.8);
    console.log('Personality matrix loaded');
  }
  
  enableLearning() {
    ai.enableAdaptiveLearning();
    ai.setConfidenceThreshold(0.75);
    console.log('Learning engine activated');
  }
}`
  }
];

export default function AetherScriptPlayground() {
  const [script, setScript] = useState(exampleScripts[0].code);
  const [selectedExample, setSelectedExample] = useState(0);

  const loadExample = (index: number) => {
    setSelectedExample(index);
    setScript(exampleScripts[index].code);
  };

  return (
    <div className="min-h-screen bg-aetherra-dark text-white">
      {/* Hero Header */}
      <motion.section 
        className="bg-gradient-to-br from-aetherra-dark via-aetherra-gray to-aetherra-dark border-b border-aetherra-green/20 py-16"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-6">
            ⚡ AetherScript Playground
          </h1>
          <p className="text-xl text-zinc-300 mb-8 max-w-3xl mx-auto">
            Experience the power of .aether scripting language. Write, test, and execute 
            AI-native code that directly interfaces with Aetherra's core systems.
          </p>
          
          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-aetherra-gray p-4 rounded-lg border border-aetherra-green/20">
              <div className="text-2xl mb-2">🧠</div>
              <h3 className="font-semibold text-aetherra-green mb-1">AI-Native Syntax</h3>
              <p className="text-sm text-zinc-400">Built for artificial intelligence from the ground up</p>
            </div>
            <div className="bg-aetherra-gray p-4 rounded-lg border border-blue-500/20">
              <div className="text-2xl mb-2">🔌</div>
              <h3 className="font-semibold text-blue-400 mb-1">Plugin Architecture</h3>
              <p className="text-sm text-zinc-400">Modular system for extending functionality</p>
            </div>
            <div className="bg-aetherra-gray p-4 rounded-lg border border-purple-500/20">
              <div className="text-2xl mb-2">⚡</div>
              <h3 className="font-semibold text-purple-400 mb-1">Real-time Execution</h3>
              <p className="text-sm text-zinc-400">Instant feedback and performance metrics</p>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Main Content */}
      <motion.main 
        className="max-w-7xl mx-auto px-6 py-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Example Scripts */}
        <motion.section variants={itemVariants} className="mb-8">
          <h2 className="text-2xl font-bold gradient-text mb-6">📚 Example Scripts</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {exampleScripts.map((example, index) => (
              <motion.button
                key={index}
                onClick={() => loadExample(index)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`p-4 rounded-lg border text-left transition-all ${
                  selectedExample === index
                    ? 'bg-aetherra-green/10 border-aetherra-green'
                    : 'bg-aetherra-gray border-zinc-700 hover:border-aetherra-green/50'
                }`}
              >
                <h3 className="font-semibold text-zinc-200 mb-2">{example.name}</h3>
                <p className="text-sm text-zinc-400">{example.description}</p>
              </motion.button>
            ))}
          </div>
        </motion.section>

        {/* Code Editor and Execution */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Code Editor */}
          <motion.section variants={itemVariants}>
            <div className="mb-4">
              <h2 className="text-2xl font-bold gradient-text mb-2">💻 Code Editor</h2>
              <p className="text-zinc-400">Write your .aether scripts with syntax highlighting and autocomplete</p>
            </div>
            <CodeEditor 
              language="aether" 
              code={script} 
              onChange={setScript} 
            />
            
            {/* Quick Actions */}
            <div className="mt-4 flex flex-wrap gap-2">
              <button 
                onClick={() => setScript("")}
                className="px-3 py-1 text-sm bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded transition-colors"
              >
                🗑️ Clear
              </button>
              <button 
                onClick={() => {
                  const formattedScript = script
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line)
                    .join('\n');
                  setScript(formattedScript);
                }}
                className="px-3 py-1 text-sm bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded transition-colors"
              >
                🎨 Format
              </button>
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(script);
                }}
                className="px-3 py-1 text-sm bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded transition-colors"
              >
                📋 Copy
              </button>
            </div>
          </motion.section>

          {/* Execution Panel */}
          <motion.section variants={itemVariants}>
            <div className="mb-4">
              <h2 className="text-2xl font-bold gradient-text mb-2">🚀 Script Execution</h2>
              <p className="text-zinc-400">Run your code and see real-time output from the AetherScript runtime</p>
            </div>
            <ScriptExecutionPanel script={script} />
          </motion.section>
        </div>

        {/* Documentation */}
        <motion.section variants={itemVariants} className="mt-16">
          <h2 className="text-3xl font-bold gradient-text mb-8 text-center">📖 AetherScript Reference</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Syntax Guide */}
            <div className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20">
              <h3 className="text-xl font-semibold text-aetherra-green mb-4">Language Syntax</h3>
              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-semibold text-zinc-200 mb-2">Plugin Declaration</h4>
                  <code className="block bg-aetherra-dark p-2 rounded text-aetherra-green font-mono">
                    plugin 'name' {`{ ... }`}
                  </code>
                </div>
                <div>
                  <h4 className="font-semibold text-zinc-200 mb-2">Method Definition</h4>
                  <code className="block bg-aetherra-dark p-2 rounded text-aetherra-green font-mono">
                    methodName() {`{ ... }`}
                  </code>
                </div>
                <div>
                  <h4 className="font-semibold text-zinc-200 mb-2">AI API Calls</h4>
                  <code className="block bg-aetherra-dark p-2 rounded text-aetherra-green font-mono">
                    ai.method() / neural.action()
                  </code>
                </div>
              </div>
            </div>

            {/* Built-in Modules */}
            <div className="bg-aetherra-gray p-6 rounded-xl border border-blue-500/20">
              <h3 className="text-xl font-semibold text-blue-400 mb-4">Built-in Modules</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="font-mono text-aetherra-green">ai.*</span>
                  <span className="text-zinc-400">AI operations</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-aetherra-green">neural.*</span>
                  <span className="text-zinc-400">Neural networks</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-aetherra-green">memory.*</span>
                  <span className="text-zinc-400">Memory management</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-aetherra-green">plugin.*</span>
                  <span className="text-zinc-400">Plugin system</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-aetherra-green">console.*</span>
                  <span className="text-zinc-400">Output & logging</span>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Call to Action */}
        <motion.section variants={itemVariants} className="mt-16">
          <div className="bg-gradient-to-r from-aetherra-green/20 to-blue-500/20 p-8 rounded-xl border border-aetherra-green/30 text-center">
            <h2 className="text-2xl font-bold gradient-text mb-4">
              🚀 Ready to Build Something Amazing?
            </h2>
            <p className="text-zinc-300 mb-6">
              AetherScript is the future of AI-native programming. Start building intelligent systems today.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-aetherra-green text-aetherra-dark rounded-lg font-semibold hover:bg-aetherra-green/90 transition-colors"
              >
                📖 View Full Documentation
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 transition-colors"
              >
                💻 Download SDK
              </motion.button>
            </div>
          </div>
        </motion.section>
      </motion.main>
    </div>
  );
}
