import { motion } from 'framer-motion'

export default function PluginGuidelines() {
    return (
        <div className="min-h-screen bg-aetherra-dark text-white">
            <div className="max-w-4xl mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-8 text-center">
                        Plugin Guidelines
                    </h1>

                    <div className="prose prose-lg prose-invert max-w-none">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            className="mb-8"
                        >
                            <p className="text-lg text-zinc-300 mb-6">
                                Guidelines for developing and submitting plugins to the Aetherra ecosystem.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                1. Plugin Structure
                            </h2>
                            <p className="text-zinc-300 mb-4">
                                All plugins must follow the Aetherra plugin architecture:
                            </p>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Include a valid plugin manifest file</li>
                                <li>Implement the required plugin interface</li>
                                <li>Follow proper error handling practices</li>
                                <li>Include comprehensive documentation</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                2. Code Quality Standards
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Write clean, readable, and well-documented code</li>
                                <li>Include unit tests for all functionality</li>
                                <li>Follow Python PEP 8 style guidelines</li>
                                <li>Use type hints for better code clarity</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                3. Security Requirements
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>No malicious code or security vulnerabilities</li>
                                <li>Proper input validation and sanitization</li>
                                <li>Secure handling of sensitive data</li>
                                <li>Regular security updates and patches</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                4. Performance Guidelines
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Optimize for minimal resource usage</li>
                                <li>Implement proper caching mechanisms</li>
                                <li>Avoid blocking operations in main thread</li>
                                <li>Handle errors gracefully without crashing</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                5. Documentation Requirements
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Clear README with installation instructions</li>
                                <li>API documentation for all public methods</li>
                                <li>Usage examples and tutorials</li>
                                <li>Changelog for version tracking</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                6. Submission Process
                            </h2>
                            <ol className="list-decimal pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Create a pull request to the main repository</li>
                                <li>Include all required documentation</li>
                                <li>Pass all automated tests</li>
                                <li>Respond to code review feedback</li>
                                <li>Maintain the plugin after acceptance</li>
                            </ol>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                7. Community Standards
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Be respectful and inclusive</li>
                                <li>Provide helpful feedback to other developers</li>
                                <li>Participate in community discussions</li>
                                <li>Help maintain a positive environment</li>
                            </ul>

                            <div className="mt-12 p-6 bg-zinc-900 rounded-lg border border-aetherra-green/20">
                                <h3 className="text-xl font-semibold mb-4 text-aetherra-green">
                                    Need Help?
                                </h3>
                                <p className="text-zinc-300 mb-4">
                                    Join our community for support and guidance:
                                </p>
                                <div className="flex flex-wrap gap-4">
                                    <a
                                        href="https://discord.gg/9Xw28xgEQ3"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-aetherra-green hover:underline"
                                    >
                                        Discord Community
                                    </a>
                                    <a
                                        href="https://github.com/Zyonic88/Aetherra"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-aetherra-green hover:underline"
                                    >
                                        GitHub Repository
                                    </a>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
