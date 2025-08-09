import { motion } from 'framer-motion'

function Home() {
    return (
        <div className="page-section">
            <div className="container text-center">
                <motion.h1
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="text-6xl font-bold gradient-text mb-6"
                >
                    Welcome to Aetherra
                </motion.h1>
                <motion.p
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto"
                >
                    An operating system that thinks. A companion that learns.
                    The future of neural computing is here.
                </motion.p>
                <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="space-x-4"
                >
                    <button className="btn-primary">Get Started</button>
                    <button className="border border-aetherra-green text-aetherra-green px-6 py-3 rounded hover:bg-aetherra-green hover:text-black transition-colors">
                        Learn More
                    </button>
                </motion.div>
            </div>
        </div>
    )
}

export default Home
