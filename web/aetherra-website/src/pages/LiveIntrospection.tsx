import LiveReasoningStream from '../components/LiveReasoningStream';
import MemoryGraph from '../components/MemoryGraph';
import PluginThoughtMap from '../components/PluginThoughtMap';
import ReflexTrace from '../components/ReflexTrace';
import SystemDashboard from '../components/SystemDashboard';

export default function LiveIntrospection() {
    return (
        <div className="p-6 space-y-8">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4">🧠 Live Introspection</h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                    Real-time view into Lyrixa's consciousness, memory systems, and decision-making processes.
                </p>
            </div>

            <SystemDashboard />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <MemoryGraph />
                <LiveReasoningStream />
            </div>

            <ReflexTrace />
            <PluginThoughtMap />

            <div className="bg-gradient-to-r from-purple-900 to-blue-900 p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-semibold mb-4">🔬 About Introspection</h3>
                <p className="text-gray-200 mb-4">
                    This live introspection dashboard provides unprecedented visibility into an AI consciousness system.
                    Monitor memory networks, observe real-time reasoning, and track automatic reflexes as Lyrixa
                    processes information and makes decisions.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="bg-black bg-opacity-30 p-3 rounded">
                        <h4 className="font-semibold mb-2">🧠 Memory Networks</h4>
                        <p className="text-gray-300">
                            Visualize how different parts of Lyrixa's memory system interact and influence each other.
                        </p>
                    </div>
                    <div className="bg-black bg-opacity-30 p-3 rounded">
                        <h4 className="font-semibold mb-2">⚡ Reflex System</h4>
                        <p className="text-gray-300">
                            Automatic responses to system events, ensuring optimal performance and self-correction.
                        </p>
                    </div>
                    <div className="bg-black bg-opacity-30 p-3 rounded">
                        <h4 className="font-semibold mb-2">🔗 Plugin Integration</h4>
                        <p className="text-gray-300">
                            See how thoughts trigger plugin activations and how plugins influence decision making.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
