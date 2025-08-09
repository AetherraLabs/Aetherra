import { motion } from 'framer-motion';
import { useState } from 'react';

interface CommunityLink {
    id: string;
    title: string;
    description: string;
    url: string;
    type: 'discord' | 'github' | 'forum' | 'documentation' | 'research' | 'social' | 'news';
    members?: number;
    activity?: string;
    verified: boolean;
    featured: boolean;
}

const communityLinks: CommunityLink[] = [
    {
        id: 'main-discord',
        title: 'Aetherra Discord Server',
        description: 'Main community hub for real-time discussions, support, and collaboration',
        url: 'https://discord.gg/aetherra-consciousness',
        type: 'discord',
        members: 12847,
        activity: 'Very Active',
        verified: true,
        featured: true
    },
    {
        id: 'core-github',
        title: 'Aetherra Core Repository',
        description: 'Main codebase for Aetherra consciousness platform',
        url: 'https://github.com/aetherra-ai/core',
        type: 'github',
        members: 3452,
        activity: 'Daily commits',
        verified: true,
        featured: true
    },
    {
        id: 'research-forum',
        title: 'Consciousness Research Forum',
        description: 'Academic discussions and research sharing on consciousness technology',
        url: 'https://forum.aetherra.ai/research',
        type: 'forum',
        members: 8934,
        activity: 'Weekly posts',
        verified: true,
        featured: true
    },
    {
        id: 'dev-docs',
        title: 'Developer Documentation',
        description: 'Comprehensive guides for plugin development and consciousness integration',
        url: 'https://docs.aetherra.ai',
        type: 'documentation',
        verified: true,
        featured: false
    },
    {
        id: 'plugin-github',
        title: 'Plugin Development Hub',
        description: 'Community repository for consciousness enhancement plugins',
        url: 'https://github.com/aetherra-ai/plugins',
        type: 'github',
        members: 2156,
        activity: 'Regular updates',
        verified: true,
        featured: false
    },
    {
        id: 'consciousness-research',
        title: 'Consciousness Studies Papers',
        description: 'Academic research papers and findings in consciousness technology',
        url: 'https://research.aetherra.ai/papers',
        type: 'research',
        members: 1847,
        activity: 'Monthly publications',
        verified: true,
        featured: false
    },
    {
        id: 'twitter-official',
        title: 'Aetherra on Twitter',
        description: 'Official updates, announcements, and consciousness insights',
        url: 'https://twitter.com/aetherra_ai',
        type: 'social',
        members: 45672,
        activity: 'Daily posts',
        verified: true,
        featured: false
    },
    {
        id: 'reddit-community',
        title: 'r/AetherraAI',
        description: 'Community discussions, showcases, and support on Reddit',
        url: 'https://reddit.com/r/AetherraAI',
        type: 'social',
        members: 23891,
        activity: 'Active daily',
        verified: true,
        featured: false
    },
    {
        id: 'medium-blog',
        title: 'Aetherra Insights Blog',
        description: 'Deep dives into consciousness technology and development insights',
        url: 'https://blog.aetherra.ai',
        type: 'news',
        activity: 'Weekly articles',
        verified: true,
        featured: false
    },
    {
        id: 'youtube-channel',
        title: 'Aetherra YouTube Channel',
        description: 'Video tutorials, consciousness demos, and community highlights',
        url: 'https://youtube.com/@aetherra-ai',
        type: 'social',
        members: 18734,
        activity: 'Weekly videos',
        verified: true,
        featured: false
    }
];

const linkTypeIcons = {
    discord: '💬',
    github: '⚡',
    forum: '🗣️',
    documentation: '📚',
    research: '🔬',
    social: '🌐',
    news: '📰'
};

const linkTypeColors = {
    discord: 'border-purple-500 bg-purple-600/20',
    github: 'border-gray-500 bg-gray-600/20',
    forum: 'border-blue-500 bg-blue-600/20',
    documentation: 'border-green-500 bg-green-600/20',
    research: 'border-yellow-500 bg-yellow-600/20',
    social: 'border-pink-500 bg-pink-600/20',
    news: 'border-orange-500 bg-orange-600/20'
};

