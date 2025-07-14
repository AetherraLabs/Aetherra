import React, { useState } from 'react'
import { motion } from 'framer-motion'
import MemoryGraph from '../components/MemoryGraph'
import SystemDashboard from '../components/SystemDashboard'
import ReflexTrace from '../components/ReflexTrace'
import PluginThoughtMap from '../components/PluginThoughtMap'
import LiveReasoningStream from '../components/LiveReasoningStream'
import DataToggle from '../components/DataToggle'

export default function LiveIntrospection() {
  const [isLiveMode, setIsLiveMode] = useState(false);

  const handleModeChange = (isLive: boolean) => {
    setIsLiveMode(isLive);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="min-h-screen bg-aetherra-dark text-white p-6 space-y-6"
    >
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-4xl font-bold bg-gradient-to-r from-aetherra-green to-blue-400 bg-clip-text text-transparent"
        >
          🧠 Live Introspection
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-lg text-gray-300 max-w-2xl mx-auto"
        >
          Peer directly into Lyrixa's cognitive processes in real-time. Watch thoughts form, 
          see memory networks evolve, and observe reflexive improvements as they happen.
        </motion.p>
      </div>

      {/* Data Source Toggle */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.6 }}
      >
        <DataToggle onModeChange={handleModeChange} />
      </motion.div>

      {/* System Overview Dashboard */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.8 }}
      >
        <SystemDashboard />
      </motion.div>

      {/* Two-column layout for main content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0 }}
          >
            <MemoryGraph />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 }}
          >
            <ReflexTrace />
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0 }}
          >
            <PluginThoughtMap />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 }}
          >
            <LiveReasoningStream />
          </motion.div>
        </div>
      </div>

      {/* Status Footer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.4 }}
        className="text-center p-4 bg-gray-900 rounded-xl border border-gray-700"
      >
        <div className="text-sm text-gray-400">
          {isLiveMode ? (
            <span className="flex items-center justify-center space-x-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span>Connected to live Lyrixa instance • Real-time cognitive monitoring active</span>
            </span>
          ) : (
            <span className="flex items-center justify-center space-x-2">
              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
              <span>Demo mode • Simulated cognitive processes for showcase purposes</span>
            </span>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
