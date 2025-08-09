import { useEffect, useState } from 'react';

interface ReflexEvent {
    id: string;
    trigger: string;
    action: string;
    plugin: string;
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
    resolved: boolean;
}

export default function ReflexTrace() {
    const [reflexEvents, setReflexEvents] = useState<ReflexEvent[]>([
        {
            id: '1',
            trigger: 'Goal not progressing for 5 minutes',
            action: 'Triggered memory cleanup routine',
            plugin: 'memory_cleanser',
            timestamp: '14:27:15',
            severity: 'medium',
            resolved: true
        },
        {
            id: '2',
            trigger: 'Plugin failure threshold reached (3/5)',
            action: 'Disabled unstable plugin temporarily',
            plugin: 'summarizer_plugin',
            timestamp: '14:29:42',
            severity: 'high',
            resolved: true
        },
        {
            id: '3',
            trigger: 'User requested status update',
            action: 'Generated reflection summary',
            plugin: 'daily_reflector',
            timestamp: '14:31:08',
            severity: 'low',
            resolved: false
        }
    ]);

    const [newEventCounter, setNewEventCounter] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            if (Math.random() > 0.7) { // 30% chance every 5 seconds
                const newEvent: ReflexEvent = {
                    id: `${Date.now()}`,
                    trigger: 'Memory usage threshold exceeded (85%)',
                    action: 'Initiated memory optimization sequence',
                    plugin: 'memory_cleanser',
                    timestamp: new Date().toLocaleTimeString(),
                    severity: 'medium',
                    resolved: false
                };

                setReflexEvents(prev => [newEvent, ...prev.slice(0, 4)]); // Keep only 5 most recent
                setNewEventCounter(prev => prev + 1);

                // Auto-resolve after 3 seconds
                setTimeout(() => {
                    setReflexEvents(current =>
                        current.map(event =>
                            event.id === newEvent.id ? { ...event, resolved: true } : event
                        )
                    );
                }, 3000);
            }
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'high': return 'text-red-400 bg-red-900 bg-opacity-20';
            case 'medium': return 'text-yellow-400 bg-yellow-900 bg-opacity-20';
            case 'low': return 'text-blue-400 bg-blue-900 bg-opacity-20';
            default: return 'text-gray-400';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'high': return '🚨';
            case 'medium': return '⚠️';
            case 'low': return 'ℹ️';
            default: return '🔍';
        }
    };

    return (
        <div className="p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">🔁 Reflex Trace</h2>
                <div className="flex items-center gap-4">
                    <div className="text-sm text-gray-400">
                        {reflexEvents.filter(e => !e.resolved).length} active reflexes
                    </div>
                    {newEventCounter > 0 && (
                        <div className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                            +{newEventCounter} new
                        </div>
                    )}
                </div>
            </div>

            <div className="bg-gray-900 rounded-xl p-4 space-y-3 max-h-80 overflow-y-auto">
                {reflexEvents.map((event, index) => (
                    <div
                        key={event.id}
                        className={`p-3 rounded-lg border-l-4 transition-all duration-500 ${event.resolved
                                ? 'border-green-500 bg-gray-800'
                                : 'border-yellow-500 bg-yellow-900 bg-opacity-10 animate-pulse'
                            } ${index === 0 && newEventCounter > 0 ? 'animate-bounce' : ''}`}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <span className="text-lg">{getSeverityIcon(event.severity)}</span>
                                <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(event.severity)}`}>
                                    {event.severity.toUpperCase()}
                                </span>
                                <span className="text-xs text-gray-500">{event.timestamp}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-400">{event.plugin}</span>
                                {event.resolved ? (
                                    <span className="text-green-400 text-sm">✅</span>
                                ) : (
                                    <span className="text-yellow-400 text-sm animate-spin">⚙️</span>
                                )}
                            </div>
                        </div>

                        <div className="text-sm space-y-1">
                            <div className="text-gray-300">
                                <span className="text-red-400">Trigger:</span> {event.trigger}
                            </div>
                            <div className="text-gray-300">
                                <span className="text-green-400">Action:</span> {event.action}
                            </div>
                        </div>
                    </div>
                ))}

                {reflexEvents.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                        <div className="text-3xl mb-2">🧘</div>
                        <div>System running smoothly - no reflexes triggered</div>
                    </div>
                )}
            </div>

            <div className="mt-4 bg-gray-800 p-3 rounded text-xs">
                <div className="flex items-center justify-between">
                    <span className="text-gray-400">
                        Reflex system monitors for anomalies and triggers automatic responses
                    </span>
                    <button
                        onClick={() => setNewEventCounter(0)}
                        className="text-blue-400 hover:text-blue-300"
                    >
                        Mark as seen
                    </button>
                </div>
            </div>
        </div>
    );
}
