import { motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import { AetherHubGallery } from '../components/AetherHubGallery';
import PluginCard from '../components/PluginCard';
import PluginSearch from '../components/PluginSearch';
import pluginData from '../data/plugin_metadata.json';
import { Plugin } from '../types';

export default function AetherHub() {
    const [activeView, setActiveView] = useState<'gallery' | 'classic'>('gallery');
    const [searchQuery, setSearchQuery] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');

    const filteredPlugins = useMemo(() => {
        return (pluginData.plugins as Plugin[]).filter((plugin) => {
            const matchesSearch = !searchQuery ||
                plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                plugin.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

            const matchesCategory = !categoryFilter || plugin.category === categoryFilter;
            const matchesStatus = !statusFilter || plugin.status === statusFilter;

            return matchesSearch && matchesCategory && matchesStatus;
        });
    }, [searchQuery, categoryFilter, statusFilter]);

    return (
        <div className="p-6 space-y-6">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4">⚡ AetherHub Marketplace</h1>
                <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                    Discover and install plugins to extend Lyrixa's capabilities. Built by the community, for the community.
                </p>
            </div>

            {/* View Toggle */}
            <div className="flex justify-center mb-8">
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-2 flex">
                    <button
                        onClick={() => setActiveView('gallery')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${activeView === 'gallery'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-300 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        🎨 Gallery View
                    </button>
                    <button
                        onClick={() => setActiveView('classic')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${activeView === 'classic'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-300 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        📋 Classic View
                    </button>
                </div>
            </div>

            {/* View Content */}
            <motion.div
                key={activeView}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
            >
                {activeView === 'gallery' ? (
                    <AetherHubGallery />
                ) : (
                    <>
                        <PluginSearch
                            onSearch={setSearchQuery}
                            onCategoryFilter={setCategoryFilter}
                            onStatusFilter={setStatusFilter}
                        />

                        <div className="flex justify-between items-center">
                            <h2 className="text-2xl font-semibold">
                                Available Plugins ({filteredPlugins.length})
                            </h2>
                            <div className="flex gap-2 text-sm text-gray-400">
                                <span>Sort by:</span>
                                <button className="text-blue-400 hover:text-blue-300">Downloads</button>
                                <span>•</span>
                                <button className="text-blue-400 hover:text-blue-300">Rating</button>
                                <span>•</span>
                                <button className="text-blue-400 hover:text-blue-300">Recent</button>
                            </div>
                        </div>

                        {filteredPlugins.length === 0 ? (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">🔍</div>
                                <h3 className="text-xl font-semibold mb-2">No plugins found</h3>
                                <p className="text-gray-400">Try adjusting your search filters</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {filteredPlugins.map((plugin) => (
                                    <PluginCard key={plugin.id} plugin={plugin} />
                                ))}
                            </div>
                        )}

                        <div className="bg-gray-800 p-6 rounded-xl shadow-lg mt-8">
                            <h3 className="text-xl font-semibold mb-4">📦 Want to publish your own plugin?</h3>
                            <p className="text-gray-300 mb-4">
                                Share your innovations with the Aetherra community. Our plugin system makes it easy to extend Lyrixa's capabilities.
                            </p>
                            <div className="flex gap-4">
                                <a
                                    href="/contribute"
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded transition-colors"
                                >
                                    Learn How to Contribute
                                </a>
                                <a
                                    href="https://github.com/AetherraLabs/Aetherra/wiki/Plugin-Development"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded transition-colors"
                                >
                                    Plugin Development Guide
                                </a>
                            </div>
                        </div>
                    </>
                )}
            </motion.div>
        </div>
    );
}
