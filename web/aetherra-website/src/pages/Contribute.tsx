import { motion } from 'framer-motion';
import { useState } from 'react';
import { CommunityLinksPanel } from '../components/CommunityLinksPanel';
import { ContributionGuide } from '../components/ContributionGuide';
import ContributionPanel from '../components/ContributionPanel';
import { PluginSubmissionForm } from '../components/PluginSubmissionForm';

export default function Contribute() {
    const [activeTab, setActiveTab] = useState<'guide' | 'submit' | 'community'>('guide');

    return (
        <div className="p-6 space-y-8">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4">🛠️ Contribute to Aetherra</h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                    Join our mission to build the most advanced AI consciousness platform. Every contribution matters.
                </p>
            </div>

            {/* Tab Navigation */}
            <div className="flex justify-center mb-8">
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-2 flex flex-wrap justify-center">
                    <button
                        onClick={() => setActiveTab('guide')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors m-1 ${activeTab === 'guide'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-300 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        📚 Contribution Guide
                    </button>
                    <button
                        onClick={() => setActiveTab('submit')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors m-1 ${activeTab === 'submit'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-300 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        🚀 Submit Plugin
                    </button>
                    <button
                        onClick={() => setActiveTab('community')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors m-1 ${activeTab === 'community'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-300 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        🌐 Community Links
                    </button>
                </div>
            </div>

            {/* Tab Content */}
            <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
            >
                {activeTab === 'guide' && <ContributionGuide />}
                {activeTab === 'submit' && <PluginSubmissionForm />}
                {activeTab === 'community' && <CommunityLinksPanel />}
            </motion.div>

            {/* Original Contribution Panel */}
            {activeTab === 'guide' && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                >
                    <ContributionPanel />
                </motion.div>
            )}
        </div>
    );
}
