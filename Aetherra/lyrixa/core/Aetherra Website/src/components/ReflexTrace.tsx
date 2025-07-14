import React from 'react'

export default function ReflexTrace() {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2 text-aetherra-green">🔁 Reflex Trace</h2>
      <ul className="text-sm bg-gray-900 rounded-xl p-4 space-y-3 border border-gray-700">
        <li className="flex items-start space-x-3 p-2 bg-gray-800 rounded-lg">
          <span className="text-blue-400">🧠</span>
          <div>
            <div className="text-gray-200">"Goal not progressing"</div>
            <div className="text-aetherra-green text-xs">→ 🔄 Triggered memory_cleanser</div>
            <div className="text-gray-500 text-xs">2.3s ago</div>
          </div>
        </li>
        <li className="flex items-start space-x-3 p-2 bg-gray-800 rounded-lg">
          <span className="text-red-400">📈</span>
          <div>
            <div className="text-gray-200">"Plugin failure threshold reached"</div>
            <div className="text-aetherra-green text-xs">→ 🔒 Disabled summarizer_plugin</div>
            <div className="text-gray-500 text-xs">15.7s ago</div>
          </div>
        </li>
        <li className="flex items-start space-x-3 p-2 bg-gray-800 rounded-lg">
          <span className="text-yellow-400">📝</span>
          <div>
            <div className="text-gray-200">"Need status update"</div>
            <div className="text-aetherra-green text-xs">→ 💬 Injected reflection summary</div>
            <div className="text-gray-500 text-xs">1m ago</div>
          </div>
        </li>
      </ul>
    </div>
  );
}
