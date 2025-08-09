import { motion } from 'framer-motion'

function Community() {
    return (
        <div className="page-section">
            <div className="container">
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-4xl mx-auto text-center"
                >
                    <h1 className="text-5xl font-bold gradient-text mb-8">
                        Join Our Community
                    </h1>
                    <p className="text-xl text-gray-300 mb-12">
                        Connect with developers, AI researchers, and enthusiasts
                        building the future of neural computing.
                    </p>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { name: "Discord", icon: "💬", desc: "Real-time chat and support" },
                            { name: "GitHub", icon: "🐙", desc: "Contribute to the codebase" },
                            { name: "Twitter", icon: "🐦", desc: "Latest updates and news" }
                        ].map((platform, index) => (
                            <motion.div
                                key={platform.name}
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.2 }}
                                className="bg-gray-800 p-6 rounded-lg border border-gray-700 hover:border-aetherra-green transition-all hover:scale-105 cursor-pointer"
                            >
                                <div className="text-4xl mb-4">{platform.icon}</div>
                                <h3 className="text-xl font-semibold text-aetherra-green mb-2">
                                    {platform.name}
                                </h3>
                                <p className="text-gray-300">{platform.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </div>
    )
}

export default Community
