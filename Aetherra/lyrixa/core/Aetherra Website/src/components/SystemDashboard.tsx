import React from 'react'

export default function SystemDashboard() {
  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      <div className="bg-gray-900 rounded-xl p-4 border border-gray-700">
        <div className="text-aetherra-green text-lg font-bold">🧠 Memory Usage</div>
        <div className="text-2xl font-mono">78%</div>
        <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
          <div className="bg-aetherra-green h-2 rounded-full" style={{width: '78%'}}></div>
        </div>
      </div>
      <div className="bg-gray-900 rounded-xl p-4 border border-gray-700">
        <div className="text-aetherra-green text-lg font-bold">📦 Plugin Load</div>
        <div className="text-2xl font-mono">14 active</div>
        <div className="text-xs text-gray-400 mt-1">3 queued • 2 optimizing</div>
      </div>
      <div className="bg-gray-900 rounded-xl p-4 border border-gray-700">
        <div className="text-aetherra-green text-lg font-bold">🤖 Agents</div>
        <div className="text-2xl font-mono">5 running</div>
        <div className="text-xs text-gray-400 mt-1">2 learning • 3 executing</div>
      </div>
      <div className="bg-gray-900 rounded-xl p-4 border border-gray-700">
        <div className="text-aetherra-green text-lg font-bold">⚡ Reflexes</div>
        <div className="text-2xl font-mono">3 triggered</div>
        <div className="text-xs text-gray-400 mt-1">Last: memory_cleanser</div>
      </div>
    </div>
  );
}
