import { motion } from 'framer-motion';
import { useState } from 'react';
import { InteractiveExamples } from '../components/InteractiveExamples';
import { LiveAetherConsole } from '../components/LiveAetherConsole';
import { ScriptTutorials } from '../components/ScriptTutorials';
import { SyntaxReference } from '../components/SyntaxReference';

type LabView = 'console' | 'tutorials' | 'reference' | 'examples';

export default function AetherScriptLab() {
    const [activeView, setActiveView] = useState<LabView>('console');
    const [showReference, setShowReference] = useState(false);

    const views = [
        { id: 'console' as LabView, label: '🖥️ Live Console', description: 'Write and execute AetherScript in real-time' },
        { id: 'tutorials' as LabView, label: '📚 Tutorials', description: 'Interactive learning guides' },
        { id: 'examples' as LabView, label: '💻 Examples', description: 'Runnable code examples' },
        { id: 'reference' as LabView, label: '📖 Reference', description: 'Complete syntax documentation' }
    ];

    return (
        <div className="h-screen bg-gray-950 text-white flex flex-col overflow-hidden">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="bg-gray-900 border-b border-gray-700 px-6 py-4"
            >
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white flex items-center">
                            <span className="mr-3">⚗️</span>
                            AetherScript Development Lab
                        </h1>
                        <p className="text-gray-400 text-sm">
                            Advanced consciousness programming environment
                        </p>
                    </div>

                    <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1 bg-gray-800 rounded-lg p-1">
                            {views.map((view) => (
                                <button
                                    key={view.id}
                                    onClick={() => setActiveView(view.id)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeView === view.id
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-300 hover:text-white hover:bg-gray-700'
                                        }`}
                                    title={view.description}
                                >
                                    {view.label}
                                </button>
                            ))}
                        </div>

                        {(activeView === 'console' || activeView === 'examples') && (
                            <button
                                onClick={() => setShowReference(!showReference)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${showReference
                                        ? 'bg-green-600 text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                    }`}
                            >
                                📚 Reference Panel
                            </button>
                        )}
                    </div>
                </div>
            </motion.div>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden">
                {/* Primary Content */}
                <motion.div
                    key={activeView}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`${showReference && (activeView === 'console' || activeView === 'examples') ? 'flex-1' : 'w-full'} overflow-hidden`}
                >
                    {activeView === 'console' && (
                        <div className="h-full p-6">
                            <LiveAetherConsole />
                        </div>
                    )}

                    {activeView === 'tutorials' && (
                        <div className="h-full">
                            <ScriptTutorials />
                        </div>
                    )}

                    {activeView === 'examples' && (
                        <div className="h-full">
                            <InteractiveExamples />
                        </div>
                    )}

                    {activeView === 'reference' && (
                        <div className="h-full">
                            <SyntaxReference />
                        </div>
                    )}
                </motion.div>

                {/* Reference Panel (for console and examples views) */}
                {showReference && (activeView === 'console' || activeView === 'examples') && (
                    <motion.div
                        initial={{ opacity: 0, x: 300 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 300 }}
                        transition={{ duration: 0.3 }}
                        className="w-96 border-l border-gray-700 bg-gray-900"
                    >
                        <div className="h-full">
                            <SyntaxReference />
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Status Bar */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="bg-gray-900 border-t border-gray-700 px-6 py-2 text-xs text-gray-400"
            >
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                        <span>AetherScript Lab v2.1.0</span>
                        <span>Consciousness-Safe Environment</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span>System Ready</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-6">
                        <span>Memory: 45.2MB / 128MB</span>
                        <span>Active Processes: 3</span>
                        <span>Consciousness Level: Optimal</span>
                    </div>
                </div>
            </motion.div>

            {/* Loading Overlay for view transitions */}
            <motion.div
                key={`${activeView}-loading`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 0 }}
                transition={{ duration: 0.1 }}
                className="fixed inset-0 bg-black/50 flex items-center justify-center pointer-events-none"
            >
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 flex items-center space-x-3">
                    <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-white">Loading {views.find(v => v.id === activeView)?.label}...</span>
                </div>
            </motion.div>
        </div>
    );
}