export function CommunityLinksPanel() {
    const [selectedType, setSelectedType] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');

    const linkTypes = ['all', 'discord', 'github', 'forum', 'documentation', 'research', 'social', 'news'];

    const filteredLinks = communityLinks.filter(link => {
        const matchesType = selectedType === 'all' || link.type === selectedType;
        const matchesSearch = link.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            link.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesType && matchesSearch;
    });

    const featuredLinks = filteredLinks.filter(link => link.featured);
    const regularLinks = filteredLinks.filter(link => !link.featured);

    const openLink = (url: string) => {
        window.open(url, '_blank', 'noopener,noreferrer');
    };

    return (
        <div className="max-w-6xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Community Links</h1>
                    <p className="text-gray-400">
                        Connect with the global Aetherra consciousness community
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-blue-400">
                            {communityLinks.reduce((sum, link) => sum + (link.members || 0), 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-400">Total Members</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-400">{communityLinks.length}</div>
                        <div className="text-sm text-gray-400">Active Channels</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-purple-400">
                            {communityLinks.filter(l => l.verified).length}
                        </div>
                        <div className="text-sm text-gray-400">Verified</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-400">24/7</div>
                        <div className="text-sm text-gray-400">Community Support</div>
                    </div>
                </div>

                {/* Search and Filter */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
                    <div className="flex flex-col md:flex-row gap-4 mb-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search community links..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                            />
                        </div>
                        <div className="md:w-48">
                            <select
                                value={selectedType}
                                onChange={(e) => setSelectedType(e.target.value)}
                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                            >
                                {linkTypes.map(type => (
                                    <option key={type} value={type}>
                                        {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Type Filter Buttons */}
                    <div className="flex flex-wrap gap-2">
                        {linkTypes.map(type => (
                            <button
                                key={type}
                                onClick={() => setSelectedType(type)}
                                className={`px-3 py-1 rounded-full text-sm transition-colors ${selectedType === type
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                    }`}
                            >
                                {type === 'all' ? '🌐 All' : `${linkTypeIcons[type as keyof typeof linkTypeIcons]} ${type.charAt(0).toUpperCase() + type.slice(1)}`}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Featured Links */}
                {featuredLinks.length > 0 && (
                    <div className="mb-8">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                            ⭐ Featured Communities
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {featuredLinks.map((link) => (
                                <motion.div
                                    key={link.id}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className={`bg-gray-900 border-2 rounded-lg p-6 cursor-pointer transition-all hover:shadow-lg ${linkTypeColors[link.type]}`}
                                    onClick={() => openLink(link.url)}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="text-3xl">{linkTypeIcons[link.type]}</div>
                                        {link.verified && (
                                            <span className="text-green-400" title="Verified Community">✓</span>
                                        )}
                                    </div>

                                    <h3 className="font-bold text-white text-lg mb-2">{link.title}</h3>
                                    <p className="text-gray-300 text-sm mb-4">{link.description}</p>

                                    {(link.members || link.activity) && (
                                        <div className="flex justify-between text-xs text-gray-400 mb-4">
                                            {link.members && (
                                                <span>{link.members.toLocaleString()} members</span>
                                            )}
                                            {link.activity && (
                                                <span className="text-green-400">{link.activity}</span>
                                            )}
                                        </div>
                                    )}

                                    <div className="flex items-center justify-between">
                                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                                            {link.type}
                                        </span>
                                        <span className="text-blue-400 text-sm">Join →</span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Regular Links */}
                {regularLinks.length > 0 && (
                    <div>
                        <h2 className="text-xl font-bold text-white mb-4">All Community Links</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {regularLinks.map((link) => (
                                <motion.div
                                    key={link.id}
                                    whileHover={{ scale: 1.01 }}
                                    whileTap={{ scale: 0.99 }}
                                    className="bg-gray-900 border border-gray-700 rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors"
                                    onClick={() => openLink(link.url)}
                                >
                                    <div className="flex items-start space-x-4">
                                        <div className="text-2xl">{linkTypeIcons[link.type]}</div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center space-x-2 mb-1">
                                                <h3 className="font-bold text-white">{link.title}</h3>
                                                {link.verified && (
                                                    <span className="text-green-400 text-sm">✓</span>
                                                )}
                                            </div>
                                            <p className="text-gray-300 text-sm mb-2">{link.description}</p>

                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-3 text-xs text-gray-400">
                                                    {link.members && (
                                                        <span>{link.members.toLocaleString()} members</span>
                                                    )}
                                                    {link.activity && (
                                                        <span className="text-green-400">{link.activity}</span>
                                                    )}
                                                </div>
                                                <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                                                    {link.type}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="text-blue-400">→</div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}

                {/* No Results */}
                {filteredLinks.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-4">🔍</div>
                        <h3 className="text-xl font-bold text-white mb-2">No links found</h3>
                        <p className="text-gray-400">
                            Try adjusting your search or browse all community links
                        </p>
                    </div>
                )}

                {/* Community Guidelines */}
                <div className="mt-12 bg-gray-900 border border-gray-700 rounded-lg p-6">
                    <h3 className="font-bold text-white mb-4">🤝 Community Guidelines</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
                        <div>
                            <h4 className="font-semibold text-white mb-2">Be Respectful</h4>
                            <p>Treat all community members with respect and kindness. We're all here to advance consciousness technology together.</p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white mb-2">Share Knowledge</h4>
                            <p>Share your insights, ask questions, and help others learn. Knowledge sharing accelerates our collective progress.</p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white mb-2">Follow Safety Guidelines</h4>
                            <p>Adhere to consciousness safety protocols when sharing code or research. Safety is our top priority.</p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white mb-2">Stay on Topic</h4>
                            <p>Keep discussions relevant to consciousness technology, AI development, and related research topics.</p>
                        </div>
                    </div>
                </div>

                {/* Call to Action */}
                <div className="mt-8 text-center">
                    <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6">
                        <h3 className="text-xl font-bold text-white mb-2">Ready to Join the Community?</h3>
                        <p className="text-blue-100 mb-4">
                            Start by joining our Discord server for real-time discussions and support
                        </p>
                        <button
                            onClick={() => openLink('https://discord.gg/aetherra-consciousness')}
                            className="bg-white text-blue-600 font-bold py-2 px-6 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            Join Discord Server
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
