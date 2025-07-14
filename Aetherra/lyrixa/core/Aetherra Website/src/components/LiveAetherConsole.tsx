import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTerminalTheme, terminalComponentStyles } from '../utils/TerminalTheme'

interface TerminalLine {
  id: string;
  type: 'command' | 'output' | 'error' | 'system';
  content: string;
  timestamp: Date;
}

interface LiveAetherConsoleProps {
  onClose?: () => void;
  initialScript?: string;
  theme?: 'default' | 'cyberpunk' | 'matrix';
}

export default function LiveAetherConsole({ 
  onClose, 
  initialScript = '', 
  theme = 'default' 
}: LiveAetherConsoleProps) {
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isFullscreen, setIsFullscreen] = useState(true);
  const [showBootSequence, setShowBootSequence] = useState(true);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const { theme: terminalTheme, css } = useTerminalTheme(theme);

  useEffect(() => {
    // Initialize terminal with boot sequence
    initializeTerminal();
    
    // Focus input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new lines are added
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  useEffect(() => {
    // Load initial script if provided
    if (initialScript) {
      setTimeout(() => {
        setCurrentInput(initialScript);
      }, 2000);
    }
  }, [initialScript]);

  const initializeTerminal = () => {
    const bootLines: TerminalLine[] = [
      { id: 'boot_1', type: 'system', content: 'Aetherra Neural Terminal v2.1.0', timestamp: new Date() },
      { id: 'boot_2', type: 'system', content: 'Initializing Lyrixa Runtime...', timestamp: new Date() },
      { id: 'boot_3', type: 'system', content: 'Loading Neural Network Modules...', timestamp: new Date() },
      { id: 'boot_4', type: 'system', content: 'Establishing Quantum Bridge Connection...', timestamp: new Date() },
      { id: 'boot_5', type: 'system', content: 'Ready for AetherScript execution.', timestamp: new Date() },
      { id: 'boot_6', type: 'output', content: '', timestamp: new Date() },
      { id: 'boot_7', type: 'output', content: 'Welcome to the Live Aether Console!', timestamp: new Date() },
      { id: 'boot_8', type: 'output', content: 'Type "help" for available commands, or start writing .aether scripts.', timestamp: new Date() },
      { id: 'boot_9', type: 'output', content: '', timestamp: new Date() }
    ];

    // Animate boot sequence
    bootLines.forEach((line, index) => {
      setTimeout(() => {
        setLines(prev => [...prev, line]);
        if (index === bootLines.length - 1) {
          setShowBootSequence(false);
        }
      }, index * 200);
    });
  };

  const addLine = (type: TerminalLine['type'], content: string) => {
    const newLine: TerminalLine = {
      id: `line_${Date.now()}_${Math.random()}`,
      type,
      content,
      timestamp: new Date()
    };
    setLines(prev => [...prev, newLine]);
  };

  const executeCommand = async (command: string) => {
    if (!command.trim()) return;

    // Add command to history
    setCommandHistory(prev => [...prev, command]);
    setHistoryIndex(-1);

    // Add command line to terminal
    addLine('command', `aether> ${command}`);
    setCurrentInput('');
    setIsExecuting(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 100)); // Small delay for UI

      // Handle built-in commands
      if (command.toLowerCase() === 'help') {
        handleHelpCommand();
      } else if (command.toLowerCase() === 'clear') {
        handleClearCommand();
      } else if (command.toLowerCase().startsWith('theme ')) {
        handleThemeCommand(command);
      } else if (command.toLowerCase() === 'examples') {
        handleExamplesCommand();
      } else if (command.toLowerCase() === 'version') {
        handleVersionCommand();
      } else {
        // Execute AetherScript
        await executeAetherScript(command);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      addLine('error', `Error: ${errorMessage}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const executeAetherScript = async (script: string) => {
    // Simulate script execution with realistic delay
    const executionTime = 200 + Math.random() * 1000;
    await new Promise(resolve => setTimeout(resolve, executionTime));

    // Parse and execute script
    const lines = script.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      
      if (trimmedLine.startsWith('//') || !trimmedLine) {
        continue; // Skip comments and empty lines
      }

      if (trimmedLine.includes('lyrixa.log(')) {
        // Handle log statements
        const match = trimmedLine.match(/lyrixa\.log\(['"`]([^'"`]*)['"`]\)/);
        if (match) {
          addLine('output', `[LOG] ${match[1]}`);
        }
      } else if (trimmedLine.includes('const ') || trimmedLine.includes('let ')) {
        // Handle variable declarations
        const varMatch = trimmedLine.match(/(const|let)\s+(\w+)/);
        if (varMatch) {
          addLine('output', `[RUNTIME] Variable '${varMatch[2]}' declared`);
        }
      } else if (trimmedLine.includes('allocateMemory')) {
        // Handle memory allocation
        const memMatch = trimmedLine.match(/allocateMemory\((\d+)\)/);
        if (memMatch) {
          addLine('output', `[MEMORY] Allocated ${memMatch[1]} bytes`);
        }
      } else if (trimmedLine.includes('loadPlugin')) {
        // Handle plugin loading
        const pluginMatch = trimmedLine.match(/loadPlugin\(['"`]([^'"`]*)['"`]\)/);
        if (pluginMatch) {
          addLine('output', `[PLUGIN] Loaded '${pluginMatch[1]}' successfully`);
        }
      } else if (trimmedLine.includes('neuralNetwork')) {
        // Handle neural network operations
        addLine('output', '[NEURAL] Neural network operation executed');
      } else if (trimmedLine.includes('quantum')) {
        // Handle quantum operations
        addLine('output', '[QUANTUM] Quantum operation completed');
      } else if (trimmedLine.includes('optimize()')) {
        // Handle optimization calls
        addLine('output', '[OPTIMIZER] Performance optimization complete');
      } else {
        // Generic execution feedback
        addLine('output', `[EXEC] ${trimmedLine}`);
      }

      // Small delay between line executions
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    addLine('output', `[RUNTIME] Script execution completed in ${executionTime.toFixed(0)}ms`);
  };

  const handleHelpCommand = () => {
    const helpText = `
Available Commands:
  help          - Show this help message
  clear         - Clear the terminal screen
  theme <name>  - Change terminal theme (default, cyberpunk, matrix)
  examples      - Show example AetherScript code
  version       - Show system version information
  exit          - Exit fullscreen mode

AetherScript Syntax:
  // Comments start with double slash
  const memory = lyrixa.allocateMemory(1024);
  lyrixa.log("Hello Neural World!");
  const optimizer = lyrixa.loadPlugin("neural_optimizer");
  optimizer.optimize();

Neural Operations:
  neuralNetwork.train(data);
  quantum.entangle(qubit1, qubit2);
  memory.optimize();
  runtime.profile();
    `;
    addLine('output', helpText);
  };

  const handleClearCommand = () => {
    setLines([]);
  };

  const handleThemeCommand = (command: string) => {
    const themeName = command.split(' ')[1];
    if (['default', 'cyberpunk', 'matrix'].includes(themeName)) {
      addLine('output', `[SYSTEM] Theme changed to '${themeName}'`);
      // Theme change would be handled by parent component
    } else {
      addLine('error', 'Invalid theme. Available themes: default, cyberpunk, matrix');
    }
  };

  const handleExamplesCommand = () => {
    const examples = `
Example AetherScript Code:

1. Basic Neural Network:
   const network = new NeuralNetwork();
   network.addLayer(128, 'relu');
   network.addLayer(64, 'relu');
   network.addLayer(10, 'softmax');
   lyrixa.log("Network created with " + network.layers.length + " layers");

2. Memory Management:
   const memory = lyrixa.allocateMemory(2048);
   lyrixa.log("Allocated " + memory.size + " bytes");
   memory.deallocate();

3. Plugin Loading:
   const optimizer = lyrixa.loadPlugin("performance_optimizer");
   const visualizer = lyrixa.loadPlugin("neural_visualizer");
   optimizer.optimize();
   visualizer.render();

4. Quantum Operations:
   const qubits = quantum.createQubits(4);
   quantum.entangle(qubits[0], qubits[1]);
   quantum.measure(qubits);

Try copying and pasting any of these examples!
    `;
    addLine('output', examples);
  };

  const handleVersionCommand = () => {
    const versionInfo = `
Aetherra Neural Terminal v2.1.0
Lyrixa Runtime: v2.1.0
Neural Engine: v3.2.1
Quantum Bridge: v1.0.5
Memory Manager: v2.0.3

Build: 2025.07.13.001
Architecture: x64
Platform: Neural-Native
    `;
    addLine('output', versionInfo);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isExecuting) {
      executeCommand(currentInput);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex !== -1) {
        const newIndex = historyIndex === commandHistory.length - 1 ? -1 : historyIndex + 1;
        setHistoryIndex(newIndex);
        setCurrentInput(newIndex === -1 ? '' : commandHistory[newIndex]);
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // TODO: Implement auto-completion
    } else if (e.key === 'Escape' && onClose) {
      onClose();
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const getLineStyle = (type: TerminalLine['type']) => {
    switch (type) {
      case 'command':
        return terminalComponentStyles.input(terminalTheme);
      case 'error':
        return terminalComponentStyles.error(terminalTheme);
      case 'system':
        return terminalComponentStyles.info(terminalTheme);
      default:
        return terminalComponentStyles.output(terminalTheme);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`fixed inset-0 z-50 ${isFullscreen ? 'bg-black' : 'bg-gray-900 m-4 rounded-xl border border-gray-700'}`}
      style={terminalComponentStyles.container(terminalTheme)}
    >
      {/* CSS Injection for terminal effects */}
      <style dangerouslySetInnerHTML={{ __html: css }} />

      {/* Scanline overlay */}
      <div className="absolute inset-0 pointer-events-none terminal-scanlines opacity-10" />

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">⚡</div>
          <div>
            <h1 className="text-lg font-bold terminal-text">Live Aether Console</h1>
            <p className="text-xs terminal-text-dim">Neural-Native Scripting Terminal</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="terminal-button"
            title="Toggle Fullscreen"
          >
            {isFullscreen ? '🗗' : '🗖'}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="terminal-button"
              title="Close (ESC)"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div 
        ref={terminalRef}
        className="flex-1 overflow-y-auto terminal-scrollbar"
        style={{ padding: '20px' }}
      >
        {/* Boot sequence animation */}
        <AnimatePresence>
          {showBootSequence && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mb-4"
            >
              <div className="terminal-flicker terminal-text">
                Initializing Neural Terminal...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Terminal lines */}
        <div className="space-y-1">
          {lines.map((line, index) => (
            <motion.div
              key={line.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
              className="flex items-start space-x-3"
            >
              <span className="text-xs terminal-text-dim w-16 flex-shrink-0">
                {formatTimestamp(line.timestamp)}
              </span>
              <span 
                className="flex-1 terminal-output"
                style={getLineStyle(line.type)}
              >
                {line.content}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Current input line */}
        <div className="flex items-center space-x-3 mt-4">
          <span className="text-xs terminal-text-dim w-16 flex-shrink-0">
            {formatTimestamp(new Date())}
          </span>
          <span style={terminalComponentStyles.prompt(terminalTheme)}>
            aether&gt;
          </span>
          <input
            ref={inputRef}
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isExecuting}
            className="flex-1 terminal-input"
            style={terminalComponentStyles.input(terminalTheme)}
            placeholder={isExecuting ? "Executing..." : "Enter AetherScript command..."}
            autoComplete="off"
            spellCheck={false}
          />
          {isExecuting && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
            />
          )}
        </div>

        {/* Cursor blink effect */}
        <motion.div
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="inline-block w-2 h-5 terminal-cursor ml-1 mt-1"
        />
      </div>

      {/* Status bar */}
      <div className="border-t border-gray-700 p-2 text-xs terminal-text-dim">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span>Theme: {theme}</span>
            <span>Lines: {lines.length}</span>
            <span>History: {commandHistory.length}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Ready</span>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
