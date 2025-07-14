import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import PluginCard from '../components/PluginCard';
import PluginSearch from '../components/PluginSearch';
import ContributionPanel from '../components/ContributionPanel';
import pluginData from '../data/plugin_metadata.json';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut"
    }
  }
};

type SortOption = 'popularity' | 'rating' | 'recent' | 'name';

export default function AetherHub() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>('popularity');

  // Extract unique categories and tags
  const availableCategories = useMemo(() => {
    return Array.from(new Set(pluginData.plugins.map(p => p.category)));
  }, []);

  const availableTags = useMemo(() => {
    const allTags = pluginData.plugins.flatMap(p => p.tags);
    return Array.from(new Set(allTags));
  }, []);

  // Filter and sort plugins
  const filteredPlugins = useMemo(() => {
    let filtered = pluginData.plugins.filter(plugin => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          plugin.name.toLowerCase().includes(query) ||
          plugin.description.toLowerCase().includes(query) ||
          plugin.author.toLowerCase().includes(query) ||
          plugin.tags.some(tag => tag.toLowerCase().includes(query));
        
        if (!matchesSearch) return false;
      }

      // Category filter
      if (selectedCategory && plugin.category !== selectedCategory) {
        return false;
      }

      // Tag filter
      if (selectedTag && !plugin.tags.includes(selectedTag)) {
        return false;
      }

      return true;
    });

    // Sort plugins
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popularity':
          return b.downloads - a.downloads;
        case 'rating':
          return b.rating - a.rating;
        case 'recent':
          return new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return filtered;
  }, [searchQuery, selectedCategory, selectedTag, sortBy]);

  const handleInstall = (pluginId: string) => {
    console.log('Installing plugin:', pluginId);
    // In a real app, this would trigger the installation process
  };

  const handlePreview = (pluginId: string) => {
    console.log('Previewing plugin:', pluginId);
    // In a real app, this would open a detailed view or demo
  };

  return (
    <div className="min-h-screen bg-aetherra-dark text-white">
      {/* Hero Header */}
      <motion.section 
        className="bg-gradient-to-br from-aetherra-dark via-aetherra-gray to-aetherra-dark border-b border-aetherra-green/20 py-16"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-6">
            AetherHub Marketplace
          </h1>
          <p className="text-xl text-zinc-300 mb-8 max-w-3xl mx-auto">
            Discover, install, and contribute to the growing ecosystem of AI-native plugins. 
            Enhance your Aetherra experience with community-driven innovations.
          </p>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
            <div>
              <div className="text-2xl font-bold text-aetherra-green">
                {pluginData.plugins.length}
              </div>
              <div className="text-sm text-zinc-400">Available Plugins</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">
                {pluginData.plugins.reduce((sum, p) => sum + p.downloads, 0).toLocaleString()}
              </div>
              <div className="text-sm text-zinc-400">Total Downloads</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">
                {availableCategories.length}
              </div>
              <div className="text-sm text-zinc-400">Categories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {Math.round(pluginData.plugins.reduce((sum, p) => sum + p.rating, 0) / pluginData.plugins.length * 10) / 10}
              </div>
              <div className="text-sm text-zinc-400">Avg Rating</div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Main Content */}
      <motion.main 
        className="max-w-7xl mx-auto px-6 py-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Search and Filters */}
        <motion.div variants={itemVariants}>
          <PluginSearch
            onSearch={setSearchQuery}
            onCategoryFilter={setSelectedCategory}
            onTagFilter={setSelectedTag}
            onSortChange={setSortBy}
            availableCategories={availableCategories}
            availableTags={availableTags}
            totalResults={filteredPlugins.length}
          />
        </motion.div>

        {/* Plugins Grid */}
        <motion.section variants={itemVariants} className="mb-16">
          {filteredPlugins.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
              {filteredPlugins.map((plugin) => (
                <PluginCard
                  key={plugin.id}
                  plugin={plugin}
                  onInstall={handleInstall}
                  onPreview={handlePreview}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-zinc-300 mb-2">
                No plugins found
              </h3>
              <p className="text-zinc-400">
                Try adjusting your search criteria or explore different categories.
              </p>
            </div>
          )}
        </motion.section>

        {/* Contribution Panel */}
        <motion.section variants={itemVariants}>
          <ContributionPanel />
        </motion.section>

        {/* Featured Categories */}
        <motion.section variants={itemVariants} className="mt-16">
          <h2 className="text-3xl font-bold gradient-text mb-8 text-center">
            Featured Categories
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {availableCategories.map((category) => {
              const categoryPlugins = pluginData.plugins.filter(p => p.category === category);
              const categoryIcons = {
                performance: '⚡',
                memory: '🧠',
                personality: '🎭',
                security: '🛡️',
                creativity: '🎨',
                development: '👨‍💻'
              };
              
              return (
                <motion.button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700 hover:border-aetherra-green/50 transition-all text-left"
                >
                  <div className="text-3xl mb-3">
                    {categoryIcons[category as keyof typeof categoryIcons] || '🔧'}
                  </div>
                  <h3 className="text-lg font-semibold text-zinc-200 mb-2 capitalize">
                    {category}
                  </h3>
                  <p className="text-sm text-zinc-400">
                    {categoryPlugins.length} plugin{categoryPlugins.length !== 1 ? 's' : ''} available
                  </p>
                </motion.button>
              );
            })}
          </div>
        </motion.section>
      </motion.main>
    </div>
  );
}
