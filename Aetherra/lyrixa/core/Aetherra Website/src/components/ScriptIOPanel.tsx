import React, { useState, useEffect, useRef } from 'react'

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  source: string;
  memoryContext?: string;
  pluginContext?: string;
}

interface MemorySnapshot {
  id: string;
  timestamp: Date;
  totalAllocated: number;
  totalUsed: number;
  activeObjects: number;
  pluginAllocations: Record<string, number>;
}

interface ScriptIOPanelProps {
  output: string;
  input: string;
  onInputChange: (value: string) => void;
  memoryContext: any;
  isExecuting: boolean;
}

export default function ScriptIOPanel({ 
  output, 
  input, 
  onInputChange, 
  memoryContext, 
  isExecuting 
}: ScriptIOPanelProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [memorySnapshots, setMemorySnapshots] = useState<MemorySnapshot[]>([]);
  const [activeTab, setActiveTab] = useState<'output' | 'logs' | 'memory'>('output');
  const [logFilter, setLogFilter] = useState<'all' | 'info' | 'warning' | 'error' | 'debug'>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const outputRef = useRef<HTMLDivElement>(null);
  const logsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize with sample logs
    initializeSampleLogs();
    initializeSampleMemory();
  }, []);

  useEffect(() => {
    // Auto-scroll when new content is added
    if (autoScroll) {
      if (activeTab === 'output' && outputRef.current) {
        outputRef.current.scrollTop = outputRef.current.scrollHeight;
      } else if (activeTab === 'logs' && logsRef.current) {
        logsRef.current.scrollTop = logsRef.current.scrollHeight;
      }
    }
  }, [output, logs, activeTab, autoScroll]);

  const initializeSampleLogs = () => {
    const sampleLogs: LogEntry[] = [
      {
        id: 'log_001',
        timestamp: new Date(Date.now() - 60000),
        level: 'info',
        message: 'Aetherra runtime initialized successfully',
        source: 'core_runtime',
        memoryContext: 'Initial allocation: 1024KB'
      },
      {
        id: 'log_002',
        timestamp: new Date(Date.now() - 45000),
        level: 'debug',
        message: 'Loading neural engine plugin',
        source: 'plugin_manager',
        pluginContext: 'neural_engine v2.1.0'
      },
      {
        id: 'log_003',
        timestamp: new Date(Date.now() - 30000),
        level: 'warning',
        message: 'Large memory allocation detected (>10MB)',
        source: 'memory_manager',
        memoryContext: 'Allocation size: 15.2MB'
      },
      {
        id: 'log_004',
        timestamp: new Date(Date.now() - 15000),
        level: 'info',
        message: 'Neural network training completed',
        source: 'neural_engine',
        memoryContext: 'Training memory freed: 8.5MB'
      }
    ];
    setLogs(sampleLogs);
  };

  const initializeSampleMemory = () => {
    const sampleMemory: MemorySnapshot[] = [
      {
        id: 'mem_001',
        timestamp: new Date(Date.now() - 60000),
        totalAllocated: 1024 * 1024,
        totalUsed: 512 * 1024,
        activeObjects: 15,
        pluginAllocations: {
          'core_runtime': 256 * 1024,
          'neural_engine': 256 * 1024
        }
      },
      {
        id: 'mem_002',
        timestamp: new Date(Date.now() - 30000),
        totalAllocated: 2048 * 1024,
        totalUsed: 1536 * 1024,
        activeObjects: 23,
        pluginAllocations: {
          'core_runtime': 256 * 1024,
          'neural_engine': 1024 * 1024,
          'memory_manager': 256 * 1024
        }
      }
    ];
    setMemorySnapshots(sampleMemory);
  };

  const addLog = (level: LogEntry['level'], message: string, source: string, context?: any) => {
    const newLog: LogEntry = {
      id: `log_${Date.now()}`,
      timestamp: new Date(),
      level,
      message,
      source,
      memoryContext: context?.memory,
      pluginContext: context?.plugin
    };
    
    setLogs(prev => [...prev, newLog].slice(-100)); // Keep last 100 logs
  };

  const captureMemorySnapshot = () => {
    const snapshot: MemorySnapshot = {
      id: `mem_${Date.now()}`,
      timestamp: new Date(),
      totalAllocated: (memoryContext?.totalAllocated || 0),
      totalUsed: (memoryContext?.totalUsed || 0),
      activeObjects: (memoryContext?.activeObjects || 0),
      pluginAllocations: memoryContext?.pluginAllocations || {}
    };
    
    setMemorySnapshots(prev => [...prev, snapshot].slice(-20)); // Keep last 20 snapshots
  };

  const clearOutput = () => {
    // This would be handled by parent component
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const clearMemory = () => {
    setMemorySnapshots([]);
  };

  const filteredLogs = logs.filter(log => 
    logFilter === 'all' || log.level === logFilter
  );

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'info': return 'text-blue-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      case 'debug': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'info': return 'ℹ️';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'debug': return '🔍';
      default: return '📝';
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString();
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Input Panel */}
      <div className="p-3 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-aetherra-green font-semibold">📝 Script Input</span>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">
              {input.length} characters
            </span>
            {isExecuting && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
                <span className="text-xs text-aetherra-green">Executing...</span>
              </div>
            )}
          </div>
        </div>
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Enter your .aether script here..."
          className="w-full h-24 bg-gray-700 border border-gray-600 rounded p-2 text-white font-mono text-sm resize-none focus:outline-none focus:border-aetherra-green"
          disabled={isExecuting}
        />
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-700 bg-gray-800">
        {[
          { key: 'output', label: 'Output', icon: '📄' },
          { key: 'logs', label: 'Logs', icon: '📋', count: logs.length },
          { key: 'memory', label: 'Memory', icon: '💾', count: memorySnapshots.length }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'text-aetherra-green border-b-2 border-aetherra-green'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="mr-1">{tab.icon}</span>
            {tab.label}
            {tab.count !== undefined && (
              <span className="ml-1 px-1 py-0.5 bg-gray-600 rounded text-xs">
                {tab.count}
              </span>
            )}
          </button>
        ))}
        
        <div className="flex-1 flex justify-end items-center px-3">
          <label className="flex items-center space-x-2 text-xs text-gray-400">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            <span>Auto-scroll</span>
          </label>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {/* Output Tab */}
        {activeTab === 'output' && (
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-2 bg-gray-800 border-b border-gray-700">
              <span className="text-sm text-gray-400">Script Output</span>
              <button
                onClick={clearOutput}
                className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                Clear
              </button>
            </div>
            <div 
              ref={outputRef}
              className="flex-1 p-3 font-mono text-sm text-white overflow-y-auto bg-gray-900"
            >
              {output ? (
                <pre className="whitespace-pre-wrap">{output}</pre>
              ) : (
                <div className="text-gray-500 italic">
                  No output yet. Run a script to see results.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-2 bg-gray-800 border-b border-gray-700">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400">System Logs</span>
                <select
                  value={logFilter}
                  onChange={(e) => setLogFilter(e.target.value as any)}
                  className="text-xs bg-gray-700 border border-gray-600 rounded px-2 py-1"
                >
                  <option value="all">All</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="debug">Debug</option>
                </select>
              </div>
              <button
                onClick={clearLogs}
                className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                Clear
              </button>
            </div>
            <div 
              ref={logsRef}
              className="flex-1 overflow-y-auto"
            >
              {filteredLogs.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  No logs to display
                </div>
              ) : (
                <div className="space-y-1 p-2">
                  {filteredLogs.map((log) => (
                    <div key={log.id} className="p-2 bg-gray-800 rounded text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          <span>{getLevelIcon(log.level)}</span>
                          <span className={`font-medium ${getLevelColor(log.level)}`}>
                            {log.level.toUpperCase()}
                          </span>
                          <span className="text-gray-400">[{log.source}]</span>
                        </div>
                        <span className="text-gray-400">
                          {formatTime(log.timestamp)}
                        </span>
                      </div>
                      <div className="text-white mb-1">{log.message}</div>
                      {log.memoryContext && (
                        <div className="text-purple-300 text-xs">
                          💾 {log.memoryContext}
                        </div>
                      )}
                      {log.pluginContext && (
                        <div className="text-blue-300 text-xs">
                          🔌 {log.pluginContext}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Memory Tab */}
        {activeTab === 'memory' && (
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-2 bg-gray-800 border-b border-gray-700">
              <span className="text-sm text-gray-400">Memory Snapshots</span>
              <div className="flex space-x-2">
                <button
                  onClick={captureMemorySnapshot}
                  className="text-xs px-2 py-1 bg-aetherra-green text-black rounded font-medium hover:bg-green-400 transition-colors"
                >
                  Capture
                </button>
                <button
                  onClick={clearMemory}
                  className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
              {memorySnapshots.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  No memory snapshots captured
                </div>
              ) : (
                memorySnapshots.slice().reverse().map((snapshot) => (
                  <div key={snapshot.id} className="p-3 bg-gray-800 rounded">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-white">
                        {formatTime(snapshot.timestamp)}
                      </span>
                      <span className="text-xs text-gray-400">
                        {snapshot.activeObjects} objects
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                      <div>
                        <span className="text-gray-400">Allocated:</span>
                        <div className="text-white">{formatBytes(snapshot.totalAllocated)}</div>
                      </div>
                      <div>
                        <span className="text-gray-400">Used:</span>
                        <div className="text-white">{formatBytes(snapshot.totalUsed)}</div>
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                      <div 
                        className="bg-aetherra-green h-2 rounded-full"
                        style={{ 
                          width: `${(snapshot.totalUsed / snapshot.totalAllocated * 100)}%` 
                        }}
                      ></div>
                    </div>
                    
                    <div className="text-xs">
                      <span className="text-gray-400">Plugin Allocations:</span>
                      <div className="mt-1 space-y-1">
                        {Object.entries(snapshot.pluginAllocations).map(([plugin, bytes]) => (
                          <div key={plugin} className="flex justify-between">
                            <span className="text-blue-300">🔌 {plugin}</span>
                            <span className="text-white">{formatBytes(bytes)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Export functions for external use
export const useScriptIO = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [memorySnapshots, setMemorySnapshots] = useState<MemorySnapshot[]>([]);

  const addLog = (level: LogEntry['level'], message: string, source: string, context?: any) => {
    const newLog: LogEntry = {
      id: `log_${Date.now()}`,
      timestamp: new Date(),
      level,
      message,
      source,
      memoryContext: context?.memory,
      pluginContext: context?.plugin
    };
    
    setLogs(prev => [...prev, newLog].slice(-100));
  };

  const captureMemorySnapshot = (memoryContext: any) => {
    const snapshot: MemorySnapshot = {
      id: `mem_${Date.now()}`,
      timestamp: new Date(),
      totalAllocated: memoryContext?.totalAllocated || 0,
      totalUsed: memoryContext?.totalUsed || 0,
      activeObjects: memoryContext?.activeObjects || 0,
      pluginAllocations: memoryContext?.pluginAllocations || {}
    };
    
    setMemorySnapshots(prev => [...prev, snapshot].slice(-20));
  };

  return { logs, memorySnapshots, addLog, captureMemorySnapshot };
};
