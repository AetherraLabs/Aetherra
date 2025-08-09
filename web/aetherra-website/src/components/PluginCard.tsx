import { Plugin } from '../types';

interface PluginCardProps {
    plugin: Plugin;
}

export default function PluginCard({ plugin }: PluginCardProps) {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-600';
            case 'beta': return 'bg-yellow-600';
            case 'experimental': return 'bg-orange-600';
            default: return 'bg-gray-600';
        }
    };

    return (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-semibold text-white">{plugin.name}</h3>
                <span className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(plugin.status)}`}>
                    {plugin.status}
                </span>
            </div>

            <p className="text-gray-300 text-sm mb-4">{plugin.description}</p>

            <div className="flex items-center gap-4 mb-4 text-sm text-gray-400">
                <span>v{plugin.version}</span>
                <span>by {plugin.author}</span>
                <div className="flex items-center">
                    <span className="text-yellow-500">★</span>
                    <span className="ml-1">{plugin.rating}/5</span>
                </div>
            </div>

            <div className="flex flex-wrap gap-1 mb-4">
                {plugin.tags.map((tag) => (
                    <span key={tag} className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">
                        {tag}
                    </span>
                ))}
            </div>

            <div className="flex justify-between items-center text-sm text-gray-400">
                <span>{plugin.downloads} downloads</span>
                <span>Updated {new Date(plugin.last_updated).toLocaleDateString()}</span>
            </div>

            <button className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors">
                Install Plugin
            </button>
        </div>
    );
}
