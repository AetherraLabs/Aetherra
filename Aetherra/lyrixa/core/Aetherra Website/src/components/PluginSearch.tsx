import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface PluginSearchProps {
  onSearch: (query: string) => void;
  onCategoryFilter: (category: string | null) => void;
  onTagFilter: (tag: string | null) => void;
  onSortChange: (sort: 'popularity' | 'rating' | 'recent' | 'name') => void;
  availableCategories: string[];
  availableTags: string[];
  totalResults: number;
}

const categoryIcons = {
  performance: '⚡',
  memory: '🧠',
  personality: '🎭',
  security: '🛡️',
  creativity: '🎨',
  development: '👨‍💻'
};

export default function PluginSearch({
  onSearch,
  onCategoryFilter,
  onTagFilter,
  onSortChange,
  availableCategories,
  availableTags,
  totalResults
}: PluginSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'popularity' | 'rating' | 'recent' | 'name'>('popularity');
  const [showFilters, setShowFilters] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch(query);
  };

  const handleCategorySelect = (category: string | null) => {
    setSelectedCategory(category);
    onCategoryFilter(category);
  };

  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag);
    onTagFilter(tag);
  };

  const handleSortChange = (sort: 'popularity' | 'rating' | 'recent' | 'name') => {
    setSortBy(sort);
    onSortChange(sort);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory(null);
    setSelectedTag(null);
    setSortBy('popularity');
    onSearch('');
    onCategoryFilter(null);
    onTagFilter(null);
    onSortChange('popularity');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20 mb-8"
    >
      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search plugins by name, description, or author..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="w-full px-4 py-3 pl-12 bg-aetherra-dark border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-aetherra-green focus:outline-none transition-colors"
          />
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-zinc-500">
            🔍
          </div>
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                onSearch('');
              }}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Filter Toggle */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-3 py-2 bg-aetherra-dark rounded-lg hover:bg-zinc-600 transition-colors"
          >
            <span className="text-sm">Filters</span>
            <span className={`transform transition-transform ${showFilters ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          <div className="text-sm text-zinc-400">
            {totalResults} plugin{totalResults !== 1 ? 's' : ''} found
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-zinc-400">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => handleSortChange(e.target.value as any)}
            className="px-3 py-2 bg-aetherra-dark border border-zinc-700 rounded text-white text-sm focus:border-aetherra-green focus:outline-none"
          >
            <option value="popularity">Popularity</option>
            <option value="rating">Rating</option>
            <option value="recent">Recently Updated</option>
            <option value="name">Name</option>
          </select>
        </div>
      </div>

      {/* Expanded Filters */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="border-t border-zinc-700 pt-4"
        >
          {/* Categories */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-zinc-300 mb-3">Categories</h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleCategorySelect(null)}
                className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedCategory === null
                    ? 'bg-aetherra-green text-aetherra-dark'
                    : 'bg-aetherra-dark text-zinc-300 hover:bg-zinc-600'
                }`}
              >
                All Categories
              </button>
              {availableCategories.map((category) => (
                <button
                  key={category}
                  onClick={() => handleCategorySelect(category)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors flex items-center space-x-2 ${
                    selectedCategory === category
                      ? 'bg-aetherra-green text-aetherra-dark'
                      : 'bg-aetherra-dark text-zinc-300 hover:bg-zinc-600'
                  }`}
                >
                  <span>{categoryIcons[category as keyof typeof categoryIcons] || '🔧'}</span>
                  <span className="capitalize">{category}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-zinc-300 mb-3">Popular Tags</h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleTagSelect(null)}
                className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedTag === null
                    ? 'bg-aetherra-green text-aetherra-dark'
                    : 'bg-aetherra-dark text-zinc-300 hover:bg-zinc-600'
                }`}
              >
                All Tags
              </button>
              {availableTags.slice(0, 12).map((tag) => (
                <button
                  key={tag}
                  onClick={() => handleTagSelect(tag)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedTag === tag
                      ? 'bg-aetherra-green text-aetherra-dark'
                      : 'bg-aetherra-dark text-zinc-300 hover:bg-zinc-600'
                  }`}
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>

          {/* Clear Filters */}
          <div className="flex justify-end">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Clear All Filters
            </button>
          </div>
        </motion.div>
      )}

      {/* Active Filters */}
      {(selectedCategory || selectedTag || searchQuery) && (
        <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-zinc-700">
          <span className="text-sm text-zinc-400">Active filters:</span>
          {searchQuery && (
            <span className="px-2 py-1 bg-blue-900 text-blue-200 rounded text-xs">
              Search: "{searchQuery}"
            </span>
          )}
          {selectedCategory && (
            <span className="px-2 py-1 bg-purple-900 text-purple-200 rounded text-xs flex items-center space-x-1">
              <span>{categoryIcons[selectedCategory as keyof typeof categoryIcons]}</span>
              <span className="capitalize">{selectedCategory}</span>
            </span>
          )}
          {selectedTag && (
            <span className="px-2 py-1 bg-green-900 text-green-200 rounded text-xs">
              #{selectedTag}
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
}
