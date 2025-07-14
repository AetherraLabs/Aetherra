import React from 'react';

const improvements = [
  { 
    id: 1, 
    type: "plugin_enhancement", 
    title: "Enhanced Neural Pathway Optimization", 
    description: "Implemented advanced memory consolidation algorithms",
    impact: "23% performance improvement",
    status: "completed",
    timestamp: "2 minutes ago"
  },
  { 
    id: 2, 
    type: "architecture_update", 
    title: "Plugin Communication Protocol v2.1", 
    description: "Upgraded inter-plugin messaging system",
    impact: "40ms response time reduction",
    status: "in_progress",
    timestamp: "5 minutes ago"
  },
  { 
    id: 3, 
    type: "bug_fix", 
    title: "Memory Leak Resolution", 
    description: "Fixed recursive memory allocation in goal_processor",
    impact: "15% memory usage reduction",
    status: "completed",
    timestamp: "8 minutes ago"
  },
  { 
    id: 4, 
    type: "learning_integration", 
    title: "Adaptive Learning Framework", 
    description: "Integrated reinforcement learning for decision optimization",
    impact: "Improved decision accuracy by 18%",
    status: "testing",
    timestamp: "12 minutes ago"
  }
];

export default function SelfImprovementFeed() {
  return (
    <div className="bg-aetherra-gray p-6 rounded-xl shadow-lg border border-aetherra-green/20">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold gradient-text">🔧 Advanced Self-Improvement</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
          <span className="text-xs text-zinc-400">Auto-evolving</span>
        </div>
      </div>
      
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {improvements.map((item) => (
          <div 
            key={item.id} 
            className="bg-aetherra-dark p-4 rounded-lg border border-zinc-700/50 hover:border-aetherra-green/30 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  item.status === 'completed' ? 'bg-green-400' :
                  item.status === 'in_progress' ? 'bg-yellow-400' :
                  item.status === 'testing' ? 'bg-blue-400' :
                  'bg-zinc-400'
                }`}></div>
                <span className={`text-xs px-2 py-1 rounded ${
                  item.type === 'plugin_enhancement' ? 'bg-purple-900 text-purple-200' :
                  item.type === 'architecture_update' ? 'bg-blue-900 text-blue-200' :
                  item.type === 'bug_fix' ? 'bg-red-900 text-red-200' :
                  'bg-green-900 text-green-200'
                }`}>
                  {item.type.replace('_', ' ')}
                </span>
              </div>
              <span className="text-xs text-zinc-500">{item.timestamp}</span>
            </div>
            
            <h3 className="text-sm font-semibold text-zinc-200 mb-1">{item.title}</h3>
            <p className="text-xs text-zinc-400 mb-2">{item.description}</p>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-aetherra-green font-mono">{item.impact}</span>
              <span className={`text-xs px-2 py-1 rounded ${
                item.status === 'completed' ? 'bg-green-900/50 text-green-300' :
                item.status === 'in_progress' ? 'bg-yellow-900/50 text-yellow-300' :
                item.status === 'testing' ? 'bg-blue-900/50 text-blue-300' :
                'bg-zinc-900/50 text-zinc-300'
              }`}>
                {item.status.replace('_', ' ')}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-zinc-700">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">
            Next optimization cycle in 47 minutes
          </span>
          <span className="text-aetherra-green">
            {improvements.filter(i => i.status === 'completed').length} completed today
          </span>
        </div>
      </div>
    </div>
  );
}
