import React, { useState, useEffect } from 'react'

interface CompletionItem {
  label: string;
  detail: string;
  documentation: string;
  type: 'keyword' | 'function' | 'variable' | 'type' | 'snippet';
  insertText: string;
}

interface AutoCompleteHelperProps {
  value: string;
  cursorPosition: { line: number; column: number };
  onInsert: (text: string) => void;
  isVisible: boolean;
  onClose: () => void;
}

export default function AutoCompleteHelper({ 
  value, 
  cursorPosition, 
  onInsert, 
  isVisible, 
  onClose 
}: AutoCompleteHelperProps) {
  const [completions, setCompletions] = useState<CompletionItem[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [filter, setFilter] = useState('');

  const aetherCompletions: CompletionItem[] = [
    // Core Types
    {
      label: 'LyrixaCore',
      detail: 'class',
      documentation: 'Main Lyrixa consciousness interface for neural operations',
      type: 'type',
      insertText: 'LyrixaCore'
    },
    {
      label: 'NeuralNetwork',
      detail: 'class',
      documentation: 'Neural network abstraction for synaptic operations',
      type: 'type',
      insertText: 'NeuralNetwork'
    },
    {
      label: 'MemoryBank',
      detail: 'class',
      documentation: 'Memory management system for neural data storage',
      type: 'type',
      insertText: 'MemoryBank'
    },
    
    // Core Functions
    {
      label: 'allocateMemory',
      detail: '(size: number, type?: string) => MemoryBlock',
      documentation: 'Allocates memory block for neural operations',
      type: 'function',
      insertText: 'allocateMemory(${1:size}${2:, "${3:type}"})'
    },
    {
      label: 'deallocateMemory',
      detail: '(block: MemoryBlock) => void',
      documentation: 'Deallocates memory block and frees resources',
      type: 'function',
      insertText: 'deallocateMemory(${1:block})'
    },
    {
      label: 'loadPlugin',
      detail: '(name: string) => PluginInterface',
      documentation: 'Loads and initializes a neural plugin',
      type: 'function',
      insertText: 'loadPlugin("${1:plugin_name}")'
    },
    {
      label: 'chainPlugins',
      detail: '(...plugins: PluginInterface[]) => PluginChain',
      documentation: 'Chains multiple plugins for sequential execution',
      type: 'function',
      insertText: 'chainPlugins(${1:plugin1}, ${2:plugin2})'
    },
    {
      label: 'optimizeNeuralPathways',
      detail: '(network: NeuralNetwork) => OptimizationResult',
      documentation: 'Optimizes neural pathways for improved performance',
      type: 'function',
      insertText: 'optimizeNeuralPathways(${1:network})'
    },
    {
      label: 'triggerReflex',
      detail: '(condition: string, action: Function) => void',
      documentation: 'Sets up reflexive neural response to conditions',
      type: 'function',
      insertText: 'triggerReflex("${1:condition}", ${2:action})'
    },
    {
      label: 'storeThought',
      detail: '(thought: string, context?: object) => ThoughtId',
      documentation: 'Stores thought in neural memory with optional context',
      type: 'function',
      insertText: 'storeThought("${1:thought}"${2:, ${3:context}})'
    },
    {
      label: 'queryMemory',
      detail: '(query: string) => MemoryResult[]',
      documentation: 'Queries neural memory for related thoughts and data',
      type: 'function',
      insertText: 'queryMemory("${1:query}")'
    },
    
    // Keywords
    {
      label: 'lyrixa',
      detail: 'keyword',
      documentation: 'Global Lyrixa consciousness instance',
      type: 'keyword',
      insertText: 'lyrixa'
    },
    {
      label: 'neuralnet',
      detail: 'keyword',
      documentation: 'Neural network namespace',
      type: 'keyword',
      insertText: 'neuralnet'
    },
    {
      label: 'memory_store',
      detail: 'keyword',
      documentation: 'Global memory storage system',
      type: 'keyword',
      insertText: 'memory_store'
    },
    {
      label: 'plugin_manager',
      detail: 'keyword',
      documentation: 'Global plugin management system',
      type: 'keyword',
      insertText: 'plugin_manager'
    },
    
    // Snippets
    {
      label: 'lyrixa-init',
      detail: 'snippet',
      documentation: 'Initialize Lyrixa consciousness with basic setup',
      type: 'snippet',
      insertText: `const lyrixa = new LyrixaCore();
const memory = lyrixa.allocateMemory(\${1:2048});
lyrixa.log("Lyrixa consciousness initialized");`
    },
    {
      label: 'neural-optimization',
      detail: 'snippet',
      documentation: 'Neural network optimization routine',
      type: 'snippet',
      insertText: `const optimizer = lyrixa.loadPlugin('performance_optimizer');
const result = optimizer.optimizeNeuralPathways(\${1:network});
lyrixa.log(\`Optimization complete: \${result.improvement}% improvement\`);`
    },
    {
      label: 'memory-management',
      detail: 'snippet',
      documentation: 'Memory allocation and cleanup pattern',
      type: 'snippet',
      insertText: `const memory = lyrixa.allocateMemory(\${1:1024}, "\${2:data}");
try {
  \${3:// Your code here}
} finally {
  lyrixa.deallocateMemory(memory);
}`
    },
    {
      label: 'plugin-chain',
      detail: 'snippet',
      documentation: 'Plugin chaining pattern for complex operations',
      type: 'snippet',
      insertText: `const analyzer = lyrixa.loadPlugin('\${1:analyzer}');
const processor = lyrixa.loadPlugin('\${2:processor}');
const chain = lyrixa.chainPlugins(analyzer, processor);
const result = chain.execute(\${3:input});`
    }
  ];

  useEffect(() => {
    if (!isVisible) return;

    // Get current word being typed
    const lines = value.split('\n');
    const currentLine = lines[cursorPosition.line - 1] || '';
    const beforeCursor = currentLine.substring(0, cursorPosition.column - 1);
    
    // Find the current word
    const wordMatch = beforeCursor.match(/(\w+)$/);
    const currentWord = wordMatch ? wordMatch[1] : '';
    
    setFilter(currentWord);
    
    // Filter completions based on current word
    const filtered = aetherCompletions.filter(completion =>
      completion.label.toLowerCase().includes(currentWord.toLowerCase()) ||
      completion.detail.toLowerCase().includes(currentWord.toLowerCase())
    );
    
    setCompletions(filtered);
    setSelectedIndex(0);
  }, [value, cursorPosition, isVisible]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isVisible) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => Math.min(prev + 1, completions.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
        case 'Tab':
          e.preventDefault();
          if (completions[selectedIndex]) {
            handleInsert(completions[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, completions, selectedIndex]);

  const handleInsert = (completion: CompletionItem) => {
    // Replace the current word with the completion
    const insertText = completion.insertText.replace(/\$\{\d+:?([^}]*)\}/g, '$1');
    onInsert(insertText);
    onClose();
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'keyword': return '🔑';
      case 'function': return '⚡';
      case 'variable': return '📦';
      case 'type': return '🧩';
      case 'snippet': return '📝';
      default: return '📄';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'keyword': return 'text-blue-400';
      case 'function': return 'text-aetherra-green';
      case 'variable': return 'text-yellow-400';
      case 'type': return 'text-purple-400';
      case 'snippet': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  if (!isVisible || completions.length === 0) {
    return null;
  }

  return (
    <div className="fixed z-50 bg-gray-800 border border-gray-600 rounded-lg shadow-xl max-w-md max-h-64 overflow-y-auto">
      <div className="p-2 border-b border-gray-600 bg-gray-700">
        <div className="text-xs text-gray-300 flex items-center">
          <span className="text-aetherra-green">🧠</span>
          <span className="ml-2">AetherScript IntelliSense</span>
          <span className="ml-auto text-gray-500">{completions.length} suggestions</span>
        </div>
      </div>
      
      <div className="py-1">
        {completions.map((completion, index) => (
          <div
            key={completion.label}
            onClick={() => handleInsert(completion)}
            className={`px-3 py-2 cursor-pointer transition-colors ${
              index === selectedIndex 
                ? 'bg-aetherra-green bg-opacity-20 border-l-2 border-aetherra-green' 
                : 'hover:bg-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <span className="text-sm">{getTypeIcon(completion.type)}</span>
              <span className="font-medium text-white">{completion.label}</span>
              <span className={`text-xs ${getTypeColor(completion.type)}`}>
                {completion.type}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-1 font-mono">
              {completion.detail}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {completion.documentation}
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-2 border-t border-gray-600 bg-gray-700">
        <div className="text-xs text-gray-400">
          Use ↑↓ to navigate, Enter/Tab to insert, Esc to close
        </div>
      </div>
    </div>
  );
}
