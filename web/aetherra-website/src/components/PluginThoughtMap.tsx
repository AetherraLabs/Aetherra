import { useEffect, useState } from 'react';

interface ThoughtConnection {
    id: string;
    trigger: string;
    plugin: string;
    action: string;
    timestamp: string;
    status: 'active' | 'completed' | 'pending';
}

export default function PluginThoughtMap() {
    const [connections, setConnections] = useState<ThoughtConnection[]>([
        {
            id: '1',
            trigger: 'User mentioned "summarize logs"',
            plugin: 'summarizer_plugin',
            action: 'Memory recall → Plugin activation',
            timestamp: '14:32:18',
            status: 'completed'
        },
        {
            id: '2',
            trigger: 'Goal progress stalled',
            plugin: 'memory_cleanser',
            action: 'Chained optimization request',
            timestamp: '14:32:20',
            status: 'active'
        },
        {
            id: '3',
            trigger: 'Plugin conflict detected',
            plugin: 'goal_autopilot',
            action: 'Priority rebalancing queued',
            timestamp: '14:32:22',
            status: 'pending'
        }
    ]);

    const [selectedConnection, setSelectedConnection] = useState<string | null>(null);

    useEffect(() => {
        const interval = setInterval(() => {
            setConnections(prev => prev.map(conn => {
                if (conn.status === 'pending') return { ...conn, status: 'active' as const };
                if (conn.status === 'active') return { ...conn, status: 'completed' as const };
                return conn;
            }));
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'border-yellow-500 bg-yellow-500 bg-opacity-10';
            case 'completed': return 'border-green-500 bg-green-500 bg-opacity-10';
            case 'pending': return 'border-blue-500 bg-blue-500 bg-opacity-10';
            default: return 'border-gray-500';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'active': return '🔄';
            case 'completed': return '✅';
            case 'pending': return '⏳';
            default: return '❓';
        }
    };

    return (
        <div className="p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">🔗 Plugin ↔ Thought Map</h2>
                <div className="text-sm text-gray-400">
                    {connections.filter(c => c.status === 'active').length} active connections
                </div>
            </div>

            <div className="space-y-3">
                {connections.map((connection) => (
                    <div
                        key={connection.id}
                        className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-300 ${getStatusColor(connection.status)} ${selectedConnection === connection.id ? 'scale-105 shadow-lg' : ''
                            }`}
                        onClick={() => setSelectedConnection(
                            selectedConnection === connection.id ? null : connection.id
                        )}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <span className="text-lg">{getStatusIcon(connection.status)}</span>
                                <span className="font-semibold text-sm">{connection.plugin}</span>
                            </div>
                            <span className="text-xs text-gray-500">{connection.timestamp}</span>
                        </div>

                        <div className="text-sm text-gray-300">
                            <div className="mb-1">
                                <span className="text-blue-400">Trigger:</span> {connection.trigger}
                            </div>
                            <div>
                                <span className="text-purple-400">Action:</span> {connection.action}
                            </div>
                        </div>

                        {selectedConnection === connection.id && (
                            <div className="mt-3 pt-3 border-t border-gray-600 text-xs">
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <span className="text-gray-400">Memory Impact:</span>
                                        <div className="text-green-400">+0.3 relevance score</div>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">Processing Time:</span>
                                        <div className="text-yellow-400">0.24s</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div className="mt-4 bg-gray-800 p-3 rounded text-sm">
                <div className="flex items-center gap-4">
                    <span className="text-gray-400">Legend:</span>
                    <div className="flex items-center gap-2">
                        <span>⏳ Pending</span>
                        <span>🔄 Processing</span>
                        <span>✅ Complete</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
