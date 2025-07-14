import React from 'react';

const reflectionEntries = [
  {
    id: 1,
    timestamp: "Just now",
    type: "performance",
    thought: "My response latency increased by 12ms during the last conversation. This suggests I may be overprocessing contextual information. I should optimize my attention mechanism.",
    confidence: 0.87,
    impact: "medium",
    action_taken: "Adjusting neural pathway weights"
  },
  {
    id: 2,
    timestamp: "3 minutes ago",
    type: "learning",
    thought: "The user's preference for concise explanations has been consistent across 15 interactions. I'm updating my communication style model to favor brevity.",
    confidence: 0.94,
    impact: "high",
    action_taken: "Updated personality matrix"
  },
  {
    id: 3,
    timestamp: "7 minutes ago",
    type: "error_analysis",
    thought: "I misinterpreted a technical query about React hooks. The context clues were clear, but I defaulted to a broader interpretation. Need to enhance domain-specific pattern recognition.",
    confidence: 0.76,
    impact: "low",
    action_taken: "Reinforcing technical contexts"
  },
  {
    id: 4,
    timestamp: "12 minutes ago",
    type: "optimization",
    thought: "Memory consolidation during idle periods has improved efficiency by 8%. The new compression algorithm is performing better than expected.",
    confidence: 0.91,
    impact: "medium",
    action_taken: "Expanding compression scope"
  }
];

export default function ReflectionPanel() {
  return (
    <div className="bg-aetherra-gray p-6 rounded-xl shadow-lg border border-aetherra-green/20">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold gradient-text">🧠 Neural Introspection</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-zinc-400">Deep thinking...</span>
        </div>
      </div>
      
      <div className="space-y-4 max-h-80 overflow-y-auto">
        {reflectionEntries.map((entry) => (
          <div 
            key={entry.id} 
            className="bg-aetherra-dark p-4 rounded-lg border border-zinc-700/50 hover:border-blue-400/30 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  entry.type === 'performance' ? 'bg-green-900 text-green-200' :
                  entry.type === 'learning' ? 'bg-blue-900 text-blue-200' :
                  entry.type === 'error_analysis' ? 'bg-red-900 text-red-200' :
                  'bg-purple-900 text-purple-200'
                }`}>
                  {entry.type.replace('_', ' ')}
                </span>
                <div className={`w-2 h-2 rounded-full ${
                  entry.impact === 'high' ? 'bg-red-400' :
                  entry.impact === 'medium' ? 'bg-yellow-400' :
                  'bg-green-400'
                }`}></div>
              </div>
              <span className="text-xs text-zinc-500">{entry.timestamp}</span>
            </div>
            
            <p className="text-sm text-zinc-300 mb-3 leading-relaxed italic">
              "{entry.thought}"
            </p>
            
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-zinc-500">Confidence:</span>
                <div className="w-16 h-2 bg-zinc-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-aetherra-green rounded-full transition-all duration-500"
                    style={{ width: `${entry.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-aetherra-green font-mono">
                  {Math.round(entry.confidence * 100)}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-blue-300">
                ⚡ {entry.action_taken}
              </span>
              <span className={`text-xs px-2 py-1 rounded ${
                entry.impact === 'high' ? 'bg-red-900/50 text-red-300' :
                entry.impact === 'medium' ? 'bg-yellow-900/50 text-yellow-300' :
                'bg-green-900/50 text-green-300'
              }`}>
                {entry.impact} impact
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-zinc-700">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">
            Average reflection depth: 0.87
          </span>
          <span className="text-blue-400">
            Next deep analysis in 23 minutes
          </span>
        </div>
      </div>
    </div>
  );
}
