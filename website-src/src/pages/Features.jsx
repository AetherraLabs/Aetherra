import { motion } from 'framer-motion'

function Features() {
    const features = [
        {
            title: "Neural Runtime",
            description: "AI-powered execution environment that optimizes in real-time",
            icon: "🧠"
        },
        {
            title: "Predictive Interface",
            description: "UI that anticipates your needs before you know them",
            icon: "🔮"
        },
        {
            title: "Adaptive Memory",
            description: "Learning system that grows with your usage patterns",
            icon: "💾"
        },
        {
            title: "Plugin Ecosystem",
            description: "Extensible architecture for unlimited customization",
            icon: "🔌"
        }
    ]

    return (
        <div className="page-section">
            <div className="container">
                <motion.h1
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl font-bold gradient-text mb-12 text-center"
                >
                    Features
                </motion.h1>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-gray-800 p-6 rounded-lg border border-gray-700 hover:border-aetherra-green transition-colors"
                        >
                            <div className="text-4xl mb-4">{feature.icon}</div>
                            <h3 className="text-xl font-semibold text-aetherra-green mb-3">
                                {feature.title}
                            </h3>
                            <p className="text-gray-300">{feature.description}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Features
