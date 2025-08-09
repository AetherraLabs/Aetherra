import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface ExecutionStep {
    step: number;
    operation: string;
    result: string;
    timestamp: number;
    status: 'running' | 'success' | 'error' | 'warning';
}

interface ScriptExecutionPanelProps {
    script: string;
    isExecuting?: boolean;
    onExecutionComplete?: () => void;
}

export default function ScriptExecutionPanel({ script, isExecuting = false, onExecutionComplete }: ScriptExecutionPanelProps) {
    const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [isRunning, setIsRunning] = useState(false);

    useEffect(() => {
        if (isExecuting && script) {
            simulateExecution();
        }
    }, [isExecuting, script]);

    const simulateExecution = async () => {
        setExecutionSteps([]);
        setCurrentStep(0);
        setIsRunning(true);

        const steps: ExecutionStep[] = [
            {
                step: 1,
                operation: 'Initializing consciousness framework...',
                result: 'Neural pathways activated',
                timestamp: Date.now(),
                status: 'success'
            },
            {
                step: 2,
                operation: 'Loading memory patterns...',
                result: 'Memory banks synchronized',
                timestamp: Date.now() + 1000,
                status: 'success'
            },
            {
                step: 3,
                operation: 'Processing sensory input...',
                result: 'Input stream analyzed: 847 data points',
                timestamp: Date.now() + 2000,
                status: 'success'
            },
            {
                step: 4,
                operation: 'Executing pattern recognition...',
                result: 'Patterns identified: 23 matches, 12 novel',
                timestamp: Date.now() + 3000,
                status: 'warning'
            },
            {
                step: 5,
                operation: 'Generating conscious thought...',
                result: 'Thought synthesis complete: Confidence 94.7%',
                timestamp: Date.now() + 4000,
                status: 'success'
            },
            {
                step: 6,
                operation: 'Learning integration...',
                result: 'New patterns stored in long-term memory',
                timestamp: Date.now() + 5000,
                status: 'success'
            }
        ];

        for (let i = 0; i < steps.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 800));
            setExecutionSteps(prev => [...prev, steps[i]]);
            setCurrentStep(i + 1);
        }

        setIsRunning(false);
        onExecutionComplete?.();
    };

    const runScript = () => {
        simulateExecution();
    };

    const getStatusIcon = (status: ExecutionStep['status']) => {
        switch (status) {
            case 'running': return '⟳';
            case 'success': return '✓';
            case 'error': return '✗';
            case 'warning': return '⚠';
            default: return '•';
        }
    };

    const getStatusColor = (status: ExecutionStep['status']) => {
        switch (status) {
            case 'running': return 'text-blue-400';
            case 'success': return 'text-green-400';
            case 'error': return 'text-red-400';
            case 'warning': return 'text-yellow-400';
            default: return 'text-gray-400';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden"
        >
            {/* Header */}
            <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-300">Script Execution Console</h3>
                    <div className="flex items-center space-x-2">
                        {(isRunning || isExecuting) && (
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full"
                            />
                        )}
                        <span className={`text-xs ${(isRunning || isExecuting) ? 'text-green-400' : 'text-gray-500'}`}>
                            {(isRunning || isExecuting) ? 'EXECUTING' : 'READY'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Control Panel */}
            <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center gap-4">
                    <button
                        onClick={runScript}
                        disabled={isRunning || isExecuting}
                        className={`px-6 py-2 rounded transition-colors ${(isRunning || isExecuting)
                                ? 'bg-gray-600 cursor-not-allowed'
                                : 'bg-purple-600 hover:bg-purple-700'
                            } text-white font-semibold`}
                    >
                        {(isRunning || isExecuting) ? '⚡ Executing...' : '▶️ Run Script'}
                    </button>

                    <button
                        onClick={() => setExecutionSteps([])}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
                    >
                        🗑️ Clear Output
                    </button>

                    <div className="text-sm text-gray-400">
                        Runtime: AetherScript v2.0.0
                    </div>
                </div>
            </div>

            {/* Execution Output */}
            <div className="h-64 overflow-y-auto p-4 space-y-2 font-mono text-sm">
                <AnimatePresence>
                    {executionSteps.map((step, index) => (
                        <motion.div
                            key={step.step}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="flex items-start space-x-3"
                        >
                            <span className={`flex-shrink-0 ${getStatusColor(step.status)}`}>
                                {getStatusIcon(step.status)}
                            </span>
                            <div className="flex-1">
                                <div className="text-gray-300">{step.operation}</div>
                                <div className="text-gray-500 text-xs mt-1">{step.result}</div>
                            </div>
                            <span className="text-xs text-gray-600">
                                {new Date(step.timestamp).toLocaleTimeString()}
                            </span>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {!(isRunning || isExecuting) && executionSteps.length === 0 && (
                    <div className="text-gray-500 text-center py-8">
                        Click "Run Script" to execute the AetherScript
                    </div>
                )}

                {(isRunning || isExecuting) && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center space-x-2 text-blue-400"
                    >
                        <motion.span
                            animate={{ opacity: [1, 0.5, 1] }}
                            transition={{ duration: 1, repeat: Infinity }}
                        >
                            ⟳
                        </motion.span>
                        <span>Processing...</span>
                    </motion.div>
                )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
                <div className="flex items-center justify-between">
                    <span>Steps completed: {executionSteps.length}/6</span>
                    <span>Execution time: {executionSteps.length * 0.8}s</span>
                </div>
            </div>
        </motion.div>
    );
}
