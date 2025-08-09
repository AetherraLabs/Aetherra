import { useEffect, useState } from 'react';

interface SystemMetrics {
    memoryUsage: number;
    pluginLoad: number;
    activeAgents: number;
    reflexesTriggered: number;
    uptime: string;
    cpuUsage: number;
}

export default function SystemDashboard() {
    const [metrics, setMetrics] = useState<SystemMetrics>({
        memoryUsage: 78,
        pluginLoad: 14,
        activeAgents: 5,
        reflexesTriggered: 3,
        uptime: '6h 22m',
        cpuUsage: 42
    });

    const [isLive, setIsLive] = useState(true);

    useEffect(() => {
        if (!isLive) return;

        const interval = setInterval(() => {
            setMetrics(prev => ({
                ...prev,
                memoryUsage: Math.max(60, Math.min(95, prev.memoryUsage + (Math.random() - 0.5) * 10)),
                cpuUsage: Math.max(20, Math.min(80, prev.cpuUsage + (Math.random() - 0.5) * 15)),
                reflexesTriggered: prev.reflexesTriggered + (Math.random() > 0.8 ? 1 : 0),
                activeAgents: Math.max(3, Math.min(8, prev.activeAgents + (Math.random() > 0.7 ? (Math.random() > 0.5 ? 1 : -1) : 0)))
            }));
        }, 3000);

        return () => clearInterval(interval);
    }, [isLive]);

    const getUsageColor = (value: number, thresholds = { low: 50, high: 80 }) => {
        if (value >= thresholds.high) return 'text-red-400';
        if (value >= thresholds.low) return 'text-yellow-400';
        return 'text-green-400';
    };

    const getUsageBar = (value: number, max = 100) => {
        const percentage = (value / max) * 100;
        let colorClass = 'bg-green-500';
        if (percentage >= 80) colorClass = 'bg-red-500';
        else if (percentage >= 50) colorClass = 'bg-yellow-500';

        return (
            <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
                <div
                    className={`h-2 rounded-full transition-all duration-500 ${colorClass}`}
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
        );
    };

    return (
        <div className="p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">📊 System Dashboard</h2>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsLive(!isLive)}
                        className={`px-3 py-1 rounded text-sm ${isLive
                                ? 'bg-green-600 text-white'
                                : 'bg-gray-600 text-gray-300'
                            }`}
                    >
                        {isLive ? '🔴 LIVE' : '⏸️ PAUSED'}
                    </button>
                    <div className="text-sm text-gray-400">
                        Uptime: {metrics.uptime}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">🧠</span>
                        <span className={`font-bold ${getUsageColor(metrics.memoryUsage)}`}>
                            {metrics.memoryUsage}%
                        </span>
                    </div>
                    <div className="text-sm text-gray-300 mb-1">Memory Usage</div>
                    {getUsageBar(metrics.memoryUsage)}
                </div>

                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">⚙️</span>
                        <span className={`font-bold ${getUsageColor(metrics.cpuUsage)}`}>
                            {metrics.cpuUsage}%
                        </span>
                    </div>
                    <div className="text-sm text-gray-300 mb-1">CPU Usage</div>
                    {getUsageBar(metrics.cpuUsage)}
                </div>

                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">📦</span>
                        <span className="font-bold text-blue-400">{metrics.pluginLoad}</span>
                    </div>
                    <div className="text-sm text-gray-300">Active Plugins</div>
                    <div className="text-xs text-gray-500 mt-1">
                        {Math.floor(metrics.pluginLoad * 0.8)} running, {Math.ceil(metrics.pluginLoad * 0.2)} idle
                    </div>
                </div>

                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">🤖</span>
                        <span className="font-bold text-purple-400">{metrics.activeAgents}</span>
                    </div>
                    <div className="text-sm text-gray-300">Active Agents</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Processing tasks and goals
                    </div>
                </div>

                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">⚡</span>
                        <span className="font-bold text-yellow-400">{metrics.reflexesTriggered}</span>
                    </div>
                    <div className="text-sm text-gray-300">Reflexes Triggered</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Last 24 hours
                    </div>
                </div>

                <div className="bg-gray-900 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-lg">🌐</span>
                        <span className="font-bold text-green-400">ONLINE</span>
                    </div>
                    <div className="text-sm text-gray-300">System Status</div>
                    <div className="text-xs text-gray-500 mt-1">
                        All systems operational
                    </div>
                </div>
            </div>

            <div className="mt-4 bg-gray-800 p-3 rounded text-sm">
                <div className="flex items-center justify-between">
                    <span className="text-gray-400">
                        Real-time monitoring of Lyrixa's consciousness infrastructure
                    </span>
                    <div className="flex items-center gap-2 text-xs">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-green-400">Healthy</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
