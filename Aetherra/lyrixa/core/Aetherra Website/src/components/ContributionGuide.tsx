import { motion } from 'framer-motion';
import { useState } from 'react';

interface ContributionGuideProps {
  onNavigateToSubmission?: () => void;
}

export default function ContributionGuide({ onNavigateToSubmission }: ContributionGuideProps) {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', title: '🌟 Overview', icon: '📋' },
    { id: 'getting-started', title: '🚀 Getting Started', icon: '🏃' },
    { id: 'development', title: '💻 Development', icon: '⚙️' },
    { id: 'plugins', title: '🔌 Plugin Development', icon: '🧩' },
    { id: 'ui-contributions', title: '🎨 UI Contributions', icon: '🖌️' },
    { id: 'documentation', title: '📚 Documentation', icon: '📖' },
    { id: 'community', title: '👥 Community', icon: '🤝' },
    { id: 'guidelines', title: '📝 Guidelines', icon: '📜' }
  ];

  const renderMarkdownContent = (section: string) => {
    switch (section) {
      case 'overview':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-aetherra-green mb-4">Welcome to Aetherra Development! 🌟</h2>
              <p className="text-gray-300 mb-4">
                Thank you for your interest in contributing to the Aetherra AI-Native Operating System!
                Whether you're a seasoned developer, UI designer, or AI enthusiast, there's a place for you in our community.
              </p>
            </div>

            <div className="bg-gradient-to-r from-aetherra-green/20 to-purple-600/20 rounded-lg p-6 border border-aetherra-green/30">
              <h3 className="text-xl font-semibold text-white mb-3">🎯 What We're Building</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• <strong>Neural-Native OS:</strong> The first operating system designed from the ground up for AI</li>
                <li>• <strong>Lyrixa Core:</strong> Advanced neural runtime for seamless AI integration</li>
                <li>• <strong>Plugin Ecosystem:</strong> Extensible architecture for community contributions</li>
                <li>• <strong>AetherScript:</strong> Neural-native programming language for AI workflows</li>
              </ul>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold text-aetherra-green mb-2">🔥 Quick Wins</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Fix typos in documentation</li>
                  <li>• Improve UI components</li>
                  <li>• Add new plugin examples</li>
                  <li>• Write tutorials</li>
                </ul>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold text-purple-400 mb-2">🚀 Major Features</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Neural network optimizations</li>
                  <li>• New plugin categories</li>
                  <li>• AI model integrations</li>
                  <li>• Performance improvements</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'getting-started':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">🚀 Getting Started</h2>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">Prerequisites</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-aetherra-green mb-2">Required Skills</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• JavaScript/TypeScript</li>
                    <li>• React & Modern Web APIs</li>
                    <li>• Git version control</li>
                    <li>• Basic AI/ML concepts</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-aetherra-green mb-2">Tools & Environment</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Node.js 18+ & npm</li>
                    <li>• VS Code (recommended)</li>
                    <li>• Git & GitHub account</li>
                    <li>• Chrome/Edge DevTools</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-aetherra-green">
              <h3 className="text-lg font-semibold text-white mb-3">⚡ Quick Setup</h3>
              <div className="bg-black rounded p-4 font-mono text-sm">
                <div className="text-aetherra-green"># Clone the repository</div>
                <div className="text-white">git clone https://github.com/Zyonic88/Aetherra.git</div>
                <div className="text-gray-500 mt-2"># Navigate to project</div>
                <div className="text-white">cd aetherra</div>
                <div className="text-gray-500 mt-2"># Install dependencies</div>
                <div className="text-white">npm install</div>
                <div className="text-gray-500 mt-2"># Start development server</div>
                <div className="text-white">npm run dev</div>
              </div>
            </div>

            <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
              <h4 className="font-semibold text-blue-300 mb-2">💡 First Contribution Tips</h4>
              <ul className="text-sm text-blue-200 space-y-1">
                <li>• Start with issues labeled "good first issue"</li>
                <li>• Read our code style guide before making changes</li>
                <li>• Test your changes thoroughly before submitting</li>
                <li>• Write clear commit messages and pull request descriptions</li>
              </ul>
            </div>
          </div>
        );

      case 'development':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">💻 Development Workflow</h2>

            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-3">🔄 Development Process</h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-aetherra-green text-black rounded-full flex items-center justify-center text-sm font-bold">1</span>
                    <div>
                      <h4 className="font-medium text-white">Fork & Clone</h4>
                      <p className="text-sm text-gray-400">Fork the repository and clone your fork locally</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-aetherra-green text-black rounded-full flex items-center justify-center text-sm font-bold">2</span>
                    <div>
                      <h4 className="font-medium text-white">Create Branch</h4>
                      <p className="text-sm text-gray-400">Create a feature branch: <code className="bg-gray-700 px-1 rounded">git checkout -b feature/amazing-feature</code></p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-aetherra-green text-black rounded-full flex items-center justify-center text-sm font-bold">3</span>
                    <div>
                      <h4 className="font-medium text-white">Develop & Test</h4>
                      <p className="text-sm text-gray-400">Make your changes and test thoroughly</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-aetherra-green text-black rounded-full flex items-center justify-center text-sm font-bold">4</span>
                    <div>
                      <h4 className="font-medium text-white">Submit PR</h4>
                      <p className="text-sm text-gray-400">Create a pull request with clear description</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-3">🧪 Testing</h3>
                <div className="bg-black rounded p-4 font-mono text-sm">
                  <div className="text-gray-500"># Run all tests</div>
                  <div className="text-white">npm test</div>
                  <div className="text-gray-500 mt-2"># Run linting</div>
                  <div className="text-white">npm run lint</div>
                  <div className="text-gray-500 mt-2"># Build production version</div>
                  <div className="text-white">npm run build</div>
                </div>
              </div>

              <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-300 mb-2">⚠️ Code Standards</h4>
                <ul className="text-sm text-yellow-200 space-y-1">
                  <li>• Follow TypeScript strict mode guidelines</li>
                  <li>• Use ESLint and Prettier for code formatting</li>
                  <li>• Write meaningful component and function names</li>
                  <li>• Add JSDoc comments for complex functions</li>
                  <li>• Keep components small and focused (Single Responsibility)</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'plugins':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">🔌 Plugin Development</h2>

            <div className="bg-gradient-to-r from-purple-600/20 to-aetherra-green/20 rounded-lg p-6 border border-purple-600/30">
              <h3 className="text-xl font-semibold text-white mb-3">Plugin Architecture</h3>
              <p className="text-gray-300 mb-4">
                Aetherra plugins are modular extensions that enhance the neural runtime with specialized capabilities.
                Each plugin follows a standard interface for seamless integration.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold text-aetherra-green mb-3">📦 Plugin Types</h4>
                <ul className="text-sm text-gray-300 space-y-2">
                  <li>• <strong>Core Extensions:</strong> System-level enhancements</li>
                  <li>• <strong>AI Models:</strong> Neural network integrations</li>
                  <li>• <strong>UI Components:</strong> Interface extensions</li>
                  <li>• <strong>Data Processors:</strong> Input/output handlers</li>
                  <li>• <strong>Visualizers:</strong> Data representation tools</li>
                </ul>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold text-purple-400 mb-3">🛠️ Development Tools</h4>
                <ul className="text-sm text-gray-300 space-y-2">
                  <li>• Plugin SDK & CLI tools</li>
                  <li>• TypeScript type definitions</li>
                  <li>• Testing framework integration</li>
                  <li>• Hot-reload development server</li>
                  <li>• Plugin marketplace submission</li>
                </ul>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-aetherra-green">
              <h3 className="text-lg font-semibold text-white mb-3">🚀 Plugin Template</h3>
              <div className="bg-black rounded p-4 font-mono text-sm">
                <div className="text-gray-500">// Basic plugin structure</div>
                <div className="text-aetherra-green">export class MyPlugin implements AetherPlugin {`{`}</div>
                <div className="text-white ml-4">name = "my-awesome-plugin";</div>
                <div className="text-white ml-4">version = "1.0.0";</div>
                <div className="text-white ml-4">category = "AI Enhancement";</div>
                <div className="text-white ml-4"></div>
                <div className="text-white ml-4">async initialize(runtime: LyrixaRuntime) {`{`}</div>
                <div className="text-gray-400 ml-8">// Plugin initialization logic</div>
                <div className="text-white ml-4">{`}`}</div>
                <div className="text-white ml-4"></div>
                <div className="text-white ml-4">async execute(params: any) {`{`}</div>
                <div className="text-gray-400 ml-8">// Main plugin functionality</div>
                <div className="text-white ml-4">{`}`}</div>
                <div className="text-aetherra-green">{`}`}</div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={onNavigateToSubmission}
                className="flex-1 bg-aetherra-green text-black py-3 px-4 rounded-lg font-medium hover:bg-green-400 transition-colors"
              >
                📤 Submit Your Plugin
              </button>
              <button className="px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors">
                📖 Plugin SDK Docs
              </button>
            </div>
          </div>
        );

      case 'ui-contributions':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">🎨 UI Contributions</h2>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">Design System</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium text-aetherra-green">Colors</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-aetherra-green rounded"></div>
                      <span className="text-gray-300">Primary: #00ff88</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-gray-900 rounded border border-gray-600"></div>
                      <span className="text-gray-300">Dark: #0a0a0a</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-aetherra-green">Typography</h4>
                  <div className="text-sm text-gray-300">
                    <div>Primary: JetBrains Mono</div>
                    <div>UI: Inter, system fonts</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-aetherra-green">Animations</h4>
                  <div className="text-sm text-gray-300">
                    <div>Framer Motion</div>
                    <div>Smooth, purposeful</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">🎯 UI Contribution Areas</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 🎨 Component library improvements</li>
                  <li>• 📱 Mobile responsiveness</li>
                  <li>• ♿ Accessibility enhancements</li>
                  <li>• 🌙 Dark/light theme refinements</li>
                </ul>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• ⚡ Performance optimizations</li>
                  <li>• 🎬 Animation improvements</li>
                  <li>• 🎪 Interactive demos</li>
                  <li>• 📊 Data visualization components</li>
                </ul>
              </div>
            </div>

            <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
              <h4 className="font-semibold text-blue-300 mb-2">📐 Design Guidelines</h4>
              <ul className="text-sm text-blue-200 space-y-1">
                <li>• Maintain neural/AI theme throughout interfaces</li>
                <li>• Use consistent spacing (4px grid system)</li>
                <li>• Follow accessibility best practices (WCAG 2.1)</li>
                <li>• Test across different screen sizes and devices</li>
                <li>• Keep animations smooth and purposeful (avoid overuse)</li>
              </ul>
            </div>
          </div>
        );

      case 'documentation':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">📚 Documentation</h2>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">Documentation Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-aetherra-green mb-2">📖 User Documentation</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Getting started guides</li>
                    <li>• Feature tutorials</li>
                    <li>• Plugin usage examples</li>
                    <li>• FAQ and troubleshooting</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-purple-400 mb-2">👨‍💻 Developer Documentation</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• API reference</li>
                    <li>• Architecture overview</li>
                    <li>• Code examples</li>
                    <li>• Plugin development guide</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-aetherra-green">
              <h3 className="text-lg font-semibold text-white mb-3">✏️ Writing Guidelines</h3>
              <div className="space-y-3 text-sm text-gray-300">
                <div>
                  <strong className="text-aetherra-green">Clear & Concise:</strong> Use simple language and short sentences. Avoid jargon when possible.
                </div>
                <div>
                  <strong className="text-aetherra-green">Code Examples:</strong> Include practical examples that users can copy and run.
                </div>
                <div>
                  <strong className="text-aetherra-green">Screenshots:</strong> Add visual aids for UI-related documentation.
                </div>
                <div>
                  <strong className="text-aetherra-green">Up-to-date:</strong> Ensure documentation matches current code behavior.
                </div>
              </div>
            </div>

            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-300 mb-2">📝 Documentation Tools</h4>
              <ul className="text-sm text-yellow-200 space-y-1">
                <li>• Markdown for all documentation files</li>
                <li>• JSDoc comments for TypeScript code</li>
                <li>• Storybook for component documentation</li>
                <li>• GitHub Wiki for extended guides</li>
              </ul>
            </div>
          </div>
        );

      case 'community':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">👥 Community</h2>

            <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg p-6 border border-blue-600/30">
              <h3 className="text-xl font-semibold text-white mb-3">Join Our Community</h3>
              <p className="text-gray-300 mb-4">
                Connect with fellow developers, AI researchers, and enthusiasts building the future of neural computing.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-3xl mb-2">💬</div>
                <h4 className="font-semibold text-white mb-2">Discord</h4>
                <p className="text-sm text-gray-400 mb-3">Real-time chat, voice channels, and community events</p>
                <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded transition-colors">
                  Join Discord
                </button>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-3xl mb-2">🐙</div>
                <h4 className="font-semibold text-white mb-2">GitHub</h4>
                <p className="text-sm text-gray-400 mb-3">Code repositories, issues, and pull requests</p>
                <button className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 rounded transition-colors">
                  View GitHub
                </button>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-3xl mb-2">🐦</div>
                <h4 className="font-semibold text-white mb-2">Twitter/X</h4>
                <p className="text-sm text-gray-400 mb-3">Updates, announcements, and tech discussions</p>
                <button className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded transition-colors">
                  Follow Us
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">🎯 Community Guidelines</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <div>• <strong>Be Respectful:</strong> Treat all community members with kindness and respect</div>
                <div>• <strong>Stay On Topic:</strong> Keep discussions relevant to Aetherra and AI development</div>
                <div>• <strong>Help Others:</strong> Share knowledge and assist fellow developers</div>
                <div>• <strong>Quality Contributions:</strong> Provide constructive feedback and well-researched suggestions</div>
                <div>• <strong>No Spam:</strong> Avoid promotional content and repeated messages</div>
              </div>
            </div>

            <div className="bg-green-900/30 border border-green-600 rounded-lg p-4">
              <h4 className="font-semibold text-green-300 mb-2">🏆 Recognition Program</h4>
              <p className="text-sm text-green-200 mb-2">
                We recognize outstanding contributors with:
              </p>
              <ul className="text-sm text-green-200 space-y-1">
                <li>• Contributor badges and profiles</li>
                <li>• Featured showcases of exceptional work</li>
                <li>• Early access to new features</li>
                <li>• Speaking opportunities at community events</li>
              </ul>
            </div>
          </div>
        );

      case 'guidelines':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-aetherra-green mb-4">📝 Guidelines</h2>

            <div className="bg-red-900/30 border border-red-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-300 mb-3">⚠️ Code of Conduct</h3>
              <div className="space-y-2 text-sm text-red-200">
                <div>• Harassment, discrimination, and toxic behavior are not tolerated</div>
                <div>• Respect intellectual property and licensing requirements</div>
                <div>• Report security vulnerabilities responsibly through proper channels</div>
                <div>• Follow all applicable laws and regulations</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">📋 Pull Request Guidelines</h3>
              <div className="space-y-3 text-sm text-gray-300">
                <div>
                  <strong className="text-aetherra-green">Title:</strong> Use descriptive titles (e.g., "Add neural optimization plugin for memory management")
                </div>
                <div>
                  <strong className="text-aetherra-green">Description:</strong> Explain what changes were made and why
                </div>
                <div>
                  <strong className="text-aetherra-green">Testing:</strong> Include test results and manual testing steps
                </div>
                <div>
                  <strong className="text-aetherra-green">Dependencies:</strong> List any new dependencies or breaking changes
                </div>
                <div>
                  <strong className="text-aetherra-green">Screenshots:</strong> Add before/after images for UI changes
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">🔍 Review Process</h3>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
                  <div>
                    <h4 className="font-medium text-white">Automated Checks</h4>
                    <p className="text-sm text-gray-400">CI/CD pipeline runs tests, linting, and builds</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                  <div>
                    <h4 className="font-medium text-white">Code Review</h4>
                    <p className="text-sm text-gray-400">Maintainers review code quality, architecture, and functionality</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                  <div>
                    <h4 className="font-medium text-white">Testing</h4>
                    <p className="text-sm text-gray-400">Manual testing in development and staging environments</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-aetherra-green text-black rounded-full flex items-center justify-center text-sm font-bold">✓</span>
                  <div>
                    <h4 className="font-medium text-white">Merge</h4>
                    <p className="text-sm text-gray-400">Approved changes are merged and deployed</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
              <h4 className="font-semibold text-blue-300 mb-2">📞 Getting Help</h4>
              <ul className="text-sm text-blue-200 space-y-1">
                <li>• Check existing issues and documentation first</li>
                <li>• Use GitHub Discussions for questions and ideas</li>
                <li>• Join our Discord for real-time help</li>
                <li>• Tag maintainers in GitHub for urgent issues</li>
              </ul>
            </div>
          </div>
        );

      default:
        return <div>Content not found</div>;
    }
  };

  return (
    <div className="h-full flex bg-gray-900 rounded-xl border border-gray-700">
      {/* Sidebar Navigation */}
      <div className="w-64 border-r border-gray-700 bg-gray-800 rounded-l-xl">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-lg font-bold text-aetherra-green">📚 Contribution Guide</h2>
        </div>
        <nav className="p-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full text-left p-3 rounded-lg mb-1 transition-colors ${activeSection === section.id
                  ? 'bg-aetherra-green text-black font-medium'
                  : 'text-gray-300 hover:bg-gray-700'
                }`}
            >
              <span className="mr-2">{section.icon}</span>
              {section.title}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {renderMarkdownContent(activeSection)}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
