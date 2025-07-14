import React, { useState } from "react";
import { motion } from "framer-motion";

interface ScriptExecutionPanelProps {
  script: string;
}

export default function ScriptExecutionPanel({ script }: ScriptExecutionPanelProps) {
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [executionTime, setExecutionTime] = useState(0);

  const runScript = async () => {
    setIsRunning(true);
    setOutput("🚀 Initializing AetherScript runtime...\n");
    
    const startTime = Date.now();
    
    // Simulate script analysis and execution
    await new Promise(resolve => setTimeout(resolve, 500));
    setOutput(prev => prev + "📋 Parsing .aether syntax...\n");
    
    await new Promise(resolve => setTimeout(resolve, 300));
    setOutput(prev => prev + "🔧 Loading Aetherra core modules...\n");
    
    await new Promise(resolve => setTimeout(resolve, 400));
    setOutput(prev => prev + "⚡ Executing script...\n\n");
    
    // Analyze script content and generate contextual output
    const lines = script.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      await new Promise(resolve => setTimeout(resolve, 100));
      
      if (line.includes('plugin')) {
        const pluginMatch = line.match(/'([^']+)'/);
        const pluginName = pluginMatch ? pluginMatch[1] : 'unknown';
        setOutput(prev => prev + `🔌 Loading plugin: ${pluginName}\n`);
      } else if (line.includes('initialize')) {
        setOutput(prev => prev + `⚙️  Calling initialize() method\n`);
      } else if (line.includes('console.log')) {
        const logMatch = line.match(/'([^']+)'/);
        const logMessage = logMatch ? logMatch[1] : 'Debug output';
        setOutput(prev => prev + `📝 ${logMessage}\n`);
      } else if (line.includes('neural')) {
        setOutput(prev => prev + `🧠 Neural pathway optimization: +12% efficiency\n`);
      } else if (line.includes('memory')) {
        setOutput(prev => prev + `💾 Memory consolidation: 2.3GB → 1.8GB\n`);
      } else if (line.includes('ai') || line.includes('AI')) {
        setOutput(prev => prev + `🤖 AI module status: ACTIVE\n`);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 200));
    const endTime = Date.now();
    setExecutionTime(endTime - startTime);
    
    setOutput(prev => prev + `\n✅ Script executed successfully!\n`);
    setOutput(prev => prev + `⏱️  Execution time: ${endTime - startTime}ms\n`);
    setOutput(prev => prev + `📊 Memory usage: 127MB\n`);
    setOutput(prev => prev + `🔋 Performance score: 94.7%\n`);
    
    setIsRunning(false);
  };

  const clearOutput = () => {
    setOutput("");
    setExecutionTime(0);
  };

  return (
    <div className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold gradient-text">AetherScript Console</h3>
        <div className="flex items-center space-x-3">
          {executionTime > 0 && (
            <span className="text-xs text-zinc-400">
              Last run: {executionTime}ms
            </span>
          )}
          <div className="flex space-x-2">
            <motion.button
              onClick={runScript}
              disabled={isRunning || !script.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                isRunning || !script.trim()
                  ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed'
                  : 'bg-aetherra-green hover:bg-aetherra-green/90 text-aetherra-dark'
              }`}
            >
              {isRunning ? (
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 border-2 border-aetherra-dark border-t-transparent rounded-full animate-spin"></div>
                  <span>Running...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span>▶️</span>
                  <span>Execute Script</span>
                </div>
              )}
            </motion.button>
            
            <motion.button
              onClick={clearOutput}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-3 py-2 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded-lg text-sm transition-colors"
            >
              🗑️ Clear
            </motion.button>
          </div>
        </div>
      </div>

      {/* Output Console */}
      <div className="bg-aetherra-dark rounded-lg border border-zinc-700">
        {/* Console Header */}
        <div className="flex items-center justify-between bg-zinc-800 px-4 py-2 rounded-t-lg border-b border-zinc-700">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
            <span className="text-xs text-zinc-400">AetherScript Runtime Console</span>
          </div>
          <span className="text-xs text-zinc-500 font-mono">aetherra://localhost:3000</span>
        </div>
        
        {/* Console Output */}
        <pre className="p-4 text-sm font-mono text-aetherra-green min-h-[200px] max-h-[400px] overflow-y-auto whitespace-pre-wrap">
          {output || "🎯 Ready to execute .aether scripts\n💡 Click 'Execute Script' to run your code"}
        </pre>
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between mt-4 text-xs text-zinc-500">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-yellow-400 animate-pulse' : output ? 'bg-green-400' : 'bg-zinc-600'}`}></div>
            <span>{isRunning ? 'Running' : output ? 'Ready' : 'Idle'}</span>
          </span>
          <span>Runtime: AetherScript v2.1.4</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>Memory: 127MB</span>
          <span>CPU: {isRunning ? '87%' : '12%'}</span>
        </div>
      </div>
    </div>
  );
}
