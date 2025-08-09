export default function ContributionPanel() {
    return (
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold mb-4">🚀 Join the Aetherra Community</h2>

            <p className="text-gray-200 mb-6">
                Help build the future of AI consciousness. Contribute code, ideas, and insights to the Aetherra project.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a
                    href="https://github.com/AetherraLabs/Aetherra"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-800 hover:bg-gray-700 p-4 rounded-lg transition-colors text-center"
                >
                    <div className="text-3xl mb-2">🐙</div>
                    <h3 className="font-semibold mb-1">GitHub</h3>
                    <p className="text-sm text-gray-300">Contribute code and report issues</p>
                </a>

                <a
                    href="https://discord.gg/aetherra"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-800 hover:bg-gray-700 p-4 rounded-lg transition-colors text-center"
                >
                    <div className="text-3xl mb-2">💬</div>
                    <h3 className="font-semibold mb-1">Discord</h3>
                    <p className="text-sm text-gray-300">Chat with developers and users</p>
                </a>

                <a
                    href="/contribute"
                    className="bg-gray-800 hover:bg-gray-700 p-4 rounded-lg transition-colors text-center"
                >
                    <div className="text-3xl mb-2">📚</div>
                    <h3 className="font-semibold mb-1">Docs</h3>
                    <p className="text-sm text-gray-300">Learn how to contribute</p>
                </a>
            </div>

            <div className="mt-6 bg-gray-800 bg-opacity-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">🎯 Current Needs</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Plugin developers for new integrations</li>
                    <li>• UI/UX designers for interface improvements</li>
                    <li>• Documentation writers for guides and tutorials</li>
                    <li>• Beta testers for experimental features</li>
                </ul>
            </div>
        </div>
    );
}
