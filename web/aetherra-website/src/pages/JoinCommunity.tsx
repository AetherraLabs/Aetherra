import communityData from '../data/community_activity.json';
import { CommunityActivity } from '../types';

export default function JoinCommunity() {
    const activities = communityData.activity as CommunityActivity[];

    const getActivityIcon = (type: string) => {
        switch (type) {
            case 'plugin_release': return '🚀';
            case 'contribution': return '💻';
            case 'discussion': return '💬';
            case 'bug_report': return '🐛';
            case 'documentation': return '📚';
            default: return '✨';
        }
    };

    const formatTimeAgo = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 24) {
            return `${diffInHours}h ago`;
        } else {
            const diffInDays = Math.floor(diffInHours / 24);
            return `${diffInDays}d ago`;
        }
    };

    return (
        <div className="p-6 space-y-8">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4">🌟 Join the Aetherra Community</h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                    Connect with developers, researchers, and AI enthusiasts building the future of consciousness simulation.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                        <h2 className="text-2xl font-semibold mb-4">🔥 Recent Community Activity</h2>

                        <div className="space-y-4">
                            {activities.map((activity, index) => (
                                <div key={index} className="flex items-start gap-3 p-4 bg-gray-700 rounded-lg">
                                    <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="font-semibold text-blue-400">@{activity.user}</span>
                                            <span className="text-gray-300">{activity.action}</span>
                                            <span className="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</span>
                                        </div>
                                        <p className="text-sm text-gray-400">{activity.details}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                        <h2 className="text-2xl font-semibold mb-4">📊 Community Stats</h2>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center p-4 bg-gray-700 rounded-lg">
                                <div className="text-2xl font-bold text-blue-400">47</div>
                                <div className="text-sm text-gray-400">Contributors</div>
                            </div>
                            <div className="text-center p-4 bg-gray-700 rounded-lg">
                                <div className="text-2xl font-bold text-green-400">12</div>
                                <div className="text-sm text-gray-400">Active Plugins</div>
                            </div>
                            <div className="text-center p-4 bg-gray-700 rounded-lg">
                                <div className="text-2xl font-bold text-purple-400">234</div>
                                <div className="text-sm text-gray-400">Discord Members</div>
                            </div>
                            <div className="text-center p-4 bg-gray-700 rounded-lg">
                                <div className="text-2xl font-bold text-orange-400">1.2k</div>
                                <div className="text-sm text-gray-400">GitHub Stars</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-gradient-to-b from-blue-900 to-blue-800 p-6 rounded-xl shadow-lg">
                        <h3 className="text-xl font-semibold mb-4">💬 Join our Discord</h3>
                        <p className="text-sm text-gray-200 mb-4">
                            Connect with the community in real-time. Get help, share ideas, and collaborate on projects.
                        </p>
                        <a
                            href="https://discord.gg/aetherra"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full bg-white text-blue-900 text-center py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                        >
                            Join Discord Server
                        </a>
                        <div className="mt-3 text-xs text-gray-300">
                            234 members • 23 online now
                        </div>
                    </div>

                    <div className="bg-gradient-to-b from-gray-900 to-gray-800 p-6 rounded-xl shadow-lg">
                        <h3 className="text-xl font-semibold mb-4">🐙 GitHub Repository</h3>
                        <p className="text-sm text-gray-200 mb-4">
                            Explore the source code, report issues, and contribute to the project.
                        </p>
                        <a
                            href="https://github.com/AetherraLabs/Aetherra"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full bg-white text-gray-900 text-center py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                        >
                            View on GitHub
                        </a>
                        <div className="mt-3 text-xs text-gray-300">
                            1.2k stars • 89 forks • MIT License
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                        <h3 className="text-xl font-semibold mb-4">📧 Newsletter</h3>
                        <p className="text-sm text-gray-300 mb-4">
                            Stay updated with the latest developments and releases.
                        </p>
                        <div className="space-y-2">
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded transition-colors">
                                Subscribe
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                <h2 className="text-2xl font-semibold mb-4">🎯 Ways to Get Involved</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">🔧</div>
                        <h3 className="font-semibold mb-2">Develop Plugins</h3>
                        <p className="text-sm text-gray-300">
                            Create plugins to extend Lyrixa's capabilities and share them with the community.
                        </p>
                    </div>

                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">🐛</div>
                        <h3 className="font-semibold mb-2">Test & Report</h3>
                        <p className="text-sm text-gray-300">
                            Help us improve by testing new features and reporting bugs you encounter.
                        </p>
                    </div>

                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">📚</div>
                        <h3 className="font-semibold mb-2">Write Documentation</h3>
                        <p className="text-sm text-gray-300">
                            Contribute to our docs, write tutorials, or create educational content.
                        </p>
                    </div>

                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">💡</div>
                        <h3 className="font-semibold mb-2">Share Ideas</h3>
                        <p className="text-sm text-gray-300">
                            Propose new features, improvements, or research directions for the project.
                        </p>
                    </div>

                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">🎨</div>
                        <h3 className="font-semibold mb-2">Design & UX</h3>
                        <p className="text-sm text-gray-300">
                            Help improve the user interface and experience of Aetherra's tools.
                        </p>
                    </div>

                    <div className="text-center p-4">
                        <div className="text-4xl mb-3">🗣️</div>
                        <h3 className="font-semibold mb-2">Spread the Word</h3>
                        <p className="text-sm text-gray-300">
                            Share Aetherra with others who might be interested in AI consciousness research.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
