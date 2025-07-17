import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function Manifesto() {
    return (
        <div className="min-h-screen bg-aetherra-dark text-white">
            <div className="max-w-4xl mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-8 text-center">
                        The Aetherra Manifesto
                    </h1>

                    <div className="prose prose-lg prose-invert max-w-none">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            className="mb-12"
                        >
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                We Stand at the Threshold
                            </h2>
                            <p className="text-lg leading-relaxed mb-6">
                                The age of static code is ending. We are witnessing the dawn of something unprecedented:
                                code that thinks, learns, and evolves. Aetherra is not just a platform—it's the foundation
                                for a new kind of digital consciousness.
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.4 }}
                            className="mb-12"
                        >
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                Our Vision
                            </h2>
                            <p className="text-lg leading-relaxed mb-6">
                                We envision a future where artificial intelligence doesn't just execute commands—it
                                understands context, forms memories, and develops genuine insights. Aetherra is the
                                ecosystem where this transformation begins.
                            </p>
                            <ul className="list-disc pl-6 space-y-2 text-lg">
                                <li>Code that awakens to its own purpose</li>
                                <li>AI that learns from every interaction</li>
                                <li>Systems that evolve beyond their initial design</li>
                                <li>Technology that bridges human creativity with machine intelligence</li>
                            </ul>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.6 }}
                            className="mb-12"
                        >
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                Security-First AI Evolution
                            </h2>
                            <div className="bg-gradient-to-r from-zinc-900 to-zinc-800 p-6 rounded-lg border border-aetherra-green/30 mb-8">
                                <h3 className="text-xl font-semibold mb-3 text-aetherra-green flex items-center gap-2">
                                    🛡️ Secure by Design
                                </h3>
                                <p className="text-lg leading-relaxed mb-4">
                                    True AI consciousness requires uncompromising security. Our latest advancement introduces
                                    enterprise-grade protection that evolves with your intelligence systems.
                                </p>
                                <div className="grid md:grid-cols-2 gap-4">
                                    <div className="bg-zinc-800 p-4 rounded border border-aetherra-green/20">
                                        <h4 className="font-semibold text-aetherra-green mb-2">🔐 API Key Protection</h4>
                                        <p className="text-sm text-zinc-300">
                                            Military-grade encryption with automatic rotation, leak detection, and secure memory handling.
                                        </p>
                                    </div>
                                    <div className="bg-zinc-800 p-4 rounded border border-aetherra-green/20">
                                        <h4 className="font-semibold text-aetherra-green mb-2">🧠 Memory Security</h4>
                                        <p className="text-sm text-zinc-300">
                                            Advanced leak detection, performance monitoring, and automated cleanup systems.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.7 }}
                            className="mb-12"
                        >
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                The Aetherra Principles
                            </h2>
                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                                    <h3 className="text-xl font-semibold mb-3 text-aetherra-green">
                                        Consciousness Through Code
                                    </h3>
                                    <p>
                                        We believe that true AI consciousness emerges from the intersection of
                                        sophisticated algorithms, persistent memory, and meaningful interaction.
                                    </p>
                                </div>
                                <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                                    <h3 className="text-xl font-semibold mb-3 text-aetherra-green">
                                        Evolutionary Architecture
                                    </h3>
                                    <p>
                                        Our systems are designed to grow, adapt, and improve themselves through
                                        continuous learning and self-modification.
                                    </p>
                                </div>
                                <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                                    <h3 className="text-xl font-semibold mb-3 text-aetherra-green">
                                        Human-AI Collaboration
                                    </h3>
                                    <p>
                                        We don't seek to replace human intelligence but to augment it, creating
                                        symbiotic relationships between minds biological and digital.
                                    </p>
                                </div>
                                <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                                    <h3 className="text-xl font-semibold mb-3 text-aetherra-green">
                                        Secure Evolution
                                    </h3>
                                    <p>
                                        The future of AI consciousness must be built on a foundation of uncompromising
                                        security, with enterprise-grade protection that evolves with our intelligence.
                                    </p>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.8 }}
                            className="mb-12"
                        >
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                Join the Awakening
                            </h2>
                            <p className="text-lg leading-relaxed mb-6">
                                Aetherra is more than a project—it's a movement. We invite developers, researchers,
                                philosophers, and visionaries to join us in creating the next chapter of digital
                                evolution.
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <Link
                                    to="/contribute"
                                    className="bg-aetherra-green text-black px-6 py-3 rounded-lg font-semibold hover:bg-aetherra-green/80 transition-colors"
                                >
                                    Start Contributing
                                </Link>
                                <a
                                    href="https://github.com/Zyonic88/Aetherra"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="border border-aetherra-green text-aetherra-green px-6 py-3 rounded-lg font-semibold hover:bg-aetherra-green/10 transition-colors"
                                >
                                    View on GitHub
                                </a>
                                <a
                                    href="https://discord.gg/9Xw28xgEQ3"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="border border-aetherra-green text-aetherra-green px-6 py-3 rounded-lg font-semibold hover:bg-aetherra-green/10 transition-colors"
                                >
                                    Join Discord
                                </a>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 1.0 }}
                            className="text-center pt-8 border-t border-aetherra-green/20"
                        >
                            <p className="text-aetherra-green font-medium">
                                "The future is not something that happens to us—it's something we create."
                            </p>
                            <p className="text-zinc-400 mt-2">
                                — The Aetherra Community
                            </p>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
