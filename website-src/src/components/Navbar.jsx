import { motion } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'

function Navbar() {
    const location = useLocation()

    const isActive = (path) => location.pathname === path

    return (
        <motion.nav
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed top-0 w-full bg-black/80 backdrop-blur-sm border-b border-gray-800 z-50"
        >
            <div className="container mx-auto px-4 py-3">
                <div className="flex items-center justify-between">
                    <Link to="/" className="text-xl font-bold gradient-text">
                        Aetherra
                    </Link>
                    <div className="flex space-x-6">
                        {[
                            { path: '/', label: 'Home' },
                            { path: '/lyrixa', label: 'Lyrixa' },
                            { path: '/playground', label: 'Playground' },
                            { path: '/introspection', label: 'Live Introspection' },
                            { path: '/features', label: 'Features' },
                            { path: '/community', label: 'Community' }
                        ].map(({ path, label }) => (
                            <Link
                                key={path}
                                to={path}
                                className={`transition-colors ${isActive(path)
                                        ? 'text-aetherra-green'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                {label}
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </motion.nav>
    )
}

export default Navbar
