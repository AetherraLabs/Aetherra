import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface Plugin {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  category: string;
  tags: string[];
  rating: number;
  downloads: number;
  lastUpdated: Date;
  featured: boolean;
  verified: boolean;
  size: string;
  compatibility: string[];
  documentation: string;
  repository?: string;
  license: string;
  screenshots: string[];
  dependencies: string[];
}

interface AetherHubGalleryProps {
  onInstallPlugin?: (plugin: Plugin) => void;
  onViewDetails?: (plugin: Plugin) => void;
}

export default function AetherHubGallery({ onInstallPlugin, onViewDetails }: AetherHubGalleryProps) {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [filteredPlugins, setFilteredPlugins] = useState<Plugin[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'downloads' | 'updated'>('rating');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);

  useEffect(() => {
    // Initialize with sample plugin data
    initializeSamplePlugins();
  }, []);

  useEffect(() => {
    // Filter and sort plugins when criteria change
    filterAndSortPlugins();
  }, [plugins, searchQuery, selectedCategory, selectedTag, sortBy]);

  const initializeSamplePlugins = () => {
    const samplePlugins: Plugin[] = [
      {
        id: 'neural_optimizer',
        name: 'Neural Optimizer Pro',
        description: 'Advanced neural network optimization with real-time performance tuning and memory management.',
        author: 'Lyrixa Research',
        version: '2.1.0',
        category: 'Performance',
        tags: ['optimization', 'neural', 'performance', 'memory'],
        rating: 4.9,
        downloads: 45,
        lastUpdated: new Date(Date.now() - 86400000 * 2), // 2 days ago
        featured: true,
        verified: true,
        size: '2.4 MB',
        compatibility: ['Lyrixa 2.0+', 'AetherOS 1.5+'],
        documentation: 'https://docs.aetherra.ai/plugins/neural-optimizer',
        repository: 'https://github.com/aetherra/neural-optimizer',
        license: 'MIT',
        screenshots: ['/screenshots/neural-optimizer-1.png', '/screenshots/neural-optimizer-2.png'],
        dependencies: ['core_runtime', 'memory_manager']
      },
      {
        id: 'visual_synth',
        name: 'Visual Synthesizer',
        description: 'Create stunning visual representations of neural network operations and data flows.',
        author: 'CognitiveArts',
        version: '1.3.2',
        category: 'Visualization',
        tags: ['visualization', 'graphics', 'neural', 'ui'],
        rating: 4.7,
        downloads: 23,
        lastUpdated: new Date(Date.now() - 86400000 * 5), // 5 days ago
        featured: true,
        verified: true,
        size: '5.1 MB',
        compatibility: ['Lyrixa 1.8+', 'AetherOS 1.4+'],
        documentation: 'https://docs.aetherra.ai/plugins/visual-synthesizer',
        license: 'GPL-3.0',
        screenshots: ['/screenshots/visual-synth-1.png'],
        dependencies: ['graphics_engine', 'data_processor']
      },
      {
        id: 'quantum_bridge',
        name: 'Quantum Bridge',
        description: 'Experimental quantum computing interface for hybrid classical-quantum neural networks.',
        author: 'QuantumMind Labs',
        version: '0.9.1',
        category: 'Research',
        tags: ['quantum', 'experimental', 'research', 'hybrid'],
        rating: 4.2,
        downloads: 12,
        lastUpdated: new Date(Date.now() - 86400000 * 1), // 1 day ago
        featured: false,
        verified: false,
        size: '12.8 MB',
        compatibility: ['Lyrixa 2.1+', 'Quantum SDK 1.0+'],
        documentation: 'https://quantummind.dev/quantum-bridge',
        repository: 'https://github.com/quantummind/quantum-bridge',
        license: 'Apache-2.0',
        screenshots: ['/screenshots/quantum-bridge-1.png', '/screenshots/quantum-bridge-2.png'],
        dependencies: ['quantum_sdk', 'bridge_runtime']
      },
      {
        id: 'emotion_engine',
        name: 'Emotion Engine',
        description: 'Advanced emotional intelligence and sentiment analysis for more human-like AI interactions.',
        author: 'EmpathAI',
        version: '3.0.0',
        category: 'AI Enhancement',
        tags: ['emotion', 'sentiment', 'ai', 'nlp'],
        rating: 4.8,
        downloads: 31,
        lastUpdated: new Date(Date.now() - 86400000 * 3), // 3 days ago
        featured: true,
        verified: true,
        size: '8.2 MB',
        compatibility: ['Lyrixa 2.0+', 'NLP Engine 2.5+'],
        documentation: 'https://docs.aetherra.ai/plugins/emotion-engine',
        license: 'MIT',
        screenshots: ['/screenshots/emotion-engine-1.png'],
        dependencies: ['nlp_engine', 'sentiment_analyzer']
      },
      {
        id: 'data_flows',
        name: 'Neural Data Flows',
        description: 'Visualize and optimize data pipelines through neural network architectures.',
        author: 'DataViz Studio',
        version: '1.5.7',
        category: 'Development',
        tags: ['data', 'pipeline', 'visualization', 'debug'],
        rating: 4.5,
        downloads: 18,
        lastUpdated: new Date(Date.now() - 86400000 * 7), // 1 week ago
        featured: false,
        verified: true,
        size: '3.7 MB',
        compatibility: ['Lyrixa 1.9+'],
        documentation: 'https://dataviz.studio/neural-data-flows',
        license: 'BSD-3-Clause',
        screenshots: ['/screenshots/data-flows-1.png', '/screenshots/data-flows-2.png'],
        dependencies: ['data_processor', 'visualization_engine']
      },
      {
        id: 'security_shield',
        name: 'Neural Security Shield',
        description: 'Comprehensive security monitoring and threat detection for neural systems.',
        author: 'SecureAI Corp',
        version: '2.2.3',
        category: 'Security',
        tags: ['security', 'monitoring', 'threat-detection', 'protection'],
        rating: 4.6,
        downloads: 26,
        lastUpdated: new Date(Date.now() - 86400000 * 4), // 4 days ago
        featured: false,
        verified: true,
        size: '4.9 MB',
        compatibility: ['Lyrixa 2.0+', 'Security Framework 1.3+'],
        documentation: 'https://docs.aetherra.ai/plugins/security-shield',
        repository: 'https://github.com/secureai/neural-security-shield',
        license: 'MIT',
        screenshots: ['/screenshots/security-shield-1.png'],
        dependencies: ['security_framework', 'threat_analyzer']
      }
    ];
    
    setPlugins(samplePlugins);
  };

  const filterAndSortPlugins = () => {
    let filtered = [...plugins];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(plugin => plugin.category === selectedCategory);
    }

    // Apply tag filter
    if (selectedTag !== 'all') {
      filtered = filtered.filter(plugin => plugin.tags.includes(selectedTag));
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'rating':
          return b.rating - a.rating;
        case 'downloads':
          return b.downloads - a.downloads;
        case 'updated':
          return b.lastUpdated.getTime() - a.lastUpdated.getTime();
        default:
          return 0;
      }
    });

    setFilteredPlugins(filtered);
  };

  const getCategories = () => {
    const categories = [...new Set(plugins.map(p => p.category))];
    return ['all', ...categories];
  };

  const getAllTags = () => {
    const tags = [...new Set(plugins.flatMap(p => p.tags))];
    return ['all', ...tags];
  };

  const formatLastUpdated = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const handleInstall = (plugin: Plugin) => {
    onInstallPlugin?.(plugin);
    // Show installation feedback
    alert(`Installing ${plugin.name}...`);
  };

  const handleViewDetails = (plugin: Plugin) => {
    setSelectedPlugin(plugin);
    onViewDetails?.(plugin);
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">★</span>);
    }
    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-600">★</span>);
    }
    return stars;
  };

  const PluginCard = ({ plugin }: { plugin: Plugin }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-aetherra-green transition-all duration-300"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="font-semibold text-white text-lg">{plugin.name}</h3>
            {plugin.verified && (
              <span className="text-aetherra-green text-sm" title="Verified Plugin">✅</span>
            )}
            {plugin.featured && (
              <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded">Featured</span>
            )}
          </div>
          <p className="text-sm text-gray-400 mb-2">by {plugin.author}</p>
        </div>
        <span className="text-xs text-gray-500">{plugin.version}</span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 mb-3 line-clamp-2">{plugin.description}</p>

      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-3">
        {plugin.tags.slice(0, 3).map((tag, index) => (
          <span
            key={index}
            className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded"
          >
            {tag}
          </span>
        ))}
        {plugin.tags.length > 3 && (
          <span className="text-xs text-gray-500">+{plugin.tags.length - 3}</span>
        )}
      </div>

      {/* Rating and Stats */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-1">
          {renderStars(plugin.rating)}
          <span className="text-sm text-gray-400 ml-1">({plugin.rating})</span>
        </div>
        <div className="text-xs text-gray-500">
          {plugin.downloads.toLocaleString()} downloads
        </div>
      </div>

      {/* Metadata */}
      <div className="text-xs text-gray-500 mb-3 space-y-1">
        <div>Size: {plugin.size}</div>
        <div>Updated: {formatLastUpdated(plugin.lastUpdated)}</div>
        <div>Category: {plugin.category}</div>
      </div>

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => handleInstall(plugin)}
          className="flex-1 bg-aetherra-green text-black py-2 px-3 rounded font-medium hover:bg-green-400 transition-colors text-sm"
        >
          📦 Install
        </button>
        <button
          onClick={() => handleViewDetails(plugin)}
          className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm"
        >
          👁️ Details
        </button>
      </div>
    </motion.div>
  );

  const PluginListItem = ({ plugin }: { plugin: Plugin }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-aetherra-green transition-colors"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="font-semibold text-white">{plugin.name}</h3>
            {plugin.verified && <span className="text-aetherra-green">✅</span>}
            {plugin.featured && (
              <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded">Featured</span>
            )}
            <span className="text-xs text-gray-500">{plugin.version}</span>
          </div>
          <p className="text-sm text-gray-300 mb-2">{plugin.description}</p>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>by {plugin.author}</span>
            <span>{plugin.downloads.toLocaleString()} downloads</span>
            <span>{plugin.category}</span>
            <span>{formatLastUpdated(plugin.lastUpdated)}</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center">
            {renderStars(plugin.rating)}
            <span className="text-sm text-gray-400 ml-1">({plugin.rating})</span>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handleInstall(plugin)}
              className="bg-aetherra-green text-black py-1 px-3 rounded font-medium hover:bg-green-400 transition-colors text-sm"
            >
              Install
            </button>
            <button
              onClick={() => handleViewDetails(plugin)}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm"
            >
              Details
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header and Controls */}
      <div className="p-4 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-aetherra-green">🔌 AetherHub Plugin Gallery</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-aetherra-green text-black' : 'bg-gray-700 hover:bg-gray-600'}`}
            >
              ⊞
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-aetherra-green text-black' : 'bg-gray-700 hover:bg-gray-600'}`}
            >
              ☰
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            placeholder="Search plugins..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-aetherra-green"
          />
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          >
            {getCategories().map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>

          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          >
            {getAllTags().map(tag => (
              <option key={tag} value={tag}>
                {tag === 'all' ? 'All Tags' : tag}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-aetherra-green"
          >
            <option value="rating">Sort by Rating</option>
            <option value="downloads">Sort by Downloads</option>
            <option value="name">Sort by Name</option>
            <option value="updated">Sort by Updated</option>
          </select>
        </div>

        <div className="mt-3 text-sm text-gray-400">
          {filteredPlugins.length} of {plugins.length} plugins
        </div>
      </div>

      {/* Plugin Grid/List */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredPlugins.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-white mb-2">No plugins found</h3>
            <p className="text-gray-400">Try adjusting your search criteria</p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPlugins.map(plugin => (
              <PluginCard key={plugin.id} plugin={plugin} />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredPlugins.map(plugin => (
              <PluginListItem key={plugin.id} plugin={plugin} />
            ))}
          </div>
        )}
      </div>

      {/* Plugin Detail Modal */}
      {selectedPlugin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white">{selectedPlugin.name}</h2>
              <button
                onClick={() => setSelectedPlugin(null)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-white mb-2">Description</h3>
                <p className="text-gray-300">{selectedPlugin.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-white mb-1">Author</h4>
                  <p className="text-gray-300">{selectedPlugin.author}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Version</h4>
                  <p className="text-gray-300">{selectedPlugin.version}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Category</h4>
                  <p className="text-gray-300">{selectedPlugin.category}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Size</h4>
                  <p className="text-gray-300">{selectedPlugin.size}</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-2">Compatibility</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedPlugin.compatibility.map((comp, index) => (
                    <span key={index} className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                      {comp}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-2">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedPlugin.tags.map((tag, index) => (
                    <span key={index} className="bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => handleInstall(selectedPlugin)}
                  className="flex-1 bg-aetherra-green text-black py-2 px-4 rounded font-medium hover:bg-green-400 transition-colors"
                >
                  📦 Install Plugin
                </button>
                {selectedPlugin.repository && (
                  <button
                    onClick={() => window.open(selectedPlugin.repository, '_blank')}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                  >
                    📂 Repository
                  </button>
                )}
                {selectedPlugin.documentation && (
                  <button
                    onClick={() => window.open(selectedPlugin.documentation, '_blank')}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition-colors"
                  >
                    📖 Docs
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
