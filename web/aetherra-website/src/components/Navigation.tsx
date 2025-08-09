import { Link, useLocation } from 'react-router-dom';

export default function Navigation() {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/lyrixa', label: 'Lyrixa Demo', icon: '🤖' },
        { path: '/aetherhub', label: 'AetherHub', icon: '⚡' },
        { path: '/playground', label: 'Playground', icon: '🛝' },
        { path: '/console', label: 'Console', icon: '🖥️' },
        { path: '/lab', label: 'Script Lab', icon: '⚗️' },
        { path: '/docs', label: 'Docs', icon: '📚' },
        { path: '/introspection', label: 'Introspection', icon: '🧠' },
        { path: '/developer', label: 'Dev Console', icon: '💻' },
        { path: '/contribute', label: 'Contribute', icon: '🛠️' },
        { path: '/community', label: 'Community', icon: '🌟' },
    ];

    return (
        <nav className="bg-gray-900 border-b border-gray-700 p-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <Link to="/" className="text-2xl font-bold text-blue-400">
                    Aetherra
                </Link>

                <div className="flex space-x-1">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`px-4 py-2 rounded-lg transition-colors ${location.pathname === item.path
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                                }`}
                        >
                            <span className="mr-2">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}
                </div>
            </div>
        </nav>
    );
}
