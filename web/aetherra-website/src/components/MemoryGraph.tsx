import { useEffect, useState } from 'react';

export default function MemoryGraph() {
    const [memoryNodes, setMemoryNodes] = useState([
        { id: 'consciousness', x: 50, y: 30, connections: ['goals', 'plugins'], strength: 0.9 },
        { id: 'goals', x: 20, y: 60, connections: ['memory'], strength: 0.7 },
        { id: 'plugins', x: 80, y: 60, connections: ['memory'], strength: 0.8 },
        { id: 'memory', x: 50, y: 80, connections: [], strength: 0.6 },
    ]);

    const [activeNode, setActiveNode] = useState('consciousness');

    useEffect(() => {
        const interval = setInterval(() => {
            setMemoryNodes(nodes => nodes.map(node => ({
                ...node,
                strength: Math.max(0.3, Math.min(1.0, node.strength + (Math.random() - 0.5) * 0.1))
            })));
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const getNodeColor = (strength: number) => {
        if (strength > 0.8) return 'bg-green-500';
        if (strength > 0.6) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">🧠 Live Memory Graph</h2>
                <div className="text-sm text-gray-400">
                    Active Node: <span className="text-blue-400">{activeNode}</span>
                </div>
            </div>

            <div className="bg-gray-900 rounded-xl h-80 relative overflow-hidden">
                <svg className="w-full h-full">
                    {/* Connections */}
                    {memoryNodes.map(node =>
                        node.connections.map(targetId => {
                            const target = memoryNodes.find(n => n.id === targetId);
                            if (!target) return null;

                            return (
                                <line
                                    key={`${node.id}-${targetId}`}
                                    x1={`${node.x}%`}
                                    y1={`${node.y}%`}
                                    x2={`${target.x}%`}
                                    y2={`${target.y}%`}
                                    stroke="rgba(59, 130, 246, 0.5)"
                                    strokeWidth="2"
                                    className="animate-pulse"
                                />
                            );
                        })
                    )}

                    {/* Nodes */}
                    {memoryNodes.map(node => (
                        <g key={node.id}>
                            <circle
                                cx={`${node.x}%`}
                                cy={`${node.y}%`}
                                r="20"
                                className={`${getNodeColor(node.strength)} cursor-pointer transition-all duration-500`}
                                onClick={() => setActiveNode(node.id)}
                                style={{ opacity: node.strength }}
                            />
                            <text
                                x={`${node.x}%`}
                                y={`${node.y + 8}%`}
                                textAnchor="middle"
                                className="text-xs fill-white font-semibold pointer-events-none"
                            >
                                {node.id}
                            </text>
                        </g>
                    ))}
                </svg>

                {/* Legend */}
                <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 p-3 rounded text-xs">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-3 h-3 bg-green-500 rounded"></div>
                        <span>High Activity (&gt;80%)</span>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                        <span>Medium Activity (60-80%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded"></div>
                        <span>Low Activity (&lt;60%)</span>
                    </div>
                </div>
            </div>

            <div className="mt-4 bg-gray-800 p-3 rounded text-sm">
                <strong>Memory Analysis:</strong> {memoryNodes.find(n => n.id === activeNode)?.id} node showing {
                    (memoryNodes.find(n => n.id === activeNode)?.strength ?? 0 * 100).toFixed(1)
                }% activity. Connected to {memoryNodes.find(n => n.id === activeNode)?.connections.length} other nodes.
            </div>
        </div>
    );
}
