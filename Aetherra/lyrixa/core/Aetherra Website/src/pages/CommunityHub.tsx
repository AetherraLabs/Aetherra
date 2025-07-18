import React, { useState } from 'react'
import { motion } from 'framer-motion'
import AetherHubGallery from '../components/AetherHubGallery'
import PluginSubmissionForm from '../components/PluginSubmissionForm'
import ContributionGuide from '../components/ContributionGuide'
import CommunityLinksPanel from '../components/CommunityLinksPanel'

type ActiveTab = 'gallery' | 'submit' | 'contribute' | 'community';

export default function CommunityHub() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('gallery');
  const [showSubmissionForm, setShowSubmissionForm] = useState(false);

  const tabs = [
    { 
      id: 'gallery' as ActiveTab, 
      label: 'Plugin Gallery', 
      icon: '🔌',
      description: 'Browse and install community plugins'
    },
    { 
      id: 'submit' as ActiveTab, 
      label: 'Submit Plugin', 
      icon: '📤',
      description: 'Share your plugin with the community'
    },
    { 
      id: 'contribute' as ActiveTab, 
      label: 'Contribute', 
      icon: '🛠️',
      description: 'Help build the future of neural computing'
    },
    { 
      id: 'community' as ActiveTab, 
      label: 'Community', 
      icon: '👥',
      description: 'Connect with developers worldwide'
    }
  ];

  const handlePluginInstall = (plugin: any) => {
    // Handle plugin installation
    console.log('Installing plugin:', plugin);
  };

  const handlePluginSubmission = (data: any) => {
    // Handle plugin submission
    console.log('Plugin submitted:', data);
    setShowSubmissionForm(false);
    setActiveTab('gallery');
  };

  const handleNavigateToSubmission = () => {
    setActiveTab('submit');
  };

  const handleCommunityLinkClick = (link: any) => {
    console.log('Community link clicked:', link);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'gallery':
        return (
          <AetherHubGallery
            onInstallPlugin={handlePluginInstall}
            onViewDetails={(plugin) => console.log('View details:', plugin)}
          />
        );
      
      case 'submit':
        return (
          <PluginSubmissionForm
            onSubmit={handlePluginSubmission}
            onCancel={() => setActiveTab('gallery')}
          />
        );
      
      case 'contribute':
        return (
          <ContributionGuide
            onNavigateToSubmission={handleNavigateToSubmission}
          />
        );
      
      case 'community':
        return (
          <CommunityLinksPanel
            onLinkClick={handleCommunityLinkClick}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="min-h-screen bg-black text-white"
    >
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="absolute inset-0 bg-[url('/neural-bg.svg')] opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="gradient-text">Community Hub</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-3xl mx-auto mb-8">
              Discover, contribute, and connect with the global Aetherra community. 
              Build the future of neural computing together.
            </p>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-2xl font-bold text-aetherra-green">7</div>
                <div className="text-sm text-gray-400">Plugins</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">1</div>
                <div className="text-sm text-gray-400">Developer</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">1</div>
                <div className="text-sm text-gray-400">Contributor</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">New</div>
                <div className="text-sm text-gray-400">Project</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-900 border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab, index) => (
              <motion.button
                key={tab.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-3 py-4 px-2 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-aetherra-green text-aetherra-green'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <div className="text-left">
                  <div className="font-medium">{tab.label}</div>
                  <div className="text-xs text-gray-500">{tab.description}</div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-4">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="h-[calc(100vh-200px)]"
        >
          {renderTabContent()}
        </motion.div>
      </div>

      {/* Footer Call-to-Action */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="bg-gradient-to-r from-aetherra-green/10 to-purple-600/10 border-t border-gray-700 mt-12"
      >
        <div className="max-w-7xl mx-auto px-4 py-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Shape the Future?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Whether you're building plugins, contributing code, or sharing ideas, 
            your voice matters in the Aetherra community.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => setActiveTab('submit')}
              className="px-8 py-3 bg-aetherra-green text-black rounded-lg font-medium hover:bg-green-400 transition-colors"
            >
              📤 Submit a Plugin
            </button>
            <button
              onClick={() => setActiveTab('contribute')}
              className="px-8 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-500 transition-colors"
            >
              🛠️ Start Contributing
            </button>
            <button
              onClick={() => setActiveTab('community')}
              className="px-8 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors"
            >
              👥 Join Community
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
