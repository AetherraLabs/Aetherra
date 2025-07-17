
export default function DashboardStats() {
  return (
    <div className="bg-aetherra-gray p-4 rounded-2xl shadow-xl border border-aetherra-green/20">
      <h2 className="text-xl font-bold mb-2 gradient-text">📊 System Dashboard</h2>
      <div className="text-xs text-zinc-500 mb-3">Demo Values - Live in Development</div>
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-zinc-300">🧠 Memory Usage:</span>
          <div className="flex items-center space-x-2">
            <div className="w-24 bg-aetherra-dark rounded-full h-2">
              <div className="bg-aetherra-green h-2 rounded-full" style={{ width: '72%' }}></div>
            </div>
            <span className="text-aetherra-green font-mono text-sm">72%</span>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-zinc-300">🔌 Plugins Active:</span>
          <span className="text-aetherra-green font-mono">14</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-zinc-300">🕒 Uptime:</span>
          <span className="text-blue-400 font-mono">6h 22m</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-zinc-300">⚡ CPU Load:</span>
          <span className="text-yellow-400 font-mono">23%</span>
        </div>
      </div>
    </div>
  );
}

// Also export as named export for backward compatibility
export { DashboardStats };
