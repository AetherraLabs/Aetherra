import { motion } from 'framer-motion';

interface ContributionPanelProps {
  className?: string;
}

const contributionStats = {
  totalContributors: 1456,
  pluginsSubmitted: 247,
  issuesResolved: 892,
  communityMembers: 12847
};

export default function ContributionPanel({ className = '' }: ContributionPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-gradient-to-br from-aetherra-gray to-aetherra-dark p-8 rounded-xl border border-aetherra-green/30 ${className}`}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold gradient-text mb-3">
          🚀 Join the Aetherra Revolution
        </h2>
        <p className="text-zinc-300 text-lg">
          Help shape the future of AI-native computing
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        <div className="text-center">
          <div className="text-2xl font-bold text-aetherra-green mb-1">
            {contributionStats.totalContributors.toLocaleString()}
          </div>
          <div className="text-sm text-zinc-400">Contributors</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-400 mb-1">
            {contributionStats.pluginsSubmitted}
          </div>
          <div className="text-sm text-zinc-400">Plugins</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-400 mb-1">
            {contributionStats.issuesResolved}
          </div>
          <div className="text-sm text-zinc-400">Issues Resolved</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {contributionStats.communityMembers.toLocaleString()}
          </div>
          <div className="text-sm text-zinc-400">Community</div>
        </div>
      </div>

      {/* Call to Action Buttons */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        {/* GitHub Contribution */}
        <motion.a
          href="https://github.com/Zyonic88/Aetherra"
          target="_blank"
          rel="noopener noreferrer"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="group bg-aetherra-dark p-6 rounded-lg border border-zinc-700 hover:border-aetherra-green/50 transition-all block"
        >
          <div className="flex items-center space-x-4 mb-3">
            <div className="text-3xl">💻</div>
            <div>
              <h3 className="text-lg font-semibold text-zinc-200 group-hover:text-aetherra-green transition-colors">
                Contribute Code
              </h3>
              <p className="text-sm text-zinc-400">
                Submit plugins, fix bugs, improve core
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500">
              View on GitHub
            </span>
            <span className="text-aetherra-green group-hover:translate-x-1 transition-transform">
              →
            </span>
          </div>
        </motion.a>

        {/* Discord Community */}
        <motion.a
          href="https://discord.gg/9Xw28xgEQ3"
          target="_blank"
          rel="noopener noreferrer"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="group bg-aetherra-dark p-6 rounded-lg border border-zinc-700 hover:border-blue-500/50 transition-all block"
        >
          <div className="flex items-center space-x-4 mb-3">
            <div className="text-3xl">💬</div>
            <div>
              <h3 className="text-lg font-semibold text-zinc-200 group-hover:text-blue-400 transition-colors">
                Join Discord
              </h3>
              <p className="text-sm text-zinc-400">
                Chat with developers and users
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500">
              4,521 members online
            </span>
            <span className="text-blue-400 group-hover:translate-x-1 transition-transform">
              →
            </span>
          </div>
        </motion.a>
      </div>

      {/* Quick Action Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center justify-center space-x-2 py-3 px-4 bg-gradient-to-r from-aetherra-green to-green-500 text-aetherra-dark rounded-lg font-semibold hover:from-aetherra-green/90 hover:to-green-500/90 transition-all"
        >
          <span>🔧</span>
          <span>Submit Plugin</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center justify-center space-x-2 py-3 px-4 bg-zinc-700 text-zinc-200 rounded-lg hover:bg-zinc-600 transition-colors"
        >
          <span>📚</span>
          <span>Documentation</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center justify-center space-x-2 py-3 px-4 bg-zinc-700 text-zinc-200 rounded-lg hover:bg-zinc-600 transition-colors"
        >
          <span>🐛</span>
          <span>Report Bug</span>
        </motion.button>
      </div>

      {/* Footer Note */}
      <div className="text-center mt-6 pt-6 border-t border-zinc-700">
        <p className="text-sm text-zinc-400">
          Every contribution makes Aetherra more powerful.{' '}
          <span className="text-aetherra-green">Thank you for building the future!</span>
        </p>
      </div>
    </motion.div>
  );
}
