import React from 'react'

export default function MemoryGraph() {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2 text-aetherra-green">🧠 Live Memory Graph</h2>
      <div className="bg-gray-900 rounded-xl h-80 flex items-center justify-center text-gray-500 border border-gray-700">
        <div className="text-center">
          <div className="text-aetherra-green text-4xl mb-2">⚡</div>
          <div>[Graph Visualization Placeholder]</div>
          <div className="text-xs mt-2 text-gray-400">Neural network topology • Memory nodes • Thought pathways</div>
        </div>
      </div>
    </div>
  );
}
