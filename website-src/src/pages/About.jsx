import { motion } from 'framer-motion'

function About() {
    return (
        <div className="page-section">
            <div className="container">
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-4xl mx-auto"
                >
                    <h1 className="text-5xl font-bold gradient-text mb-8 text-center">
                        About Aetherra
                    </h1>
                    <div className="grid md:grid-cols-2 gap-8">
                        <div>
                            <h2 className="text-2xl font-semibold text-aetherra-green mb-4">
                                Our Vision
                            </h2>
                            <p className="text-gray-300 mb-6">
                                Aetherra represents the next evolution in computing - an AI-native
                                operating system that doesn't just run programs, but thinks alongside you.
                            </p>
                        </div>
                        <div>
                            <h2 className="text-2xl font-semibold text-aetherra-green mb-4">
                                The Technology
                            </h2>
                            <p className="text-gray-300 mb-6">
                                Built on cutting-edge neural architectures, Aetherra learns from
                                your patterns, anticipates your needs, and evolves with your workflow.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}

export default About
