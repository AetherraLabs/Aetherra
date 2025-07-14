import React, { useState, useEffect } from 'react'

interface PluginInvocation {
  id: string;
  timestamp: string;
  pluginName: string;
  action: 'load' | 'execute' | 'chain' | 'unload';
  status: 'pending' | 'success' | 'error' | 'warning';
  duration?: number;
  inputData?: string;
  outputData?: string;
  chainedFrom?: string;
  chainedTo?: string;
}

interface PluginTraceViewerProps {
  isActive: boolean;
  script: string;
}

export default function PluginTraceViewer({ isActive, script }: PluginTraceViewerProps) {
  const [pluginTrace, setPluginTrace] = useState<PluginInvocation[]>([]);
  const [activePlugins, setActivePlugins] = useState<string[]>([]);

  useEffect(() => {
    if (isActive) {
      simulatePluginTrace();
    }
  }, [isActive, script]);

  const simulatePluginTrace = async () => {
    const traces: PluginInvocation[] = [];
    const plugins: string[] = [];

    // Core system plugins always load first
    traces.push({
      id: 'plugin_001',
      timestamp: new Date().toLocaleTimeString(),
      pluginName: 'core_runtime',
      action: 'load',
      status: 'success',
      duration: 12,
      inputData: 'System initialization',
      outputData: 'Runtime ready'
    });
    plugins.push('core_runtime');

    await sleep(200);

    // Analyze script content for plugin requirements
    if (script.includes('lyrixa')) {
      traces.push({
        id: 'plugin_002',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'lyrixa_consciousness',
        action: 'load',
        status: 'success',
        duration: 145,
        inputData: 'Consciousness interface request',
        outputData: 'Neural substrate connected',
        chainedFrom: 'core_runtime'
      });
      plugins.push('lyrixa_consciousness');

      await sleep(150);

      traces.push({
        id: 'plugin_003',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'lyrixa_consciousness',
        action: 'execute',
        status: 'success',
        duration: 89,
        inputData: 'User script context',
        outputData: 'Cognitive processing active'
      });
    }

    if (script.includes('memory') || script.includes('neural')) {
      traces.push({
        id: 'plugin_004',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'neural_engine',
        action: 'load',
        status: 'success',
        duration: 234,
        inputData: 'Neural network initialization',
        outputData: 'Synaptic pathways established',
        chainedFrom: 'lyrixa_consciousness'
      });
      plugins.push('neural_engine');

      await sleep(250);

      traces.push({
        id: 'plugin_005',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'memory_manager',
        action: 'load',
        status: 'success',
        duration: 67,
        inputData: 'Memory subsystem request',
        outputData: 'Memory banks allocated',
        chainedTo: 'neural_engine'
      });
      plugins.push('memory_manager');
    }

    if (script.includes('plugin') || script.includes('extend')) {
      traces.push({
        id: 'plugin_006',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'plugin_loader',
        action: 'load',
        status: 'success',
        duration: 45,
        inputData: 'Dynamic plugin discovery',
        outputData: 'Extension framework ready'
      });
      plugins.push('plugin_loader');

      await sleep(100);

      traces.push({
        id: 'plugin_007',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'script_analyzer',
        action: 'chain',
        status: 'success',
        duration: 78,
        inputData: 'Script semantic analysis',
        outputData: 'Dependency graph built',
        chainedFrom: 'plugin_loader'
      });
    }

    if (script.includes('optimize') || script.includes('performance')) {
      traces.push({
        id: 'plugin_008',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'performance_optimizer',
        action: 'load',
        status: 'warning',
        duration: 156,
        inputData: 'Performance analysis request',
        outputData: 'Optimization suggestions available'
      });
      plugins.push('performance_optimizer');

      await sleep(120);

      traces.push({
        id: 'plugin_009',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'performance_optimizer',
        action: 'execute',
        status: 'success',
        duration: 203,
        inputData: 'Neural pathway analysis',
        outputData: 'Efficiency increased 23.7%',
        chainedTo: 'neural_engine'
      });
    }

    // Simulate cleanup
    setTimeout(() => {
      traces.push({
        id: 'plugin_010',
        timestamp: new Date().toLocaleTimeString(),
        pluginName: 'garbage_collector',
        action: 'execute',
        status: 'success',
        duration: 34,
        inputData: 'Cleanup unused plugins',
        outputData: 'Memory freed: 2.3MB'
      });
      setPluginTrace([...traces]);
    }, 3000);

    setPluginTrace(traces);
    setActivePlugins(plugins);
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'load': return '📥';
      case 'execute': return '⚡';
      case 'chain': return '🔗';
      case 'unload': return '📤';
      default: return '🔧';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-yellow-400';
      case 'success': return 'text-aetherra-green';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      default: return '❓';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center space-x-3">
          <span className="text-aetherra-green font-semibold">🔌 Plugin Trace</span>
          <span className="text-xs text-gray-400">Dynamic Extension System</span>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-gray-400">Active: {activePlugins.length}</span>
          <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-aetherra-green animate-pulse' : 'bg-gray-600'}`}></div>
        </div>
      </div>

      {/* Plugin Trace List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {pluginTrace.length === 0 && !isActive && (
          <div className="text-gray-500 italic text-center py-8">
            🔌 Plugin system idle
            <br />
            <span className="text-xs">Execute a script to monitor plugin activations</span>
          </div>
        )}

        {pluginTrace.map((invocation) => (
          <div key={invocation.id} className="bg-gray-800 rounded-lg p-3 border-l-4 border-purple-600">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getActionIcon(invocation.action)}</span>
                <span className="font-semibold text-purple-300">{invocation.pluginName}</span>
                <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                  {invocation.action.toUpperCase()}
                </span>
                <span className={`text-xs ${getStatusColor(invocation.status)}`}>
                  {getStatusIcon(invocation.status)} {invocation.status}
                </span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-gray-400">
                {invocation.duration && <span>⏱️ {invocation.duration}ms</span>}
                <span>[{invocation.timestamp}]</span>
              </div>
            </div>

            {/* Chain Information */}
            {(invocation.chainedFrom || invocation.chainedTo) && (
              <div className="mb-2 text-xs">
                {invocation.chainedFrom && (
                  <div className="text-blue-300">
                    ← Chained from: <span className="font-mono">{invocation.chainedFrom}</span>
                  </div>
                )}
                {invocation.chainedTo && (
                  <div className="text-green-300">
                    → Chaining to: <span className="font-mono">{invocation.chainedTo}</span>
                  </div>
                )}
              </div>
            )}

            {/* Input/Output Data */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 text-xs">
              {invocation.inputData && (
                <div>
                  <span className="text-gray-400">Input:</span>
                  <div className="text-blue-300 bg-gray-700 p-2 rounded mt-1">
                    {invocation.inputData}
                  </div>
                </div>
              )}
              {invocation.outputData && (
                <div>
                  <span className="text-gray-400">Output:</span>
                  <div className="text-green-300 bg-gray-700 p-2 rounded mt-1">
                    {invocation.outputData}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isActive && pluginTrace.length === 0 && (
          <div className="flex items-center space-x-3 p-3 bg-gray-800 rounded">
            <div className="w-4 h-4 border-2 border-aetherra-green border-t-transparent rounded-full animate-spin"></div>
            <span className="text-aetherra-green">Initializing plugin system...</span>
          </div>
        )}
      </div>

      {/* Active Plugins Footer */}
      {activePlugins.length > 0 && (
        <div className="p-3 bg-gray-800 border-t border-gray-700 rounded-b-xl">
          <div className="text-xs text-gray-400 mb-2">Currently Active Plugins:</div>
          <div className="flex flex-wrap gap-2">
            {activePlugins.map((plugin, index) => (
              <span 
                key={index} 
                className="px-2 py-1 bg-purple-600 text-white rounded-full text-xs font-medium"
              >
                🔌 {plugin}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
