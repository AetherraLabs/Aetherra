import React from 'react';

export default function ThoughtLog() {
  const thoughts = [
    { time: "10:21", text: "Evaluating plugin conflict: summarizer_plugin vs memory_cleanser", type: "warning" },
    { time: "10:22", text: "Adjusted goal priority based on emotional tone.", type: "info" },
    { time: "10:23", text: "Confidence decay detected, triggering reflection cycle.", type: "alert" },
    { time: "10:24", text: "Memory consolidation successful. 847 patterns linked.", type: "success" },
    { time: "10:25", text: "New learning pathway discovered in neural network.", type: "discovery" }
  ];

  return (
    <div className="bg-aetherra-gray p-4 rounded-2xl shadow-xl border border-aetherra-green/20">
      <h2 className="text-xl font-bold mb-2 gradient-text">🧠 Thought Log</h2>
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {thoughts.map((thought, index) => (
          <div
            key={index}
            className="text-sm flex items-start space-x-2"
          >
            <span className="text-zinc-500 font-mono text-xs">[{thought.time}]</span>
            <span className={`text-xs px-2 py-1 rounded ${
              thought.type === 'warning' ? 'bg-yellow-900 text-yellow-200' :
              thought.type === 'alert' ? 'bg-red-900 text-red-200' :
              thought.type === 'success' ? 'bg-green-900 text-green-200' :
              thought.type === 'discovery' ? 'bg-purple-900 text-purple-200' :
              'bg-blue-900 text-blue-200'
            }`}>
              {thought.type}
            </span>
            <span className="text-zinc-300 flex-1">{thought.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Also export as named export for backward compatibility
export { ThoughtLog };
