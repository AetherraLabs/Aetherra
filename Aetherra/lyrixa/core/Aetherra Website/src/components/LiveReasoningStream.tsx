import React, { useEffect, useState } from 'react'

interface ReasoningEntry {
  timestamp: string;
  type: 'analysis' | 'decision' | 'execution' | 'reflection';
  content: string;
  confidence: number;
}

export default function LiveReasoningStream() {
  const [entries, setEntries] = useState<ReasoningEntry[]>([
    { timestamp: '01:32:18', type: 'analysis', content: 'Analyzing user input...', confidence: 0.95 },
    { timestamp: '01:32:19', type: 'decision', content: 'Matching intent to plugin: assistant_trainer', confidence: 0.87 },
    { timestamp: '01:32:20', type: 'execution', content: 'Plugin improvement proposal found → Queued', confidence: 0.92 },
    { timestamp: '01:32:21', type: 'reflection', content: 'Notified user of potential optimization', confidence: 0.89 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newEntry: ReasoningEntry = {
        timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
        type: ['analysis', 'decision', 'execution', 'reflection'][Math.floor(Math.random() * 4)] as any,
        content: [
          'Processing contextual patterns...',
          'Evaluating plugin performance metrics',
          'Optimizing neural pathway efficiency',
          'Consolidating memory fragments',
          'Triggering adaptive response protocol',
          'Analyzing user behavior patterns'
        ][Math.floor(Math.random() * 6)],
        confidence: Math.random() * 0.4 + 0.6 // 0.6 to 1.0
      };
      
      setEntries(prev => [newEntry, ...prev.slice(0, 9)]); // Keep last 10 entries
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'analysis': return 'text-blue-400';
      case 'decision': return 'text-yellow-400';
      case 'execution': return 'text-aetherra-green';
      case 'reflection': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'analysis': return '🔍';
      case 'decision': return '🎯';
      case 'execution': return '⚡';
      case 'reflection': return '🧠';
      default: return '💭';
    }
  };

  return (
    <div className="p-4 h-80 overflow-y-auto bg-gray-900 rounded-xl border border-gray-700">
      <h2 className="text-xl font-bold mb-4 text-aetherra-green sticky top-0 bg-gray-900 pb-2">
        🧠 Lyrixa Thought Stream
      </h2>
      <ul className="text-sm space-y-2 font-mono">
        {entries.map((entry, index) => (
          <li key={`${entry.timestamp}-${index}`} className="flex items-start space-x-3 p-2 bg-gray-800 rounded-lg">
            <span className="text-gray-500 min-w-[60px]">[{entry.timestamp}]</span>
            <span className="text-lg">{getTypeIcon(entry.type)}</span>
            <div className="flex-1">
              <div className={`${getTypeColor(entry.type)}`}>{entry.content}</div>
              <div className="text-xs text-gray-500 mt-1">
                Confidence: {(entry.confidence * 100).toFixed(1)}%
                <span className="ml-2 text-gray-600">Type: {entry.type}</span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
