import React from 'react';
import LyrixaChat from '../components/LyrixaChat';
import DashboardStats from '../components/DashboardStats';
import ThoughtLog from '../components/ThoughtLog';
import ReflectionPanel from '../components/ReflectionPanel';
import SelfImprovementFeed from '../components/SelfImprovementFeed';

export default function LyrixaSandbox() {
  return (
    <div className="min-h-screen bg-aetherra-dark text-white p-6 neural-bg">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">
            🧪 Lyrixa Sandbox Demo
          </h1>
          <p className="text-zinc-300 text-lg max-w-2xl mx-auto">
            Experience Lyrixa's cognitive processes in a controlled environment. 
            Watch real-time AI decision making and self-improvement cycles.
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <DashboardStats />
            <ReflectionPanel />
            <SelfImprovementFeed />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <ThoughtLog />
            <LyrixaChat />
          </div>
        </div>

        {/* Footer Status */}
        <div className="mt-8 bg-aetherra-gray p-4 rounded-xl border border-aetherra-green/20">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-aetherra-green rounded-full animate-pulse"></div>
                <span className="text-aetherra-green">Sandbox Environment: Active</span>
              </div>
              <div className="text-zinc-400">|</div>
              <span className="text-zinc-300">All systems operational</span>
            </div>
            <div className="text-zinc-500 font-mono">
              Sandbox Mode • Safe Environment
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
