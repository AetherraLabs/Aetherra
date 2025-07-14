import React from 'react';
import { motion } from 'framer-motion';
import SelfImprovementFeedV4 from '../components/SelfImprovementFeedV4';
import ReflectionPanelV4 from '../components/ReflectionPanelV4';

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

export default function LyrixaTechnical() {
  return (
    <div className="min-h-screen bg-aetherra-dark text-white">
      {/* Technical Header */}
      <motion.header 
        className="bg-gradient-to-r from-aetherra-dark via-aetherra-gray to-aetherra-dark border-b border-aetherra-green/20 p-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold gradient-text mb-2">
                Lyrixa Technical Deep-Dive
              </h1>
              <p className="text-zinc-400">
                Advanced AI Self-Improvement & Neural Introspection Systems
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-aetherra-dark px-4 py-2 rounded-lg border border-aetherra-green/30">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
                  <span className="text-xs text-aetherra-green font-mono">ACTIVE</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-zinc-300">System Status</div>
                <div className="text-xs text-zinc-500">All systems operational</div>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.main 
        className="max-w-7xl mx-auto p-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Performance Metrics Row */}
        <motion.section variants={itemVariants} className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-aetherra-gray p-4 rounded-xl border border-aetherra-green/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-400">Neural Efficiency</span>
                <span className="text-xs text-green-400">↗ +12%</span>
              </div>
              <div className="text-2xl font-bold text-aetherra-green">94.7%</div>
              <div className="w-full bg-zinc-700 rounded-full h-2 mt-2">
                <div className="bg-aetherra-green h-2 rounded-full" style={{width: '94.7%'}}></div>
              </div>
            </div>

            <div className="bg-aetherra-gray p-4 rounded-xl border border-blue-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-400">Response Time</span>
                <span className="text-xs text-green-400">↗ -23ms</span>
              </div>
              <div className="text-2xl font-bold text-blue-400">127ms</div>
              <div className="w-full bg-zinc-700 rounded-full h-2 mt-2">
                <div className="bg-blue-400 h-2 rounded-full" style={{width: '78%'}}></div>
              </div>
            </div>

            <div className="bg-aetherra-gray p-4 rounded-xl border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-400">Learning Rate</span>
                <span className="text-xs text-green-400">↗ +8.3%</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">0.87</div>
              <div className="w-full bg-zinc-700 rounded-full h-2 mt-2">
                <div className="bg-purple-400 h-2 rounded-full" style={{width: '87%'}}></div>
              </div>
            </div>

            <div className="bg-aetherra-gray p-4 rounded-xl border border-yellow-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-400">Memory Usage</span>
                <span className="text-xs text-green-400">↗ -15%</span>
              </div>
              <div className="text-2xl font-bold text-yellow-400">2.1GB</div>
              <div className="w-full bg-zinc-700 rounded-full h-2 mt-2">
                <div className="bg-yellow-400 h-2 rounded-full" style={{width: '35%'}}></div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Main Dashboard Grid */}
        <motion.section variants={itemVariants}>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Self-Improvement Feed */}
            <div>
              <SelfImprovementFeedV4 />
            </div>

            {/* Neural Reflection Panel */}
            <div>
              <ReflectionPanelV4 />
            </div>
          </div>
        </motion.section>

        {/* Technical Insights Section */}
        <motion.section variants={itemVariants} className="mt-8">
          <div className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20">
            <h3 className="text-xl font-semibold gradient-text mb-4">
              ⚡ Real-time Technical Insights
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-aetherra-dark p-4 rounded-lg border border-zinc-700/50">
                <h4 className="text-sm font-semibold text-zinc-200 mb-2">
                  🧩 Plugin Architecture
                </h4>
                <p className="text-xs text-zinc-400 mb-3">
                  Dynamic plugin loading with hot-swap capabilities
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-aetherra-green">47 active plugins</span>
                  <span className="text-xs text-blue-400">0.3ms avg load time</span>
                </div>
              </div>

              <div className="bg-aetherra-dark p-4 rounded-lg border border-zinc-700/50">
                <h4 className="text-sm font-semibold text-zinc-200 mb-2">
                  🔄 Adaptive Learning
                </h4>
                <p className="text-xs text-zinc-400 mb-3">
                  Continuous model refinement through interaction
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-purple-400">12.7k iterations</span>
                  <span className="text-xs text-green-400">+18% accuracy</span>
                </div>
              </div>

              <div className="bg-aetherra-dark p-4 rounded-lg border border-zinc-700/50">
                <h4 className="text-sm font-semibold text-zinc-200 mb-2">
                  🛡️ Error Resilience
                </h4>
                <p className="text-xs text-zinc-400 mb-3">
                  Self-healing architecture with graceful degradation
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-red-400">3 errors handled</span>
                  <span className="text-xs text-green-400">99.97% uptime</span>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* System Status Footer */}
        <motion.footer variants={itemVariants} className="mt-8 text-center">
          <div className="bg-aetherra-gray p-4 rounded-xl border border-aetherra-green/20">
            <div className="flex items-center justify-center space-x-8 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
                <span className="text-zinc-400">Core Systems: Online</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-zinc-400">Learning Engine: Active</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span className="text-zinc-400">Self-Improvement: Running</span>
              </div>
            </div>
          </div>
        </motion.footer>
      </motion.main>
    </div>
  );
}
