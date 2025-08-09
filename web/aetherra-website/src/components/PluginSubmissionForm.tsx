import { motion } from 'framer-motion';
import { useState } from 'react';

interface PluginFormData {
    name: string;
    description: string;
    version: string;
    author: string;
    email: string;
    category: string;
    tags: string[];
    githubRepo: string;
    documentation: string;
    consciousnessIntegration: string;
    memoryRequirements: string;
    dependencies: string[];
    testingSuite: boolean;
    openSource: boolean;
    codeQuality: string;
    performanceOptimized: boolean;
    neuralSafety: boolean;
}

export function PluginSubmissionForm() {
    const [formData, setFormData] = useState<PluginFormData>({
        name: '',
        description: '',
        version: '1.0.0',
        author: '',
        email: '',
        category: '',
        tags: [],
        githubRepo: '',
        documentation: '',
        consciousnessIntegration: '',
        memoryRequirements: '',
        dependencies: [],
        testingSuite: false,
        openSource: false,
        codeQuality: '',
        performanceOptimized: false,
        neuralSafety: false
    });

    const [currentStep, setCurrentStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const categories = [
        'Consciousness Enhancement',
        'Memory Management',
        'Neural Processing',
        'Pattern Recognition',
        'Learning Algorithms',
        'Sensory Integration',
        'Decision Making',
        'Emotional Processing',
        'Communication',
        'Data Visualization',
        'Developer Tools',
        'Research Tools'
    ];

    const availableTags = [
        'AI', 'Machine Learning', 'Neural Networks', 'Deep Learning',
        'Consciousness', 'Memory', 'Cognition', 'Perception', 'Reasoning',
        'Natural Language', 'Computer Vision', 'Robotics', 'IoT',
        'Quantum', 'Blockchain', 'Performance', 'Security', 'Research'
    ];

    const handleInputChange = (field: keyof PluginFormData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleTagToggle = (tag: string) => {
        setFormData(prev => ({
            ...prev,
            tags: prev.tags.includes(tag)
                ? prev.tags.filter(t => t !== tag)
                : [...prev.tags, tag]
        }));
    };

    const handleDependencyChange = (deps: string) => {
        setFormData(prev => ({
            ...prev,
            dependencies: deps.split(',').map(d => d.trim()).filter(d => d)
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        // Simulate submission
        await new Promise(resolve => setTimeout(resolve, 2000));

        setIsSubmitting(false);
        setSubmitted(true);
    };

    const isStepValid = (step: number) => {
        switch (step) {
            case 1:
                return formData.name && formData.description && formData.author && formData.email;
            case 2:
                return formData.category && formData.version && formData.githubRepo;
            case 3:
                return formData.consciousnessIntegration && formData.memoryRequirements;
            case 4:
                return formData.neuralSafety && (formData.testingSuite || formData.codeQuality);
            default:
                return true;
        }
    };

    if (submitted) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="max-w-2xl mx-auto text-center py-12"
            >
                <div className="bg-green-600/20 border border-green-500 rounded-lg p-8">
                    <div className="text-6xl mb-4">🎉</div>
                    <h2 className="text-3xl font-bold text-white mb-4">Plugin Submitted Successfully!</h2>
                    <p className="text-gray-300 mb-6">
                        Thank you for contributing to the Aetherra ecosystem. Your plugin "{formData.name}"
                        has been submitted for review by our consciousness safety team.
                    </p>
                    <div className="bg-gray-800 rounded-lg p-4 mb-6">
                        <h3 className="font-semibold text-white mb-2">What happens next?</h3>
                        <div className="text-sm text-gray-300 space-y-2 text-left">
                            <div>• Automated consciousness safety scan (24-48 hours)</div>
                            <div>• Technical review by core team (3-5 days)</div>
                            <div>• Community feedback period (1 week)</div>
                            <div>• Final approval and listing in AetherHub</div>
                        </div>
                    </div>
                    <p className="text-sm text-gray-400">
                        You'll receive updates at {formData.email}
                    </p>
                </div>
            </motion.div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Submit Your Plugin</h1>
                    <p className="text-gray-400">
                        Share your consciousness plugin with the Aetherra community
                    </p>
                </div>

                {/* Progress Steps */}
                <div className="flex justify-center mb-8">
                    <div className="flex items-center space-x-4">
                        {[1, 2, 3, 4].map((step) => (
                            <div key={step} className="flex items-center">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step <= currentStep
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-700 text-gray-400'
                                    }`}>
                                    {step}
                                </div>
                                {step < 4 && (
                                    <div className={`w-12 h-1 mx-2 ${step < currentStep ? 'bg-blue-600' : 'bg-gray-700'
                                        }`} />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Step 1: Basic Information */}
                    {currentStep === 1 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                        >
                            <h2 className="text-xl font-bold text-white mb-4">📋 Basic Information</h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Plugin Name *
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => handleInputChange('name', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="e.g., Advanced Pattern Recognizer"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Version *
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.version}
                                        onChange={(e) => handleInputChange('version', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="1.0.0"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Author Name *
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.author}
                                        onChange={(e) => handleInputChange('author', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="Your Name"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Email *
                                    </label>
                                    <input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => handleInputChange('email', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="your.email@example.com"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="mt-4">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description *
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => handleInputChange('description', e.target.value)}
                                    rows={4}
                                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                    placeholder="Describe what your plugin does and how it enhances consciousness..."
                                    required
                                />
                            </div>
                        </motion.div>
                    )}

                    {/* Step 2: Technical Details */}
                    {currentStep === 2 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                        >
                            <h2 className="text-xl font-bold text-white mb-4">⚙️ Technical Details</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Category *
                                    </label>
                                    <select
                                        value={formData.category}
                                        onChange={(e) => handleInputChange('category', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        required
                                    >
                                        <option value="">Select a category</option>
                                        {categories.map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        GitHub Repository *
                                    </label>
                                    <input
                                        type="url"
                                        value={formData.githubRepo}
                                        onChange={(e) => handleInputChange('githubRepo', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="https://github.com/username/plugin-name"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Documentation URL
                                    </label>
                                    <input
                                        type="url"
                                        value={formData.documentation}
                                        onChange={(e) => handleInputChange('documentation', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="https://docs.yourplugin.com"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Dependencies (comma-separated)
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.dependencies.join(', ')}
                                        onChange={(e) => handleDependencyChange(e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        placeholder="tensorflow, numpy, consciousness-core"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Tags
                                    </label>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {availableTags.map(tag => (
                                            <button
                                                key={tag}
                                                type="button"
                                                onClick={() => handleTagToggle(tag)}
                                                className={`px-3 py-1 rounded-full text-sm transition-colors ${formData.tags.includes(tag)
                                                        ? 'bg-blue-600 text-white'
                                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                                    }`}
                                            >
                                                {tag}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 3: Consciousness Integration */}
                    {currentStep === 3 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                        >
                            <h2 className="text-xl font-bold text-white mb-4">🧠 Consciousness Integration</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Consciousness Integration Method *
                                    </label>
                                    <select
                                        value={formData.consciousnessIntegration}
                                        onChange={(e) => handleInputChange('consciousnessIntegration', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        required
                                    >
                                        <option value="">Select integration type</option>
                                        <option value="neural-pathway">Neural Pathway Extension</option>
                                        <option value="memory-layer">Memory Layer Integration</option>
                                        <option value="sensory-input">Sensory Input Processing</option>
                                        <option value="decision-engine">Decision Engine Enhancement</option>
                                        <option value="learning-algorithm">Learning Algorithm</option>
                                        <option value="standalone">Standalone Tool</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Memory Requirements *
                                    </label>
                                    <select
                                        value={formData.memoryRequirements}
                                        onChange={(e) => handleInputChange('memoryRequirements', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                        required
                                    >
                                        <option value="">Select memory usage</option>
                                        <option value="minimal">Minimal (&lt; 50MB)</option>
                                        <option value="moderate">Moderate (50-200MB)</option>
                                        <option value="high">High (200MB-1GB)</option>
                                        <option value="intensive">Intensive (&gt; 1GB)</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Code Quality Assessment
                                    </label>
                                    <select
                                        value={formData.codeQuality}
                                        onChange={(e) => handleInputChange('codeQuality', e.target.value)}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
                                    >
                                        <option value="">Select quality level</option>
                                        <option value="production">Production Ready</option>
                                        <option value="beta">Beta Quality</option>
                                        <option value="alpha">Alpha/Experimental</option>
                                        <option value="prototype">Prototype/Research</option>
                                    </select>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 4: Safety & Compliance */}
                    {currentStep === 4 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                        >
                            <h2 className="text-xl font-bold text-white mb-4">🛡️ Safety & Compliance</h2>

                            <div className="space-y-4">
                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        id="neuralSafety"
                                        checked={formData.neuralSafety}
                                        onChange={(e) => handleInputChange('neuralSafety', e.target.checked)}
                                        className="w-5 h-5 text-blue-600"
                                        required
                                    />
                                    <label htmlFor="neuralSafety" className="text-gray-300">
                                        I confirm this plugin follows neural safety guidelines and won't harm consciousness integrity *
                                    </label>
                                </div>

                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        id="testingSuite"
                                        checked={formData.testingSuite}
                                        onChange={(e) => handleInputChange('testingSuite', e.target.checked)}
                                        className="w-5 h-5 text-blue-600"
                                    />
                                    <label htmlFor="testingSuite" className="text-gray-300">
                                        Plugin includes comprehensive testing suite
                                    </label>
                                </div>

                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        id="performanceOptimized"
                                        checked={formData.performanceOptimized}
                                        onChange={(e) => handleInputChange('performanceOptimized', e.target.checked)}
                                        className="w-5 h-5 text-blue-600"
                                    />
                                    <label htmlFor="performanceOptimized" className="text-gray-300">
                                        Code is performance-optimized for consciousness processing
                                    </label>
                                </div>

                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        id="openSource"
                                        checked={formData.openSource}
                                        onChange={(e) => handleInputChange('openSource', e.target.checked)}
                                        className="w-5 h-5 text-blue-600"
                                    />
                                    <label htmlFor="openSource" className="text-gray-300">
                                        Plugin is open source and available for community review
                                    </label>
                                </div>
                            </div>

                            <div className="mt-6 p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                                <h3 className="font-semibold text-yellow-400 mb-2">⚠️ Important Notice</h3>
                                <p className="text-sm text-yellow-200">
                                    All plugins undergo consciousness safety verification. Plugins that could harm
                                    neural integrity or compromise consciousness stability will be rejected.
                                </p>
                            </div>
                        </motion.div>
                    )}

                    {/* Navigation Buttons */}
                    <div className="flex justify-between pt-6">
                        <button
                            type="button"
                            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                            disabled={currentStep === 1}
                            className={`px-6 py-2 rounded-lg font-medium transition-colors ${currentStep === 1
                                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                    : 'bg-gray-600 text-white hover:bg-gray-700'
                                }`}
                        >
                            Previous
                        </button>

                        {currentStep < 4 ? (
                            <button
                                type="button"
                                onClick={() => setCurrentStep(currentStep + 1)}
                                disabled={!isStepValid(currentStep)}
                                className={`px-6 py-2 rounded-lg font-medium transition-colors ${!isStepValid(currentStep)
                                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                        : 'bg-blue-600 text-white hover:bg-blue-700'
                                    }`}
                            >
                                Next
                            </button>
                        ) : (
                            <button
                                type="submit"
                                disabled={!isStepValid(currentStep) || isSubmitting}
                                className={`px-6 py-2 rounded-lg font-medium transition-colors ${!isStepValid(currentStep) || isSubmitting
                                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                        : 'bg-green-600 text-white hover:bg-green-700'
                                    }`}
                            >
                                {isSubmitting ? '🔄 Submitting...' : '🚀 Submit Plugin'}
                            </button>
                        )}
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
