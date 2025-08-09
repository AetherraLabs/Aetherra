export function DashboardStats() {
    return (
        <div className="bg-zinc-900 p-4 rounded-2xl shadow-xl">
            <h2 className="text-xl font-bold mb-2">📊 System Dashboard</h2>
            <ul className="text-sm space-y-1">
                <li>🧠 Memory Usage: 72%</li>
                <li>🔌 Plugins Active: 14</li>
                <li>🕒 Uptime: 6h 22m</li>
            </ul>
        </div>
    );
}
