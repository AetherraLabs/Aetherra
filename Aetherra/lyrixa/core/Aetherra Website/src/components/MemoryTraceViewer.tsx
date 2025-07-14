import React, { useState, useEffect } from 'react'

interface MemoryEntry {
  id: string;
  timestamp: string;
  type: 'allocation' | 'access' | 'modification' | 'deallocation';
  address: string;
  size: number;
  content: string;
  plugin?: string;
}

interface MemoryTraceViewerProps {
  isActive: boolean;
  script: string;
}

export default function MemoryTraceViewer({ isActive, script }: MemoryTraceViewerProps) {
  const [memoryTrace, setMemoryTrace] = useState<MemoryEntry[]>([]);
  const [totalMemoryUsed, setTotalMemoryUsed] = useState(0);

  useEffect(() => {
    if (isActive) {
      simulateMemoryTrace();
    }
  }, [isActive, script]);

  const simulateMemoryTrace = () => {
    const traces: MemoryEntry[] = [];
    let memoryCounter = 0;

    // Simulate initial memory allocation
    traces.push({
      id: 'mem_001',
      timestamp: new Date().toLocaleTimeString(),
      type: 'allocation',
      address: '0x7F8A2C000000',
      size: 1024,
      content: 'AetherScript Runtime Stack',
      plugin: 'core'
    });
    memoryCounter += 1024;

    // Analyze script for memory operations
    if (script.includes('var ') || script.includes('let ') || script.includes('const ')) {
      traces.push({
        id: 'mem_002',
        timestamp: new Date().toLocaleTimeString(),
        type: 'allocation',
        address: '0x7F8A2C001000',
        size: 256,
        content: 'Variable declarations',
        plugin: 'script_parser'
      });
      memoryCounter += 256;
    }

    if (script.includes('lyrixa')) {
      traces.push({
        id: 'mem_003',
        timestamp: new Date().toLocaleTimeString(),
        type: 'allocation',
        address: '0x7F8A2C002000',
        size: 2048,
        content: 'Lyrixa consciousness interface',
        plugin: 'lyrixa_core'
      });
      memoryCounter += 2048;

      traces.push({
        id: 'mem_004',
        timestamp: new Date().toLocaleTimeString(),
        type: 'access',
        address: '0x7F8A2C002000',
        size: 2048,
        content: 'Neural substrate connection',
        plugin: 'lyrixa_core'
      });
    }

    if (script.includes('memory') || script.includes('neural')) {
      traces.push({
        id: 'mem_005',
        timestamp: new Date().toLocaleTimeString(),
        type: 'allocation',
        address: '0x7F8A2C003000',
        size: 4096,
        content: 'Neural network weights',
        plugin: 'neural_engine'
      });
      memoryCounter += 4096;

      traces.push({
        id: 'mem_006',
        timestamp: new Date().toLocaleTimeString(),
        type: 'modification',
        address: '0x7F8A2C003000',
        size: 4096,
        content: 'Weight matrix update',
        plugin: 'neural_engine'
      });
    }

    if (script.includes('plugin')) {
      traces.push({
        id: 'mem_007',
        timestamp: new Date().toLocaleTimeString(),
        type: 'allocation',
        address: '0x7F8A2C004000',
        size: 512,
        content: 'Plugin manager heap',
        plugin: 'plugin_manager'
      });
      memoryCounter += 512;
    }

    // Simulate memory cleanup
    setTimeout(() => {
      traces.push({
        id: 'mem_008',
        timestamp: new Date().toLocaleTimeString(),
        type: 'deallocation',
        address: '0x7F8A2C001000',
        size: 256,
        content: 'Temporary variables cleanup',
        plugin: 'garbage_collector'
      });
      setMemoryTrace([...traces]);
    }, 2000);

    setMemoryTrace(traces);
    setTotalMemoryUsed(memoryCounter);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'allocation': return '🟢';
      case 'access': return '🔵';
      case 'modification': return '🟡';
      case 'deallocation': return '🔴';
      default: return '⚪';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'allocation': return 'text-green-400';
      case 'access': return 'text-blue-400';
      case 'modification': return 'text-yellow-400';
      case 'deallocation': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center space-x-3">
          <span className="text-aetherra-green font-semibold">🧠 Memory Trace</span>
          <span className="text-xs text-gray-400">Neural Memory Operations</span>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-gray-400">Total: {formatBytes(totalMemoryUsed)}</span>
          <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-aetherra-green' : 'bg-gray-600'}`}></div>
        </div>
      </div>

      {/* Memory Trace List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {memoryTrace.length === 0 && !isActive && (
          <div className="text-gray-500 italic text-center py-8">
            🧬 Memory tracing inactive
            <br />
            <span className="text-xs">Execute a script to monitor memory operations</span>
          </div>
        )}

        {memoryTrace.map((entry) => (
          <div key={entry.id} className="bg-gray-800 rounded-lg p-3 border-l-4 border-gray-600">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getTypeIcon(entry.type)}</span>
                <span className={`font-semibold text-sm ${getTypeColor(entry.type)}`}>
                  {entry.type.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500">[{entry.timestamp}]</span>
              </div>
              <span className="text-xs text-gray-400">{formatBytes(entry.size)}</span>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-400">Address:</span>
                <div className="font-mono text-blue-300">{entry.address}</div>
              </div>
              <div>
                <span className="text-gray-400">Plugin:</span>
                <div className="text-purple-300">{entry.plugin || 'system'}</div>
              </div>
            </div>
            
            <div className="mt-2">
              <span className="text-gray-400 text-xs">Content:</span>
              <div className="text-gray-200 text-sm">{entry.content}</div>
            </div>
          </div>
        ))}

        {isActive && memoryTrace.length === 0 && (
          <div className="flex items-center space-x-3 p-3 bg-gray-800 rounded">
            <div className="w-4 h-4 border-2 border-aetherra-green border-t-transparent rounded-full animate-spin"></div>
            <span className="text-aetherra-green">Initializing memory tracer...</span>
          </div>
        )}
      </div>

      {/* Memory Stats */}
      <div className="p-3 bg-gray-800 border-t border-gray-700 rounded-b-xl">
        <div className="grid grid-cols-4 gap-3 text-xs text-center">
          <div>
            <div className="text-green-400 font-semibold">Allocations</div>
            <div className="text-white">{memoryTrace.filter(e => e.type === 'allocation').length}</div>
          </div>
          <div>
            <div className="text-blue-400 font-semibold">Accesses</div>
            <div className="text-white">{memoryTrace.filter(e => e.type === 'access').length}</div>
          </div>
          <div>
            <div className="text-yellow-400 font-semibold">Modifications</div>
            <div className="text-white">{memoryTrace.filter(e => e.type === 'modification').length}</div>
          </div>
          <div>
            <div className="text-red-400 font-semibold">Deallocations</div>
            <div className="text-white">{memoryTrace.filter(e => e.type === 'deallocation').length}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
