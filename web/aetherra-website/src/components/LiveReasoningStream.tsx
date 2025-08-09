import { useEffect, useState } from 'react';

interface ThoughtEntry {
    id: string;
    timestamp: string;
    thought: string;
    type: 'analysis' | 'decision' | 'observation' | 'action';
    confidence: number;
}

export default function LiveReasoningStream() {
    const [thoughts, setThoughts] = useState<ThoughtEntry[]>([
        {
            id: '1',
            timestamp: '14:32:18',
            thought: 'User query detected: "improve plugin performance"',
            type: 'observation',
            confidence: 0.95
        },
        {
            id: '2',
            timestamp: '14:32:19',
            thought: 'Analyzing current plugin metrics and bottlenecks',
            type: 'analysis',
            confidence: 0.87
        },
        {
            id: '3',
            timestamp: '14:32:20',
            thought: 'Decision: Prioritize memory_cleanser optimization',
            type: 'decision',
            confidence: 0.92
        },
        {
            id: '4',
            timestamp: '14:32:21',
            thought: 'Initiating plugin improvement sequence',
            type: 'action',
            confidence: 0.98
        }
    ]);

    const [isAutoScroll, setIsAutoScroll] = useState(true);

    useEffect(() => {
        const interval = setInterval(() => {
            const thoughtTemplates = [
                'Evaluating goal progress and resource allocation',
                'Memory consolidation cycle initiated',
                'Plugin interaction patterns analyzed',
                'User intent classification: {confidence}% certainty',
                'Optimizing response generation strategy',
                'Cross-referencing memory contexts',
                'Reflex threshold monitoring active',
                'Goal priority rebalancing considered'
            ];

            const types: ThoughtEntry['type'][] = ['analysis', 'decision', 'observation', 'action'];

            const newThought: ThoughtEntry = {
                id: Date.now().toString(),
                timestamp: new Date().toLocaleTimeString(),
                thought: thoughtTemplates[Math.floor(Math.random() * thoughtTemplates.length)]
                    .replace('{confidence}', Math.floor(Math.random() * 20 + 80).toString()),
                type: types[Math.floor(Math.random() * types.length)],
                confidence: Math.random() * 0.3 + 0.7 // 70-100%
            };

            setThoughts(prev => [newThought, ...prev.slice(0, 19)]); // Keep only 20 most recent
        }, 4000);

        return () => clearInterval(interval);
    }, []);

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'analysis': return '🔍';
            case 'decision': return '⚖️';
            case 'observation': return '👁️';
            case 'action': return '⚡';
            default: return '🧠';
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'analysis': return 'text-blue-400';
            case 'decision': return 'text-purple-400';
            case 'observation': return 'text-green-400';
            case 'action': return 'text-orange-400';
            default: return 'text-gray-400';
        }
    };

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.9) return 'text-green-400';
        if (confidence >= 0.7) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <div className="p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">🧠 Lyrixa Thought Stream</h2>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsAutoScroll(!isAutoScroll)}
                        className={`px-3 py-1 rounded text-sm ${isAutoScroll ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300'
                            }`}
                    >
                        {isAutoScroll ? '📺 Live' : '⏸️ Paused'}
                    </button>
                    <div className="text-sm text-gray-400">
                        {thoughts.length} thoughts captured
                    </div>
                </div>
            </div>

            <div className="bg-gray-900 rounded-xl p-4 h-80 overflow-y-auto">
                <div className="space-y-2 font-mono text-sm">
                    {thoughts.map((thought, index) => (
                        <div
                            key={thought.id}
                            className={`flex items-start gap-3 p-2 rounded transition-all duration-500 ${index === 0 ? 'bg-blue-900 bg-opacity-30 animate-fade-in' : 'hover:bg-gray-800'
                                }`}
                        >
                            <div className="flex-shrink-0 w-20 text-xs text-gray-500">
                                [{thought.timestamp}]
                            </div>

                            <div className="flex-shrink-0">
                                <span className="text-lg">{getTypeIcon(thought.type)}</span>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className={`${getTypeColor(thought.type)} break-words`}>
                                    {thought.thought}
                                </div>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-xs text-gray-500 capitalize">
                                        {thought.type}
                                    </span>
                                    <span className={`text-xs ${getConfidenceColor(thought.confidence)}`}>
                                        {(thought.confidence * 100).toFixed(1)}% confidence
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {thoughts.length === 0 && (
                    <div className="text-center text-gray-500 py-12">
                        <div className="text-3xl mb-2">🧠</div>
                        <div>Waiting for thought activity...</div>
                    </div>
                )}
            </div>

            <div className="mt-4 bg-gray-800 p-3 rounded text-sm">
                <div className="flex items-center justify-between">
                    <span className="text-gray-400">
                        Real-time stream of Lyrixa's reasoning process and decision making
                    </span>
                    <div className="flex items-center gap-4 text-xs">
                        <div className="flex items-center gap-1">
                            <span>🔍 Analysis</span>
                            <span>⚖️ Decision</span>
                            <span>👁️ Observation</span>
                            <span>⚡ Action</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
