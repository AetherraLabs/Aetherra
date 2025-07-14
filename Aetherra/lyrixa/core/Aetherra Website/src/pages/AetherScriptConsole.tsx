import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import AutoCompleteHelper from '../components/AutoCompleteHelper'
import ExecutionHistoryPanel from '../components/ExecutionHistoryPanel'
import ScriptIOPanel from '../components/ScriptIOPanel'
import { ScriptValidator } from '../utils/ScriptValidator'

interface AetherScriptConsoleProps {
  // Optional props for integration
}

interface ExecutionState {
  isExecuting: boolean;
  currentScript: string;
  output: string;
  memoryContext: any;
  startTime?: Date;
}

export default function AetherScriptConsole({}: AetherScriptConsoleProps) {
  const [script, setScript] = useState('');
  const [executionState, setExecutionState] = useState<ExecutionState>({
    isExecuting: false,
    currentScript: '',
    output: '',
    memoryContext: null
  });
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [validationErrors, setValidationErrors] = useState<any[]>([]);
  const [cursorPosition, setCursorPosition] = useState({ line: 0, column: 0 });
  const [layout, setLayout] = useState<'horizontal' | 'vertical'>('horizontal');
  
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const validator = useRef(new ScriptValidator());

  useEffect(() => {
    // Initialize with sample script
    const sampleScript = `// Welcome to AetherScript Console
// Neural-native scripting for the Aetherra OS

const lyrixa = new LyrixaCore();
lyrixa.log("Hello from the neural dimension!");

// Memory allocation example
const memory = lyrixa.allocateMemory(1024);
lyrixa.log(\`Allocated \${memory.size} bytes\`);

// Plugin loading example
const optimizer = lyrixa.loadPlugin("performance_optimizer");
optimizer.optimize();

lyrixa.log("Script execution complete!");`;
    
    setScript(sampleScript);
    validateScript(sampleScript);
  }, []);

  const validateScript = async (scriptContent: string) => {
    try {
      const result = await validator.current.validate(scriptContent);
      setValidationErrors(result.errors);
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const executeScript = async () => {
    if (executionState.isExecuting) return;

    setExecutionState(prev => ({
      ...prev,
      isExecuting: true,
      currentScript: script,
      output: '',
      startTime: new Date()
    }));

    try {
      // Simulate script execution
      const output = await simulateScriptExecution(script);
      
      setExecutionState(prev => ({
        ...prev,
        isExecuting: false,
        output: output.result,
        memoryContext: output.memoryContext
      }));

      // Add to execution history
      const duration = Date.now() - (executionState.startTime?.getTime() || Date.now());
      // This would typically call a history function from the ExecutionHistoryPanel
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setExecutionState(prev => ({
        ...prev,
        isExecuting: false,
        output: `Error: ${errorMessage}`
      }));
    }
  };

  const simulateScriptExecution = async (scriptContent: string): Promise<any> => {
    // Simulate execution delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // Parse script and generate realistic output
    const lines = scriptContent.split('\n').filter(line => 
      line.trim() && !line.trim().startsWith('//') && !line.trim().startsWith('const ') && !line.trim().startsWith('let ')
    );

    let output = '';
    const memoryAllocations = [];
    const pluginsLoaded = [];

    for (const line of lines) {
      if (line.includes('lyrixa.log(')) {
        const match = line.match(/lyrixa\.log\((.*)\)/);
        if (match) {
          const logContent = match[1].replace(/['"]/g, '');
          output += `[${new Date().toLocaleTimeString()}] ${logContent}\n`;
        }
      } else if (line.includes('allocateMemory')) {
        const match = line.match(/allocateMemory\((\d+)\)/);
        if (match) {
          const size = parseInt(match[1]);
          memoryAllocations.push(size);
          output += `[${new Date().toLocaleTimeString()}] Memory allocated: ${size} bytes\n`;
        }
      } else if (line.includes('loadPlugin')) {
        const match = line.match(/loadPlugin\(["']([^"']+)["']\)/);
        if (match) {
          const plugin = match[1];
          pluginsLoaded.push(plugin);
          output += `[${new Date().toLocaleTimeString()}] Plugin loaded: ${plugin}\n`;
        }
      } else if (line.includes('optimize()')) {
        output += `[${new Date().toLocaleTimeString()}] Performance optimization complete\n`;
      }
    }

    const totalMemory = memoryAllocations.reduce((sum, mem) => sum + mem, 0);
    
    return {
      result: output || `[${new Date().toLocaleTimeString()}] Script executed successfully\n`,
      memoryContext: {
        totalAllocated: totalMemory + 1024, // Base allocation
        totalUsed: Math.floor(totalMemory * 0.7),
        activeObjects: pluginsLoaded.length + 5,
        pluginAllocations: pluginsLoaded.reduce((acc, plugin) => {
          acc[plugin] = 256 + Math.floor(Math.random() * 512);
          return acc;
        }, {} as Record<string, number>)
      }
    };
  };

  const handleScriptChange = (value: string) => {
    setScript(value);
    validateScript(value);
    
    // Update cursor position for autocomplete
    if (editorRef.current) {
      const textarea = editorRef.current;
      const text = textarea.value.substring(0, textarea.selectionStart);
      const lines = text.split('\n');
      setCursorPosition({
        line: lines.length - 1,
        column: lines[lines.length - 1].length
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Handle autocomplete triggers
    if (e.key === '.' || (e.ctrlKey && e.key === ' ')) {
      setShowAutocomplete(true);
    } else if (e.key === 'Escape') {
      setShowAutocomplete(false);
    } else if (e.key === 'F5' || (e.ctrlKey && e.key === 'Enter')) {
      e.preventDefault();
      executeScript();
    }
  };

  const loadScriptFromHistory = (scriptContent: string) => {
    setScript(scriptContent);
    validateScript(scriptContent);
  };

  const clearConsole = () => {
    setExecutionState(prev => ({
      ...prev,
      output: ''
    }));
  };

  const toggleLayout = () => {
    setLayout(prev => prev === 'horizontal' ? 'vertical' : 'horizontal');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="min-h-screen bg-black text-white"
    >
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-aetherra-green">
              ⚡ AetherScript Console
            </h1>
            <span className="text-sm text-gray-400">
              Neural-Native Development Environment
            </span>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-sm">
              {validationErrors.length > 0 && (
                <div className="flex items-center space-x-1 text-yellow-400">
                  <span>⚠️</span>
                  <span>{validationErrors.length} issues</span>
                </div>
              )}
              <div className="text-gray-400">
                Lines: {script.split('\n').length}
              </div>
            </div>
            
            <button
              onClick={toggleLayout}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
              title="Toggle Layout"
            >
              {layout === 'horizontal' ? '📱' : '💻'}
            </button>
            
            <button
              onClick={executeScript}
              disabled={executionState.isExecuting}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                executionState.isExecuting
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-aetherra-green text-black hover:bg-green-400'
              }`}
            >
              {executionState.isExecuting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  <span>Executing...</span>
                </div>
              ) : (
                <>▶️ Execute (F5)</>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex h-[calc(100vh-80px)] ${
        layout === 'horizontal' ? 'flex-row' : 'flex-col'
      }`}>
        {/* Left Panel - Editor & History */}
        <div className={`${
          layout === 'horizontal' ? 'w-1/2' : 'h-1/2'
        } flex ${layout === 'horizontal' ? 'flex-col' : 'flex-row'}`}>
          {/* Script Editor */}
          <div className={`${
            layout === 'horizontal' ? 'h-2/3' : 'w-2/3'
          } p-4 border-r border-gray-700`}>
            <div className="h-full flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="text-lg font-semibold text-aetherra-green">
                  📝 Script Editor
                </span>
                <div className="flex items-center space-x-2 text-sm text-gray-400">
                  <span>Cursor: {cursorPosition.line + 1}:{cursorPosition.column + 1}</span>
                </div>
              </div>
              
              <div className="relative flex-1">
                <textarea
                  ref={editorRef}
                  value={script}
                  onChange={(e) => handleScriptChange(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full h-full bg-gray-900 border border-gray-700 rounded-xl p-4 text-white font-mono text-sm resize-none focus:outline-none focus:border-aetherra-green"
                  placeholder="Enter your .aether script here..."
                  spellCheck={false}
                />
                
                {/* Autocomplete */}
                {showAutocomplete && (
                  <div className="absolute z-10">
                    <AutoCompleteHelper
                      value={script}
                      onInsert={(completion: string) => {
                        // Handle completion insertion
                        setScript(prev => prev + completion);
                        setShowAutocomplete(false);
                      }}
                      onClose={() => setShowAutocomplete(false)}
                      cursorPosition={cursorPosition}
                      isVisible={showAutocomplete}
                    />
                  </div>
                )}
                
                {/* Validation Errors */}
                {validationErrors.length > 0 && (
                  <div className="absolute top-2 right-2 bg-yellow-900 border border-yellow-600 rounded p-2 max-w-sm">
                    <div className="text-xs text-yellow-300">
                      <div className="font-semibold mb-1">Validation Issues:</div>
                      {validationErrors.slice(0, 3).map((error, index) => (
                        <div key={index} className="mb-1">
                          Line {error.line}: {error.message}
                        </div>
                      ))}
                      {validationErrors.length > 3 && (
                        <div>+{validationErrors.length - 3} more...</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Execution History */}
          <div className={`${
            layout === 'horizontal' ? 'h-1/3' : 'w-1/3'
          } p-4 border-t border-gray-700`}>
            <ExecutionHistoryPanel
              onLoadScript={loadScriptFromHistory}
            />
          </div>
        </div>

        {/* Right Panel - I/O */}
        <div className={`${
          layout === 'horizontal' ? 'w-1/2' : 'h-1/2'
        } p-4`}>
          <ScriptIOPanel
            output={executionState.output}
            input={script}
            onInputChange={handleScriptChange}
            memoryContext={executionState.memoryContext}
            isExecuting={executionState.isExecuting}
          />
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-900 border-t border-gray-700 px-4 py-2 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span>🧠 Lyrixa Neural Runtime v2.1.0</span>
            <span>🔌 {Object.keys(executionState.memoryContext?.pluginAllocations || {}).length} plugins loaded</span>
            <span>💾 Memory: {executionState.memoryContext ? 
              `${Math.round(executionState.memoryContext.totalUsed / 1024)}KB used` : 
              '0KB used'
            }</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>Layout: {layout}</span>
            <span>Ready</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
