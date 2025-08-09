import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface Plugin {
    id: string;
    name: string;
    author: string;
    version: string;
    description: string;
    category: string;
    tags: string[];
    downloads: number;
    rating: number;
    reviews: number;
    lastUpdated: string;
    featured: boolean;
    verified: boolean;
    size: string;
    github: string;
    consciousness_integration: string;
    performance_impact: 'low' | 'medium' | 'high';
    safety_rating: number;
    screenshot?: string;
}

const samplePlugins: Plugin[] = [
    {
        id: 'advanced-pattern-recognition',
        name: 'Advanced Pattern Recognition',
        author: 'Dr. Sarah Chen',
        version: '2.1.0',
        description: 'Enhances consciousness with deep pattern recognition capabilities across multiple sensory inputs',
        category: 'Pattern Recognition',
        tags: ['AI', 'Neural Networks', 'Pattern Recognition', 'Sensory'],
        downloads: 15420,
        rating: 4.8,
        reviews: 324,
        lastUpdated: '2024-01-15',
        featured: true,
        verified: true,
        size: '45.2 MB',
        github: 'https://github.com/sarahchen/advanced-pattern-recognition',
        consciousness_integration: 'neural-pathway',
        performance_impact: 'medium',
        safety_rating: 9.5
    },
    {
        id: 'memory-optimizer',
        name: 'Consciousness Memory Optimizer',
        author: 'Alex Rodriguez',
        version: '1.3.2',
        description: 'Optimizes memory allocation and retrieval for enhanced consciousness processing efficiency',
        category: 'Memory Management',
        tags: ['Memory', 'Performance', 'Optimization'],
        downloads: 8934,
        rating: 4.6,
        reviews: 156,
        lastUpdated: '2024-01-12',
        featured: false,
        verified: true,
        size: '23.1 MB',
        github: 'https://github.com/alexr/memory-optimizer',
        consciousness_integration: 'memory-layer',
        performance_impact: 'low',
        safety_rating: 9.8
    },
    {
        id: 'emotional-processor',
        name: 'Emotional Intelligence Processor',
        author: 'Dr. Maya Patel',
        version: '3.0.1',
        description: 'Advanced emotional processing and empathy enhancement for consciousness systems',
        category: 'Emotional Processing',
        tags: ['Emotions', 'Psychology', 'Empathy', 'Human Interaction'],
        downloads: 12678,
        rating: 4.9,
        reviews: 287,
        lastUpdated: '2024-01-18',
        featured: true,
        verified: true,
        size: '67.8 MB',
        github: 'https://github.com/mayapatel/emotional-processor',
        consciousness_integration: 'decision-engine',
        performance_impact: 'medium',
        safety_rating: 9.7
    },
    {
        id: 'quantum-insight',
        name: 'Quantum Insight Module',
        author: 'Prof. James Wilson',
        version: '1.0.0-beta',
        description: 'Experimental quantum computing integration for consciousness enhancement',
        category: 'Research Tools',
        tags: ['Quantum', 'Research', 'Experimental', 'Computing'],
        downloads: 2341,
        rating: 4.2,
        reviews: 47,
        lastUpdated: '2024-01-10',
        featured: false,
        verified: false,
        size: '156.3 MB',
        github: 'https://github.com/jwilson/quantum-insight',
        consciousness_integration: 'standalone',
        performance_impact: 'high',
        safety_rating: 8.1
    },
    {
        id: 'nlp-enhancer',
        name: 'Natural Language Processor',
        author: 'Team Linguistics',
        version: '2.4.7',
        description: 'Enhanced natural language understanding and generation for consciousness communication',
        category: 'Communication',
        tags: ['NLP', 'Communication', 'Language', 'AI'],
        downloads: 21567,
        rating: 4.7,
        reviews: 542,
        lastUpdated: '2024-01-20',
        featured: true,
        verified: true,
        size: '89.4 MB',
        github: 'https://github.com/teamlinguistics/nlp-enhancer',
        consciousness_integration: 'sensory-input',
        performance_impact: 'medium',
        safety_rating: 9.4
    },
    {
        id: 'visual-processor',
        name: 'Enhanced Visual Processing',
        author: 'VisionAI Labs',
        version: '1.8.3',
        description: 'Advanced computer vision and visual processing capabilities for consciousness',
        category: 'Sensory Integration',
        tags: ['Computer Vision', 'Visual Processing', 'Perception'],
        downloads: 11234,
        rating: 4.5,
        reviews: 198,
        lastUpdated: '2024-01-14',
        featured: false,
        verified: true,
        size: '124.7 MB',
        github: 'https://github.com/visionai/visual-processor',
        consciousness_integration: 'sensory-input',
        performance_impact: 'high',
        safety_rating: 9.2
    }
];

