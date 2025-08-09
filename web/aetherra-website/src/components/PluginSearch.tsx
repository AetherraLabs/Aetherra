import { useState } from 'react';

interface PluginSearchProps {
    onSearch: (query: string) => void;
    onCategoryFilter: (category: string) => void;
    onStatusFilter: (status: string) => void;
}

export default function PluginSearch({ onSearch, onCategoryFilter, onStatusFilter }: PluginSearchProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedStatus, setSelectedStatus] = useState('');

    const categories = ['All', 'Text Processing', 'System Optimization', 'Goal Management', 'Audio Processing'];
    const statuses = ['All', 'active', 'beta', 'experimental'];

    const handleSearchChange = (value: string) => {
        setSearchQuery(value);
        onSearch(value);
    };

    const handleCategoryChange = (category: string) => {
        setSelectedCategory(category);
        onCategoryFilter(category === 'All' ? '' : category);
    };

    const handleStatusChange = (status: string) => {
        setSelectedStatus(status);
        onStatusFilter(status === 'All' ? '' : status);
    };

    return (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg mb-6">
            <h2 className="text-xl font-semibold mb-4">🔍 Find Plugins</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        placeholder="Search plugins..."
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                    <select
                        value={selectedCategory}
                        onChange={(e) => handleCategoryChange(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        {categories.map((category) => (
                            <option key={category} value={category}>
                                {category}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
                    <select
                        value={selectedStatus}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        {statuses.map((status) => (
                            <option key={status} value={status}>
                                {status === 'All' ? 'All Statuses' : status}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
                <span className="text-sm text-gray-400">Popular tags:</span>
                {['nlp', 'optimization', 'automation', 'ai'].map((tag) => (
                    <button
                        key={tag}
                        onClick={() => handleSearchChange(tag)}
                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-sm transition-colors"
                    >
                        {tag}
                    </button>
                ))}
            </div>
        </div>
    );
}
