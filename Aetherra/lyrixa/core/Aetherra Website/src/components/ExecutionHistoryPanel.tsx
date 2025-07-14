import React, { useState, useEffect } from 'react'

interface ExecutionHistoryEntry {
  id: string;
  timestamp: Date;
  script: string;
  status: 'success' | 'error' | 'warning';
  duration: number;
  memoryUsed: number;
  outputSummary: string;
  errorMessage?: string;
  pluginsUsed: string[];
}

interface ExecutionHistoryPanelProps {
  onLoadScript: (script: string) => void;
}

export default function ExecutionHistoryPanel({ onLoadScript }: ExecutionHistoryPanelProps) {
  const [history, setHistory] = useState<ExecutionHistoryEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'success' | 'error' | 'warning'>('all');

  useEffect(() => {
    // Load history from localStorage or initialize with sample data
    const savedHistory = localStorage.getItem('aether-execution-history');
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory).map((entry: any) => ({
          ...entry,
          timestamp: new Date(entry.timestamp)
        }));
        setHistory(parsed);
      } catch (error) {
        console.error('Failed to load execution history:', error);
        initializeSampleHistory();
      }
    } else {
      initializeSampleHistory();
    }
  }, []);

  const initializeSampleHistory = () => {
    const sampleHistory: ExecutionHistoryEntry[] = [
      {
        id: 'exec_001',
        timestamp: new Date(Date.now() - 3600000), // 1 hour ago
        script: 'const lyrixa = new LyrixaCore();\nlyrixa.log("Hello Aetherra!");',
        status: 'success',
        duration: 245,
        memoryUsed: 1024,
        outputSummary: 'Hello Aetherra! message logged successfully',
        pluginsUsed: ['core_runtime']
      },
      {
        id: 'exec_002',
        timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
        script: 'const memory = lyrixa.allocateMemory(2048);\nconst optimizer = lyrixa.loadPlugin("performance_optimizer");',
        status: 'success',
        duration: 567,
        memoryUsed: 2048,
        outputSummary: 'Memory allocated and optimizer plugin loaded',
        pluginsUsed: ['core_runtime', 'performance_optimizer']
      },
      {
        id: 'exec_003',
        timestamp: new Date(Date.now() - 900000), // 15 minutes ago
        script: 'const network = new NeuralNetwork();\nnetwork.invalidMethod();',
        status: 'error',
        duration: 123,
        memoryUsed: 512,
        outputSummary: 'Runtime error during execution',
        errorMessage: 'TypeError: network.invalidMethod is not a function',
        pluginsUsed: ['core_runtime', 'neural_engine']
      },
      {
        id: 'exec_004',
        timestamp: new Date(Date.now() - 300000), // 5 minutes ago
        script: 'const largeMemory = lyrixa.allocateMemory(50000);\n// Large allocation warning',
        status: 'warning',
        duration: 789,
        memoryUsed: 50000,
        outputSummary: 'Large memory allocation completed with warnings',
        pluginsUsed: ['core_runtime', 'memory_manager']
      }
    ];
    setHistory(sampleHistory);
    saveHistory(sampleHistory);
  };

  const saveHistory = (historyData: ExecutionHistoryEntry[]) => {
    localStorage.setItem('aether-execution-history', JSON.stringify(historyData));
  };

  const addExecution = (entry: Omit<ExecutionHistoryEntry, 'id' | 'timestamp'>) => {
    const newEntry: ExecutionHistoryEntry = {
      ...entry,
      id: `exec_${Date.now()}`,
      timestamp: new Date()
    };
    
    const updatedHistory = [newEntry, ...history].slice(0, 50); // Keep last 50 executions
    setHistory(updatedHistory);
    saveHistory(updatedHistory);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('aether-execution-history');
    setSelectedEntry(null);
  };

  const filteredHistory = history.filter(entry => 
    filter === 'all' || entry.status === filter
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      default: return '❓';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-aetherra-green';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatMemory = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const selectedEntryData = selectedEntry ? history.find(e => e.id === selectedEntry) : null;

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center space-x-3">
          <span className="text-aetherra-green font-semibold">📜 Execution History</span>
          <span className="text-xs text-gray-400">{history.length} total executions</span>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="text-xs bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white"
          >
            <option value="all">All</option>
            <option value="success">Success</option>
            <option value="error">Errors</option>
            <option value="warning">Warnings</option>
          </select>
          <button
            onClick={clearHistory}
            className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 flex">
        {/* List Panel */}
        <div className="w-1/2 border-r border-gray-700 overflow-y-auto">
          {filteredHistory.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {filter === 'all' ? 'No executions yet' : `No ${filter} executions`}
              <br />
              <span className="text-xs">Run some .aether scripts to see history</span>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {filteredHistory.map((entry) => (
                <div
                  key={entry.id}
                  onClick={() => setSelectedEntry(entry.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedEntry === entry.id 
                      ? 'bg-aetherra-green bg-opacity-20 border border-aetherra-green' 
                      : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm">{getStatusIcon(entry.status)}</span>
                      <span className={`text-sm font-medium ${getStatusColor(entry.status)}`}>
                        {entry.status.toUpperCase()}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {formatTimestamp(entry.timestamp)}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-300 mb-2 font-mono bg-gray-700 p-2 rounded overflow-hidden">
                    {entry.script.split('\n')[0].substring(0, 50)}
                    {entry.script.length > 50 && '...'}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>⏱️ {formatDuration(entry.duration)}</span>
                    <span>💾 {formatMemory(entry.memoryUsed)}</span>
                    <span>🔌 {entry.pluginsUsed.length}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail Panel */}
        <div className="w-1/2 overflow-y-auto">
          {selectedEntryData ? (
            <div className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-white">Execution Details</h3>
                <button
                  onClick={() => onLoadScript(selectedEntryData.script)}
                  className="text-xs px-3 py-1 bg-aetherra-green text-black rounded font-medium hover:bg-green-400 transition-colors"
                >
                  Load Script
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Status:</span>
                  <div className={`font-medium ${getStatusColor(selectedEntryData.status)}`}>
                    {getStatusIcon(selectedEntryData.status)} {selectedEntryData.status.toUpperCase()}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Duration:</span>
                  <div className="text-white">{formatDuration(selectedEntryData.duration)}</div>
                </div>
                <div>
                  <span className="text-gray-400">Memory Used:</span>
                  <div className="text-white">{formatMemory(selectedEntryData.memoryUsed)}</div>
                </div>
                <div>
                  <span className="text-gray-400">Timestamp:</span>
                  <div className="text-white">{selectedEntryData.timestamp.toLocaleString()}</div>
                </div>
              </div>

              <div>
                <span className="text-gray-400 text-sm">Script:</span>
                <div className="mt-1 p-3 bg-gray-800 rounded font-mono text-sm text-white overflow-x-auto">
                  <pre>{selectedEntryData.script}</pre>
                </div>
              </div>

              <div>
                <span className="text-gray-400 text-sm">Output Summary:</span>
                <div className="mt-1 p-3 bg-gray-800 rounded text-sm text-white">
                  {selectedEntryData.outputSummary}
                </div>
              </div>

              {selectedEntryData.errorMessage && (
                <div>
                  <span className="text-red-400 text-sm">Error:</span>
                  <div className="mt-1 p-3 bg-red-900 bg-opacity-20 border border-red-600 rounded text-sm text-red-300">
                    {selectedEntryData.errorMessage}
                  </div>
                </div>
              )}

              <div>
                <span className="text-gray-400 text-sm">Plugins Used:</span>
                <div className="mt-1 flex flex-wrap gap-2">
                  {selectedEntryData.pluginsUsed.map((plugin, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 bg-purple-600 text-white rounded text-xs"
                    >
                      🔌 {plugin}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 text-center text-gray-500">
              <div className="text-4xl mb-2">📋</div>
              Select an execution from the list to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Export the addExecution function for use by the console
export const useExecutionHistory = () => {
  const [history, setHistory] = useState<ExecutionHistoryEntry[]>([]);

  const addExecution = (entry: Omit<ExecutionHistoryEntry, 'id' | 'timestamp'>) => {
    const newEntry: ExecutionHistoryEntry = {
      ...entry,
      id: `exec_${Date.now()}`,
      timestamp: new Date()
    };
    
    const savedHistory = localStorage.getItem('aether-execution-history');
    const currentHistory = savedHistory ? JSON.parse(savedHistory) : [];
    const updatedHistory = [newEntry, ...currentHistory].slice(0, 50);
    
    setHistory(updatedHistory);
    localStorage.setItem('aether-execution-history', JSON.stringify(updatedHistory));
  };

  return { addExecution };
};
