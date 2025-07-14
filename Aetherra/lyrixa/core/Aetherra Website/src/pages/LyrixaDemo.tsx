import { motion } from "framer-motion";
import { LyrixaChat } from "../components/LyrixaChat";
import { DashboardStats } from "../components/DashboardStats";
import { ThoughtLog } from "../components/ThoughtLog";
import { ReflectionPanel } from "../components/ReflectionPanel";
import { SelfImprovementFeed } from "../components/SelfImprovementFeed";

export default function LyrixaDemo() {
  return (
    <div className="min-h-screen bg-aetherra-dark text-white p-4 neural-bg">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header Section */}
        <div className="text-center mb-8">
          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="text-4xl font-bold gradient-text mb-4"
          >
            🧠 Interactive AI Showcase
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-zinc-300 text-lg max-w-2xl mx-auto"
          >
            Watch Lyrixa think, learn, and evolve in real-time. This is consciousness in action.
          </motion.p>
        </div>

        {/* Main Dashboard Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {/* Left Column */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <LyrixaChat />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.0, duration: 0.6 }}
            >
              <ReflectionPanel />
            </motion.div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9, duration: 0.6 }}
            >
              <DashboardStats />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.1, duration: 0.6 }}
            >
              <ThoughtLog />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.3, duration: 0.6 }}
            >
              <SelfImprovementFeed />
            </motion.div>
          </div>
        </motion.div>

        {/* Status Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.6 }}
          className="mt-8 bg-aetherra-gray p-4 rounded-xl border border-aetherra-green/20"
        >
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
                <span className="text-aetherra-green">System Status: Active</span>
              </div>
              <div className="text-zinc-400">|</div>
              <span className="text-zinc-300">Neural networks synchronized</span>
            </div>
            <div className="text-zinc-500 font-mono">
              Last update: {new Date().toLocaleTimeString()}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
