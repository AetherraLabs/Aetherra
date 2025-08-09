export default function ReflectionPanel() {
    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-2">🧠 Daily Reflection</h2>
            <div className="text-sm text-gray-300">
                <p>"In the last 24 hours, Lyrixa improved 3 plugins, escalated 1 goal, and rebalanced memory usage."</p>
                <p className="mt-2 text-xs text-gray-500">Source: daily_reflector.aether</p>
            </div>
        </div>
    );
}
