import { motion } from 'framer-motion';
import { useState } from 'react';

interface CommunityLink {
  id: string;
  name: string;
  description: string;
  url: string;
  icon: string;
  color: string;
  members?: string;
  activity?: string;
}

interface CommunityLinksPanelProps {
  onLinkClick?: (link: CommunityLink) => void;
}

export default function CommunityLinksPanel({ onLinkClick }: CommunityLinksPanelProps) {
  const [hoveredLink, setHoveredLink] = useState<string | null>(null);

  const communityLinks: CommunityLink[] = [
    {
      id: 'github',
      name: 'GitHub',
      description: 'Contribute code, report issues, and collaborate on the Aetherra codebase. Join our open-source development community.',
      url: 'https://github.com/aetherra/aetherra',
      icon: '🐙',
      color: 'bg-gray-700 hover:bg-gray-600 border-gray-600',
      members: 'Open Source',
      activity: 'Active development'
    },
    {
      id: 'discord',
      name: 'Discord',
      description: 'Real-time chat with the community, get help, share projects, and participate in voice channels and events.',
      url: 'https://discord.gg/aetherra',
      icon: '💬',
      color: 'bg-indigo-700 hover:bg-indigo-600 border-indigo-600',
      members: 'Coming Soon',
      activity: 'Setting up community'
    },
    {
      id: 'twitter',
      name: 'Twitter / X',
      description: 'Follow for the latest updates, announcements, AI research insights, and community highlights.',
      url: 'https://twitter.com/aetherra_ai',
      icon: '🐦',
      color: 'bg-blue-700 hover:bg-blue-600 border-blue-600',
      members: 'Coming Soon',
      activity: 'Daily updates'
    }
  ];

  const handleLinkClick = (link: CommunityLink) => {
    onLinkClick?.(link);
    // Open in new tab
    window.open(link.url, '_blank', 'noopener,noreferrer');
  };

  const getAdditionalInfo = (linkId: string) => {
    switch (linkId) {
      case 'github':
        return {
          stats: [
            { label: 'Stars', value: 'TBD' },
            { label: 'Forks', value: 'TBD' },
            { label: 'Issues', value: 'TBD' },
            { label: 'PRs', value: 'TBD' }
          ],
          highlights: [
            'Open source and transparent development',
            'Weekly community calls and roadmap reviews',
            'Contributor recognition and mentorship program',
            'Comprehensive documentation and guides'
          ]
        };
      case 'discord':
        return {
          stats: [
            { label: 'Channels', value: 'TBD' },
            { label: 'Online', value: 'TBD' },
            { label: 'Events', value: 'Weekly' },
            { label: 'Bots', value: 'AI helpers' }
          ],
          highlights: [
            'Real-time help and troubleshooting support',
            'Voice channels for pair programming',
            'Weekly community events and workshops',
            'Showcase your projects and get feedback'
          ]
        };
      case 'twitter':
        return {
          stats: [
            { label: 'Tweets', value: 'TBD' },
            { label: 'Engagement', value: 'High' },
            { label: 'Hashtag', value: '#AetherraAI' },
            { label: 'Lists', value: 'AI Tech' }
          ],
          highlights: [
            'Latest AI research and breakthrough announcements',
            'Community project highlights and features',
            'Tech talks and conference updates',
            'Behind-the-scenes development insights'
          ]
        };
      default:
        return { stats: [], highlights: [] };
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <h2 className="text-xl font-bold text-aetherra-green mb-2">
          🌐 Join Our Community
        </h2>
        <p className="text-gray-400 text-sm">
          Connect with developers, AI researchers, and enthusiasts building the future of neural computing
        </p>
      </div>

      {/* Community Links */}
      <div className="flex-1 p-4">
        <div className="space-y-4">
          {communityLinks.map((link, index) => (
            <motion.div
              key={link.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              onMouseEnter={() => setHoveredLink(link.id)}
              onMouseLeave={() => setHoveredLink(null)}
              className="relative"
            >
              <div
                onClick={() => handleLinkClick(link)}
                className={`${link.color} rounded-xl p-4 border-2 cursor-pointer transition-all duration-300 transform hover:scale-105 hover:shadow-lg`}
              >
                {/* Main Link Content */}
                <div className="flex items-start space-x-4">
                  <div className="text-4xl">{link.icon}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xl font-semibold text-white">{link.name}</h3>
                      <div className="flex items-center space-x-3 text-sm text-gray-300">
                        <span>{link.members}</span>
                        <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                        <span>{link.activity}</span>
                      </div>
                    </div>
                    <p className="text-gray-300 text-sm mb-3 leading-relaxed">
                      {link.description}
                    </p>

                    {/* Quick Stats */}
                    {hoveredLink === link.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-3"
                      >
                        <div className="grid grid-cols-4 gap-2">
                          {getAdditionalInfo(link.id).stats.map((stat, idx) => (
                            <div key={idx} className="text-center">
                              <div className="text-white font-semibold text-sm">{stat.value}</div>
                              <div className="text-gray-400 text-xs">{stat.label}</div>
                            </div>
                          ))}
                        </div>

                        <div className="bg-black bg-opacity-30 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-2">Platform Highlights:</h4>
                          <ul className="space-y-1">
                            {getAdditionalInfo(link.id).highlights.map((highlight, idx) => (
                              <li key={idx} className="text-gray-300 text-xs flex items-start">
                                <span className="text-aetherra-green mr-2">•</span>
                                {highlight}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </div>

                {/* Call to Action */}
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-gray-400 text-sm">
                    <span>Click to join</span>
                    <span>→</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {link.id === 'github' && (
                      <div className="flex space-x-1">
                        <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded">Open Source</span>
                        <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">Active</span>
                      </div>
                    )}
                    {link.id === 'discord' && (
                      <div className="flex space-x-1">
                        <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded">Live Chat</span>
                        <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">24/7</span>
                      </div>
                    )}
                    {link.id === 'twitter' && (
                      <div className="flex space-x-1">
                        <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">Updates</span>
                        <span className="bg-yellow-600 text-white text-xs px-2 py-1 rounded">News</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Additional Community Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-6 bg-gradient-to-r from-aetherra-green/10 to-purple-600/10 rounded-xl p-4 border border-aetherra-green/30"
        >
          <h3 className="text-lg font-semibold text-white mb-3">🎯 Community Guidelines</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-aetherra-green mb-2">Core Values</h4>
              <ul className="space-y-1 text-gray-300">
                <li>• Respect and inclusivity for all members</li>
                <li>• Constructive feedback and collaboration</li>
                <li>• Knowledge sharing and mentorship</li>
                <li>• Innovation and creative problem-solving</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-purple-400 mb-2">What to Expect</h4>
              <ul className="space-y-1 text-gray-300">
                <li>• Weekly community events and workshops</li>
                <li>• Direct access to core development team</li>
                <li>• Early previews of new features</li>
                <li>• Opportunities to shape the project roadmap</li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3"
        >
          <button className="bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg p-3 text-center transition-colors">
            <div className="text-2xl mb-1">📧</div>
            <div className="text-white font-medium text-sm">Newsletter</div>
            <div className="text-gray-400 text-xs">Weekly updates</div>
          </button>
          <button className="bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg p-3 text-center transition-colors">
            <div className="text-2xl mb-1">📝</div>
            <div className="text-white font-medium text-sm">Blog</div>
            <div className="text-gray-400 text-xs">Tech insights</div>
          </button>
          <button className="bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg p-3 text-center transition-colors">
            <div className="text-2xl mb-1">🎥</div>
            <div className="text-white font-medium text-sm">YouTube</div>
            <div className="text-gray-400 text-xs">Tutorials & talks</div>
          </button>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-6 bg-gray-800 rounded-xl p-4 border border-gray-700"
        >
          <h3 className="text-lg font-semibold text-white mb-3 text-center">
            🌍 Global Community Impact
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-aetherra-green">TBD</div>
              <div className="text-gray-400 text-sm">Total Members</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">TBD</div>
              <div className="text-gray-400 text-sm">Countries</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">TBD</div>
              <div className="text-gray-400 text-sm">Contributors</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">TBD</div>
              <div className="text-gray-400 text-sm">Code Commits</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
