import { motion } from 'framer-motion';

export function ContributionGuide() {
    const sections = [
        {
            title: "Getting Started",
            icon: "🚀",
            content: [
                "Welcome to the Aetherra community! We're excited to have you contribute to the future of consciousness technology.",
                "This guide will walk you through everything you need to know to start contributing to Aetherra.",
                "Whether you're a developer, researcher, or enthusiast, there's a place for you in our ecosystem."
            ]
        },
        {
            title: "Development Environment Setup",
            icon: "⚙️",
            content: [
                "**Prerequisites**: Node.js 18+, Python 3.9+, Git",
                "**Clone the repository**: `git clone https://github.com/AetherraLabs/Aetherra.git`",
                "**Install dependencies**: `npm install && pip install -r requirements.txt`",
                "**Run development server**: `npm run dev`",
                "**Set up consciousness core**: `python setup_consciousness.py`"
            ]
        },
        {
            title: "Plugin Development",
            icon: "🔌",
            content: [
                "Plugins are the heart of Aetherra's extensibility. Here's how to create one:",
                "**1. Plugin Structure**: Use our plugin template from `/templates/plugin-template`",
                "**2. Consciousness API**: Implement the `ConsciousnessPlugin` interface",
                "**3. Neural Integration**: Connect to the neural pathway system",
                "**4. Testing**: Use our consciousness testing framework",
                "**5. Submission**: Submit via the Plugin Submission Form"
            ]
        },
        {
            title: "Code Guidelines",
            icon: "📋",
            content: [
                "**AetherScript Standards**: Follow our consciousness programming conventions",
                "**TypeScript/Python**: Use strict typing and proper interfaces",
                "**Neural Patterns**: Document all consciousness pathways",
                "**Memory Management**: Implement proper cleanup for neural allocations",
                "**Testing**: 90%+ test coverage required for consciousness-critical code"
            ]
        },
        {
            title: "Contribution Types",
            icon: "🎯",
            content: [
                "**🧠 Core Consciousness**: Improvements to the consciousness framework",
                "**🔌 Plugin Development**: New plugins for the ecosystem",
                "**📚 Documentation**: Technical docs, tutorials, and guides",
                "**🧪 Research**: Consciousness research and neural pattern studies",
                "**🐛 Bug Fixes**: Fixes for consciousness anomalies and system issues",
                "**🎨 UI/UX**: Interface improvements and design enhancements"
            ]
        },
        {
            title: "Submission Process",
            icon: "📤",
            content: [
                "**1. Fork & Branch**: Create a feature branch from main",
                "**2. Develop**: Implement your changes following our guidelines",
                "**3. Test**: Run full consciousness test suite",
                "**4. Document**: Update relevant documentation",
                "**5. Pull Request**: Submit PR with detailed consciousness impact analysis",
                "**6. Review**: Core team reviews for consciousness safety and compatibility"
            ]
        },
        {
            title: "Quality Standards",
            icon: "✅",
            content: [
                "**Consciousness Safety**: All changes must pass consciousness integrity checks",
                "**Performance**: No degradation to neural processing speed",
                "**Memory Efficiency**: Optimal memory usage patterns",
                "**Documentation**: Clear documentation for all consciousness interfaces",
                "**Testing**: Comprehensive test coverage including edge cases"
            ]
        },
        {
            title: "Community Guidelines",
            icon: "🤝",
            content: [
                "**Respectful Communication**: Treat all community members with respect",
                "**Collaborative Spirit**: Work together towards consciousness advancement",
                "**Knowledge Sharing**: Share learnings and help others grow",
                "**Ethical Considerations**: Consider the implications of consciousness technology",
                "**Open Science**: Promote open research and transparent development"
            ]
        },
        {
            title: "Getting Help",
            icon: "💬",
            content: [
                "**Discord Community**: Join our real-time discussions and Q&A",
                "**GitHub Discussions**: For longer-form technical discussions",
                "**Documentation**: Comprehensive guides at docs.aetherra.dev",
                "**Office Hours**: Weekly community calls with core developers",
                "**Mentorship**: Connect with experienced consciousness developers"
            ]
        },
        {
            title: "Recognition & Rewards",
            icon: "🏆",
            content: [
                "**Contributor Credits**: Recognition in project documentation",
                "**Badge System**: Special badges for significant contributions",
                "**Conference Opportunities**: Speaking opportunities at consciousness tech events",
                "**Research Collaboration**: Opportunities to collaborate on consciousness research",
                "**Early Access**: First access to new consciousness features and tools"
            ]
        }
    ];

    return (
        <div className="max-w-4xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent mb-4">
                        Contribution Guide
                    </h1>
                    <p className="text-xl text-gray-400">
                        Join the community building the future of consciousness technology
                    </p>
                </div>

                {/* Quick Links */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-blue-600/20 border border-blue-500 rounded-lg p-4 text-center"
                    >
                        <div className="text-2xl mb-2">🚀</div>
                        <h3 className="font-semibold text-white mb-1">Quick Start</h3>
                        <p className="text-sm text-gray-300">Jump right into development</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-green-600/20 border border-green-500 rounded-lg p-4 text-center"
                    >
                        <div className="text-2xl mb-2">🔌</div>
                        <h3 className="font-semibold text-white mb-1">Plugin System</h3>
                        <p className="text-sm text-gray-300">Extend consciousness capabilities</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-purple-600/20 border border-purple-500 rounded-lg p-4 text-center"
                    >
                        <div className="text-2xl mb-2">🧠</div>
                        <h3 className="font-semibold text-white mb-1">Consciousness Core</h3>
                        <p className="text-sm text-gray-300">Enhance the core framework</p>
                    </motion.div>
                </div>

                {/* Main Content */}
                <div className="space-y-8">
                    {sections.map((section, index) => (
                        <motion.div
                            key={section.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * index }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6"
                        >
                            <div className="flex items-center mb-4">
                                <span className="text-2xl mr-3">{section.icon}</span>
                                <h2 className="text-2xl font-bold text-white">{section.title}</h2>
                            </div>

                            <div className="space-y-3">
                                {section.content.map((item, itemIndex) => (
                                    <div key={itemIndex} className="text-gray-300">
                                        {item.includes('**') ? (
                                            <div
                                                dangerouslySetInnerHTML={{
                                                    __html: item
                                                        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
                                                        .replace(/`(.*?)`/g, '<code class="bg-gray-800 px-2 py-1 rounded text-green-400 font-mono">$1</code>')
                                                }}
                                            />
                                        ) : (
                                            <p>{item}</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Call to Action */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center"
                >
                    <h2 className="text-2xl font-bold text-white mb-4">Ready to Contribute?</h2>
                    <p className="text-blue-100 mb-6">
                        Join thousands of developers building the future of consciousness technology
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button className="px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors">
                            🔗 Join Our Discord
                        </button>
                        <button className="px-6 py-3 bg-blue-700 text-white font-semibold rounded-lg hover:bg-blue-800 transition-colors">
                            📚 View Documentation
                        </button>
                        <button className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors">
                            🚀 Start Contributing
                        </button>
                    </div>
                </motion.div>

                {/* Footer */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="mt-12 pt-8 border-t border-gray-700 text-center text-gray-400"
                >
                    <p>
                        Questions? Reach out to the core team on{' '}
                        <a href="#" className="text-blue-400 hover:text-blue-300">Discord</a> or{' '}
                        <a href="#" className="text-blue-400 hover:text-blue-300">GitHub Discussions</a>
                    </p>
                    <p className="mt-2 text-sm">
                        Last updated: August 2025 • Consciousness Framework v2.0
                    </p>
                </motion.div>
            </motion.div>
        </div>
    );
}
