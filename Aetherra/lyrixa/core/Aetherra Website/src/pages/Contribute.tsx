import { motion } from 'framer-motion';

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

export default function Contribute() {
  return (
    <div className="min-h-screen bg-aetherra-dark text-white">
      {/* Hero Section */}
      <motion.section
        className="bg-gradient-to-br from-aetherra-dark via-aetherra-gray to-aetherra-dark border-b border-aetherra-green/20 py-16"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-6">
            🚀 Contribute to Aetherra
          </h1>
          <p className="text-xl text-zinc-300 mb-8">
            Help build the future of AI-native computing. Your contributions shape the next generation of intelligent systems.
          </p>
        </div>
      </motion.section>

      {/* Main Content */}
      <motion.main
        className="max-w-4xl mx-auto px-6 py-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Getting Started */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Getting Started</h2>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20">
              <div className="text-3xl mb-4">👨‍💻</div>
              <h3 className="text-xl font-semibold mb-3">Code Contributions</h3>
              <p className="text-zinc-400 mb-4">
                Improve core functionality, fix bugs, and implement new features.
              </p>
              <ul className="space-y-2 text-sm text-zinc-300">
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-aetherra-green rounded-full"></span>
                  <span>Fork the repository on GitHub</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-aetherra-green rounded-full"></span>
                  <span>Create a feature branch</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-aetherra-green rounded-full"></span>
                  <span>Submit a pull request</span>
                </li>
              </ul>
            </div>

            <div className="bg-aetherra-gray p-6 rounded-xl border border-blue-500/20">
              <div className="text-3xl mb-4">🔧</div>
              <h3 className="text-xl font-semibold mb-3">Plugin Development</h3>
              <p className="text-zinc-400 mb-4">
                Create plugins that extend Aetherra's capabilities and share them with the community.
              </p>
              <ul className="space-y-2 text-sm text-zinc-300">
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                  <span>Use the Plugin SDK</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                  <span>Follow best practices</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                  <span>Submit to AetherHub</span>
                </li>
              </ul>
            </div>
          </div>
        </motion.section>

        {/* Development Workflow */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Development Workflow</h2>

          <div className="bg-aetherra-gray p-8 rounded-xl border border-aetherra-green/20">
            <div className="space-y-8">
              {/* Step 1 */}
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-aetherra-green rounded-full flex items-center justify-center text-aetherra-dark font-bold text-sm">
                  1
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Setup Development Environment</h3>
                  <div className="bg-aetherra-dark p-4 rounded-lg font-mono text-sm mb-3">
                    <div className="text-zinc-500"># Clone the repository</div>
                    <div className="text-aetherra-green">git clone https://github.com/Zyonic88/Aetherra.git</div>
                    <div className="text-zinc-500 mt-2"># Install dependencies</div>
                    <div className="text-aetherra-green">cd aetherra && npm install</div>
                    <div className="text-zinc-500 mt-2"># Start development server</div>
                    <div className="text-aetherra-green">npm run dev</div>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-blue-400 rounded-full flex items-center justify-center text-aetherra-dark font-bold text-sm">
                  2
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Create Your Plugin</h3>
                  <div className="bg-aetherra-dark p-4 rounded-lg font-mono text-sm mb-3">
                    <div className="text-zinc-500"># Generate plugin template</div>
                    <div className="text-blue-400">aetherra create-plugin my-awesome-plugin</div>
                    <div className="text-zinc-500 mt-2"># Edit plugin metadata</div>
                    <div className="text-blue-400">nano src/plugin.json</div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-purple-400 rounded-full flex items-center justify-center text-aetherra-dark font-bold text-sm">
                  3
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Test and Validate</h3>
                  <div className="bg-aetherra-dark p-4 rounded-lg font-mono text-sm mb-3">
                    <div className="text-zinc-500"># Run tests</div>
                    <div className="text-purple-400">npm test</div>
                    <div className="text-zinc-500 mt-2"># Validate plugin structure</div>
                    <div className="text-purple-400">aetherra validate-plugin</div>
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center text-aetherra-dark font-bold text-sm">
                  4
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Submit for Review</h3>
                  <div className="bg-aetherra-dark p-4 rounded-lg font-mono text-sm mb-3">
                    <div className="text-zinc-500"># Create pull request</div>
                    <div className="text-yellow-400">gh pr create --title "Add: My Awesome Plugin"</div>
                    <div className="text-zinc-500 mt-2"># Or submit to marketplace</div>
                    <div className="text-yellow-400">aetherra submit-plugin</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Code Examples */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Plugin Example</h2>

          <div className="bg-aetherra-gray p-6 rounded-xl border border-aetherra-green/20">
            <h3 className="text-lg font-semibold mb-4">Basic Plugin Structure</h3>
            <div className="bg-aetherra-dark p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <div className="text-zinc-500">// plugin.json</div>
              <div className="text-white">{`{
  "name": "example-plugin",
  "version": "1.0.0",
  "description": "An example plugin for Aetherra",
  "author": "Your Name",
  "category": "utility",
  "entry": "index.js",
  "permissions": ["memory.read", "network.request"]
}`}</div>

              <div className="text-zinc-500 mt-6">// index.js</div>
              <div className="text-white">{`class ExamplePlugin {
  constructor(aetherra) {
    this.aetherra = aetherra;
  }

  async initialize() {
    console.log('Example plugin initialized');

    // Register event handlers
    this.aetherra.on('message', this.handleMessage);
  }

  handleMessage = (message) => {
    // Process incoming messages
    if (message.content.includes('example')) {
      return {
        response: 'Example plugin activated!',
        confidence: 0.8
      };
    }
  }

  async cleanup() {
    this.aetherra.off('message', this.handleMessage);
  }
}

module.exports = ExamplePlugin;`}</div>
            </div>
          </div>
        </motion.section>

        {/* Resources */}
        <motion.section variants={itemVariants} className="mb-16">
          <h2 className="text-3xl font-bold gradient-text mb-8">Resources & Documentation</h2>

          <div className="grid md:grid-cols-2 gap-6">
            <motion.a
              href="https://github.com/Zyonic88/Aetherra"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.02 }}
              className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700 hover:border-aetherra-green/50 transition-all block"
            >
              <div className="text-2xl mb-3">📚</div>
              <h3 className="text-lg font-semibold mb-2">Plugin SDK Documentation</h3>
              <p className="text-zinc-400 text-sm">
                Complete API reference and development guides
              </p>
            </motion.a>

            <motion.a
              href="https://github.com/Zyonic88/Aetherra"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.02 }}
              className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700 hover:border-blue-500/50 transition-all block"
            >
              <div className="text-2xl mb-3">🔧</div>
              <h3 className="text-lg font-semibold mb-2">Example Plugins</h3>
              <p className="text-zinc-400 text-sm">
                Browse real plugin implementations and templates
              </p>
            </motion.a>

            <motion.a
              href="https://discord.gg/9Xw28xgEQ3"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.02 }}
              className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700 hover:border-purple-500/50 transition-all block"
            >
              <div className="text-2xl mb-3">💬</div>
              <h3 className="text-lg font-semibold mb-2">Community Support</h3>
              <p className="text-zinc-400 text-sm">
                Get help from developers and share your progress
              </p>
            </motion.a>

            <motion.a
              href="https://github.com/Zyonic88/Aetherra/issues"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.02 }}
              className="bg-aetherra-gray p-6 rounded-xl border border-zinc-700 hover:border-red-500/50 transition-all block"
            >
              <div className="text-2xl mb-3">🐛</div>
              <h3 className="text-lg font-semibold mb-2">Issue Tracker</h3>
              <p className="text-zinc-400 text-sm">
                Report bugs and request new features
              </p>
            </motion.a>
          </div>
        </motion.section>

        {/* Call to Action */}
        <motion.section variants={itemVariants}>
          <div className="bg-gradient-to-r from-aetherra-green/20 to-blue-500/20 p-8 rounded-xl border border-aetherra-green/30 text-center">
            <h2 className="text-2xl font-bold gradient-text mb-4">
              Ready to Start Contributing?
            </h2>
            <p className="text-zinc-300 mb-6">
              Join thousands of developers building the future of AI-native computing
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-aetherra-green text-aetherra-dark rounded-lg font-semibold hover:bg-aetherra-green/90 transition-colors"
              >
                🚀 Start Contributing
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 transition-colors"
              >
                📖 Read Documentation
              </motion.button>
            </div>
          </div>
        </motion.section>
      </motion.main>
    </div>
  );
}
