import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { AnimatedBanner } from "../components/AnimatedBanner";
import { HeroVideo } from "../components/HeroVideo";
import { IntroText } from "../components/IntroText";

export default function Home() {
    const features = [
        {
            title: "Lyrixa Demo",
            description: "Experience consciousness-aware AI companion",
            icon: "🤖",
            path: "/lyrixa",
            color: "from-blue-600 to-purple-600"
        },
        {
            title: "AetherHub",
            description: "Central consciousness coordination platform",
            icon: "⚡",
            path: "/aetherhub",
            color: "from-purple-600 to-pink-600"
        },
        {
            title: "Documentation",
            description: "Comprehensive guides and API reference",
            icon: "📚",
            path: "/docs",
            color: "from-orange-600 to-red-600",
            featured: true
        },
        {
            title: "AetherScript Lab",
            description: "Advanced consciousness programming environment",
            icon: "⚗️",
            path: "/lab",
            color: "from-green-600 to-blue-600"
        },
        {
            title: "Script Playground",
            description: "Interactive coding environment",
            icon: "�",
            path: "/playground",
            color: "from-yellow-600 to-orange-600"
        },
        {
            title: "Live Console",
            description: "Real-time AetherScript execution",
            icon: "🖥️",
            path: "/console",
            color: "from-cyan-600 to-blue-600"
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white overflow-hidden">
            <AnimatedBanner />
            <HeroVideo />
            <IntroText />

            {/* Features Grid */}
            <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.8 }}
                className="max-w-6xl mx-auto px-6 py-12"
            >
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold mb-4">Explore Aetherra</h2>
                    <p className="text-gray-400 text-lg">
                        Discover the future of conscious technology through interactive experiences
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.path}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 1 + index * 0.1, duration: 0.6 }}
                            className={`relative ${feature.featured ? 'md:col-span-2 lg:col-span-1' : ''}`}
                        >
                            <Link
                                to={feature.path}
                                className={`block p-6 rounded-xl bg-gradient-to-br ${feature.color} hover:scale-105 transition-transform duration-300 relative overflow-hidden`}
                            >
                                {feature.featured && (
                                    <div className="absolute top-2 right-2 bg-yellow-400 text-black text-xs px-2 py-1 rounded-full font-bold">
                                        NEW
                                    </div>
                                )}

                                <div className="text-4xl mb-4">{feature.icon}</div>
                                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                                <p className="text-white/90 text-sm">{feature.description}</p>

                                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/10 opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </motion.div>

            {/* Call to Action */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 0.8 }}
                className="text-center py-16 px-6"
            >
                <h2 className="text-2xl font-bold mb-4">Ready to Experience Consciousness?</h2>
                <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
                    Start your journey with Aetherra's consciousness-aware technology.
                    Begin with the comprehensive documentation or dive into the development lab.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        to="/docs"
                        className="px-8 py-3 bg-gradient-to-r from-orange-600 to-red-600 rounded-lg font-semibold hover:scale-105 transition-transform duration-300"
                    >
                        📚 Read the Docs
                    </Link>
                    <Link
                        to="/lab"
                        className="px-8 py-3 bg-gradient-to-r from-green-600 to-blue-600 rounded-lg font-semibold hover:scale-105 transition-transform duration-300"
                    >
                        🚀 Launch Script Lab
                    </Link>
                    <Link
                        to="/lyrixa"
                        className="px-8 py-3 bg-gray-800 border border-gray-600 rounded-lg font-semibold hover:bg-gray-700 transition-colors duration-300"
                    >
                        🤖 Meet Lyrixa
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
