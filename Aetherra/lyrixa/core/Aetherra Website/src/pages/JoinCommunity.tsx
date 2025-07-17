import { motion } from 'framer-motion';
import communityData from '../data/community_activity.json';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
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

export default function JoinCommunity() {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getActivityIcon = (type: string) => {
    const icons = {
      plugin_release: '🚀',
      community_contribution: '🤝',
      discussion: '💬',
      showcase: '🎨',
      bug_fix: '🐛',
      tutorial: '📚',
      integration: '🔧'
    };
    return icons[type as keyof typeof icons] || '📢';
  };

  return (
    <div className="min-h-screen bg-aetherra-dark text-white">
      {/* Hero Section */}
      <motion.section
        className="bg-gradient-to-br from-aetherra-dark via-aetherra-gray to-aetherra-dark border-b border-aetherra-green/20 py-16"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-6">
            💫 Join the Aetherra Community
          </h1>
          <p className="text-xl text-zinc-300 mb-8 max-w-3xl mx-auto">
            Connect with developers, researchers, and enthusiasts building the future of AI-native computing.
            Share ideas, get support, and collaborate on groundbreaking projects.
          </p>

          {/* Community Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
            <div>
              <div className="text-2xl font-bold text-aetherra-green">
                {communityData.stats.community_members.toLocaleString()}
              </div>
              <div className="text-sm text-zinc-400">Community Members</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">
                {communityData.stats.discord_members.toLocaleString()}
              </div>
              <div className="text-sm text-zinc-400">Discord Members</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">
                {communityData.stats.github_stars.toLocaleString()}
              </div>
              <div className="text-sm text-zinc-400">GitHub Stars</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {communityData.stats.active_developers.toLocaleString()}
              </div>
              <div className="text-sm text-zinc-400">Active Developers</div>
            </div>
          </div>
          
          {/* Transparency Notice */}
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <p className="text-sm text-blue-300 text-center">
                <strong>🌱 Growing Community:</strong> Aetherra is a new project with an authentic, 
                passionate community. These are our real numbers as we build something revolutionary together.
              </p>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Main Content */}
      <motion.main
        className="max-w-6xl mx-auto px-6 py-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Join Platforms */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8 text-center">Connect With Us</h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Discord */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className="bg-gradient-to-br from-indigo-900/50 to-blue-900/50 p-8 rounded-xl border border-blue-500/30 text-center"
            >
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-2xl font-bold text-blue-400 mb-3">Discord Community</h3>
              <p className="text-zinc-300 mb-6">
                Real-time discussions, support, and collaboration with fellow developers.
              </p>
              <div className="mb-6">
                <div className="text-lg font-semibold text-blue-300">
                  {communityData.stats.discord_members.toLocaleString()} members
                </div>
                <div className="text-sm text-zinc-400">Coming Soon</div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
              >
                Join Discord Server
              </motion.button>
            </motion.div>

            {/* GitHub */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className="bg-gradient-to-br from-gray-900/50 to-zinc-900/50 p-8 rounded-xl border border-zinc-500/30 text-center"
            >
              <div className="text-6xl mb-4">💻</div>
              <h3 className="text-2xl font-bold text-zinc-300 mb-3">GitHub Repository</h3>
              <p className="text-zinc-300 mb-6">
                Contribute code, report issues, and access the complete source code.
              </p>
              <div className="mb-6">
                <div className="text-lg font-semibold text-zinc-300">
                  {communityData.stats.github_stars.toLocaleString()} stars
                </div>
                <div className="text-sm text-zinc-400">Open source & collaborative</div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full py-3 bg-zinc-700 hover:bg-zinc-600 rounded-lg font-semibold transition-colors"
              >
                View on GitHub
              </motion.button>
            </motion.div>

            {/* Twitter/X */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className="bg-gradient-to-br from-slate-900/50 to-gray-900/50 p-8 rounded-xl border border-slate-500/30 text-center"
            >
              <div className="text-6xl mb-4">🐦</div>
              <h3 className="text-2xl font-bold text-slate-300 mb-3">Follow on X</h3>
              <p className="text-zinc-300 mb-6">
                Stay updated with announcements, releases, and community highlights.
              </p>
              <div className="mb-6">
                <div className="text-lg font-semibold text-slate-300">
                  Coming Soon
                </div>
                <div className="text-sm text-zinc-400">Daily updates & insights</div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold transition-colors"
              >
                Follow @AetherraAI
              </motion.button>
            </motion.div>
          </div>
        </motion.section>

        {/* Community Activity Feed */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Recent Community Activity</h2>

          <div className="grid lg:grid-cols-2 gap-8">
            <div className="space-y-4">
              {communityData.activity.slice(0, 4).map((activity) => (
                <motion.div
                  key={activity.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700/50 hover:border-aetherra-green/30 transition-all"
                >
                  <div className="flex items-start space-x-4">
                    <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs ${activity.type === 'plugin_release' ? 'bg-green-900 text-green-200' :
                            activity.type === 'community_contribution' ? 'bg-blue-900 text-blue-200' :
                              activity.type === 'discussion' ? 'bg-purple-900 text-purple-200' :
                                'bg-zinc-900 text-zinc-200'
                          }`}>
                          {activity.type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-zinc-500">by @{activity.author}</span>
                      </div>
                      <h3 className="font-semibold text-zinc-200 mb-2">{activity.title}</h3>
                      <p className="text-sm text-zinc-400 mb-3">{activity.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-xs text-zinc-500">
                          <span>❤️ {activity.engagement.likes}</span>
                          <span>💬 {activity.engagement.comments}</span>
                          <span>🔄 {activity.engagement.shares}</span>
                        </div>
                        <span className="text-xs text-zinc-500">
                          {formatTimestamp(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="space-y-4">
              {communityData.activity.slice(4).map((activity) => (
                <motion.div
                  key={activity.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700/50 hover:border-aetherra-green/30 transition-all"
                >
                  <div className="flex items-start space-x-4">
                    <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs ${activity.type === 'plugin_release' ? 'bg-green-900 text-green-200' :
                            activity.type === 'community_contribution' ? 'bg-blue-900 text-blue-200' :
                              activity.type === 'discussion' ? 'bg-purple-900 text-purple-200' :
                                'bg-zinc-900 text-zinc-200'
                          }`}>
                          {activity.type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-zinc-500">by @{activity.author}</span>
                      </div>
                      <h3 className="font-semibold text-zinc-200 mb-2">{activity.title}</h3>
                      <p className="text-sm text-zinc-400 mb-3">{activity.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-xs text-zinc-500">
                          <span>❤️ {activity.engagement.likes}</span>
                          <span>💬 {activity.engagement.comments}</span>
                          <span>🔄 {activity.engagement.shares}</span>
                        </div>
                        <span className="text-xs text-zinc-500">
                          {formatTimestamp(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Trending Topics */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Trending Topics</h2>

          <div className="bg-aetherra-gray p-8 rounded-xl border border-aetherra-green/20">
            <div className="flex flex-wrap gap-3">
              {communityData.trending_tags.map((tag, index) => (
                <motion.button
                  key={tag}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors ${index === 0 ? 'bg-aetherra-green text-aetherra-dark' :
                      index === 1 ? 'bg-blue-600 text-white' :
                        index === 2 ? 'bg-purple-600 text-white' :
                          'bg-zinc-700 text-zinc-200 hover:bg-zinc-600'
                    }`}
                >
                  #{tag}
                </motion.button>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Call to Action */}
        <motion.section variants={itemVariants}>
          <div className="bg-gradient-to-r from-aetherra-green/20 to-blue-500/20 p-8 rounded-xl border border-aetherra-green/30 text-center">
            <h2 className="text-2xl font-bold gradient-text mb-4">
              🚀 Ready to Shape the Future?
            </h2>
            <p className="text-zinc-300 mb-6">
              Join our growing community of innovators and help build the next generation of AI-native systems.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                💬 Join Discord
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-aetherra-green text-aetherra-dark rounded-lg font-semibold hover:bg-aetherra-green/90 transition-colors"
              >
                🌟 Star on GitHub
              </motion.button>
            </div>
          </div>
        </motion.section>
      </motion.main>
    </div>
  );
}
