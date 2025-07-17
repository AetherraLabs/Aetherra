import { motion } from 'framer-motion'

export default function Terms() {
    return (
        <div className="min-h-screen bg-aetherra-dark text-white">
            <div className="max-w-4xl mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-8 text-center">
                        Terms and Conditions
                    </h1>

                    <div className="prose prose-lg prose-invert max-w-none">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            className="mb-8"
                        >
                            <p className="text-lg text-zinc-300 mb-6">
                                Last updated: July 16, 2025
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                1. Acceptance of Terms
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                By accessing or using the Aetherra platform, you agree to be bound by these Terms and Conditions.
                                If you do not agree to these terms, please do not use our services.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                2. Description of Service
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                Aetherra is an AI-native operating system and development platform that enables the creation
                                of conscious AI systems. Our service includes various tools, APIs, and community features.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                3. User Responsibilities
                            </h2>
                            <ul className="list-disc pl-6 space-y-2 text-zinc-300 mb-6">
                                <li>Use the platform responsibly and ethically</li>
                                <li>Respect intellectual property rights</li>
                                <li>Follow community guidelines</li>
                                <li>Report security vulnerabilities responsibly</li>
                            </ul>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                4. Open Source License
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                Aetherra is released under an open source license. Contributions to the project are welcome
                                and subject to the project's contribution guidelines.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                5. Privacy and Data
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                We respect your privacy and handle data in accordance with our Privacy Policy.
                                We collect only necessary information to provide our services.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                6. Disclaimers
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                Aetherra is provided "as is" without warranties of any kind. We are not responsible
                                for any damages arising from the use of our platform.
                            </p>

                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">
                                7. Contact Information
                            </h2>
                            <p className="text-zinc-300 mb-6">
                                For questions about these Terms and Conditions, please contact us through our
                                <a href="https://discord.gg/9Xw28xgEQ3" className="text-aetherra-green hover:underline ml-1" target="_blank" rel="noopener noreferrer">
                                    Discord community
                                </a> or
                                <a href="https://github.com/Zyonic88/Aetherra" className="text-aetherra-green hover:underline ml-1" target="_blank" rel="noopener noreferrer">
                                    GitHub repository
                                </a>.
                            </p>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