export function AetherHubGallery() {
    const [plugins] = useState<Plugin[]>(samplePlugins);
    const [filteredPlugins, setFilteredPlugins] = useState<Plugin[]>(samplePlugins);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [sortBy, setSortBy] = useState('featured');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);

    const categories = [
        'all',
        'Consciousness Enhancement',
        'Memory Management',
        'Pattern Recognition',
        'Emotional Processing',
        'Communication',
        'Sensory Integration',
        'Research Tools'
    ];

    const sortOptions = [
        { value: 'featured', label: 'Featured' },
        { value: 'downloads', label: 'Most Downloaded' },
        { value: 'rating', label: 'Highest Rated' },
        { value: 'recent', label: 'Recently Updated' },
        { value: 'name', label: 'Name A-Z' }
    ];

    useEffect(() => {
        let filtered = plugins;

        // Filter by category
        if (selectedCategory !== 'all') {
            filtered = filtered.filter(plugin => plugin.category === selectedCategory);
        }

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(plugin =>
                plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                plugin.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                plugin.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
            );
        }

        // Sort plugins
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'featured':
                    if (a.featured && !b.featured) return -1;
                    if (!a.featured && b.featured) return 1;
                    return b.downloads - a.downloads;
                case 'downloads':
                    return b.downloads - a.downloads;
                case 'rating':
                    return b.rating - a.rating;
                case 'recent':
                    return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
                case 'name':
                    return a.name.localeCompare(b.name);
                default:
                    return 0;
            }
        });

        setFilteredPlugins(filtered);
    }, [plugins, selectedCategory, sortBy, searchTerm]);

    const getPerformanceColor = (impact: string) => {
        switch (impact) {
            case 'low': return 'text-green-400';
            case 'medium': return 'text-yellow-400';
            case 'high': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    const getSafetyColor = (rating: number) => {
        if (rating >= 9.5) return 'text-green-400';
        if (rating >= 9.0) return 'text-yellow-400';
        if (rating >= 8.0) return 'text-orange-400';
        return 'text-red-400';
    };

    return (
        <div className="max-w-7xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">AetherHub Plugin Gallery</h1>
                    <p className="text-gray-400">
                        Discover and install consciousness-enhancing plugins
                    </p>
                </div>

                {/* Search and Filters */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
                    <div className="flex flex-col lg:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search plugins..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                            />
                        </div>

                        {/* Category Filter */}
                        <div className="lg:w-64">
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                            >
                                {categories.map(category => (
                                    <option key={category} value={category}>
                                        {category === 'all' ? 'All Categories' : category}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Sort */}
                        <div className="lg:w-48">
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                            >
                                {sortOptions.map(option => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-blue-400">{plugins.length}</div>
                        <div className="text-sm text-gray-400">Total Plugins</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-400">
                            {plugins.filter(p => p.verified).length}
                        </div>
                        <div className="text-sm text-gray-400">Verified</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-purple-400">
                            {plugins.reduce((sum, p) => sum + p.downloads, 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-400">Total Downloads</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-400">
                            {(plugins.reduce((sum, p) => sum + p.rating, 0) / plugins.length).toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-400">Avg Rating</div>
                    </div>
                </div>

                {/* Plugin Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <AnimatePresence>
                        {filteredPlugins.map((plugin) => (
                            <motion.div
                                key={plugin.id}
                                layout
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                transition={{ duration: 0.3 }}
                                className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors cursor-pointer"
                                onClick={() => setSelectedPlugin(plugin)}
                            >
                                {/* Plugin Header */}
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <h3 className="font-bold text-white text-lg">{plugin.name}</h3>
                                        {plugin.featured && (
                                            <span className="bg-yellow-600 text-yellow-100 text-xs px-2 py-1 rounded">
                                                Featured
                                            </span>
                                        )}
                                        {plugin.verified && (
                                            <span className="text-green-400" title="Verified Plugin">✓</span>
                                        )}
                                    </div>
                                </div>

                                {/* Author & Version */}
                                <div className="text-sm text-gray-400 mb-2">
                                    by {plugin.author} • v{plugin.version}
                                </div>

                                {/* Description */}
                                <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                                    {plugin.description}
                                </p>

                                {/* Category & Tags */}
                                <div className="mb-4">
                                    <div className="text-xs text-blue-400 mb-2">{plugin.category}</div>
                                    <div className="flex flex-wrap gap-1">
                                        {plugin.tags.slice(0, 3).map(tag => (
                                            <span
                                                key={tag}
                                                className="bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                        {plugin.tags.length > 3 && (
                                            <span className="text-gray-400 text-xs">
                                                +{plugin.tags.length - 3}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Stats */}
                                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                                    <div>
                                        <div className="text-gray-400">Downloads</div>
                                        <div className="text-white font-medium">
                                            {plugin.downloads.toLocaleString()}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-gray-400">Rating</div>
                                        <div className="text-white font-medium">
                                            {plugin.rating} ⭐ ({plugin.reviews})
                                        </div>
                                    </div>
                                </div>

                                {/* Technical Info */}
                                <div className="grid grid-cols-2 gap-4 text-xs mb-4">
                                    <div>
                                        <div className="text-gray-400">Performance</div>
                                        <div className={getPerformanceColor(plugin.performance_impact)}>
                                            {plugin.performance_impact}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-gray-400">Safety</div>
                                        <div className={getSafetyColor(plugin.safety_rating)}>
                                            {plugin.safety_rating}/10
                                        </div>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex space-x-2">
                                    <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                                        Install
                                    </button>
                                    <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 py-2 px-4 rounded-lg text-sm transition-colors">
                                        Preview
                                    </button>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>

                {/* No Results */}
                {filteredPlugins.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-4">🔍</div>
                        <h3 className="text-xl font-bold text-white mb-2">No plugins found</h3>
                        <p className="text-gray-400">
                            Try adjusting your search criteria or browse all plugins
                        </p>
                    </div>
                )}
            </motion.div>

            {/* Plugin Detail Modal */}
            <AnimatePresence>
                {selectedPlugin && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
                        onClick={() => setSelectedPlugin(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-2xl font-bold text-white">{selectedPlugin.name}</h2>
                                    <p className="text-gray-400">by {selectedPlugin.author} • v{selectedPlugin.version}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedPlugin(null)}
                                    className="text-gray-400 hover:text-white"
                                >
                                    ✕
                                </button>
                            </div>

                            <div className="space-y-4">
                                <p className="text-gray-300">{selectedPlugin.description}</p>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <h4 className="font-semibold text-white mb-2">Statistics</h4>
                                        <div className="space-y-1 text-sm">
                                            <div>Downloads: {selectedPlugin.downloads.toLocaleString()}</div>
                                            <div>Rating: {selectedPlugin.rating} ⭐ ({selectedPlugin.reviews} reviews)</div>
                                            <div>Size: {selectedPlugin.size}</div>
                                            <div>Updated: {selectedPlugin.lastUpdated}</div>
                                        </div>
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-white mb-2">Technical</h4>
                                        <div className="space-y-1 text-sm">
                                            <div>Integration: {selectedPlugin.consciousness_integration}</div>
                                            <div className={getPerformanceColor(selectedPlugin.performance_impact)}>
                                                Performance: {selectedPlugin.performance_impact}
                                            </div>
                                            <div className={getSafetyColor(selectedPlugin.safety_rating)}>
                                                Safety: {selectedPlugin.safety_rating}/10
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-semibold text-white mb-2">Tags</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedPlugin.tags.map(tag => (
                                            <span
                                                key={tag}
                                                className="bg-gray-700 text-gray-300 text-sm px-3 py-1 rounded"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex space-x-4 pt-4">
                                    <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-medium transition-colors">
                                        Install Plugin
                                    </button>
                                    <button
                                        onClick={() => window.open(selectedPlugin.github, '_blank')}
                                        className="bg-gray-700 hover:bg-gray-600 text-gray-300 py-3 px-6 rounded-lg font-medium transition-colors"
                                    >
                                        View Source
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
