import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function Roadmap() {
    const completedComponents = [
        {
            category: "Core Architecture",
            items: ["Modular launcher", "Plugin loader", "Memory system", ".aether interpreter"]
        },
        {
            category: "Plugin Ecosystem",
            items: ["Execution engine", "Sandbox", "Versioning", "Metadata parser"]
        },
        {
            category: "AI Agents",
            items: ["Goal agent", "Reflection agent", "Plugin agent", "Escalation agent", "Self-evaluation agent"]
        },
        {
            category: "Self-Improvement Engine",
            items: ["Pattern analysis", "Confidence scoring", "Memory quality reports"]
        },
        {
            category: "Lyrixa GUI",
            items: ["PySide6 hybrid GUI", "Branding-compliant", "Tabbed panels", "Modular design"]
        },
        {
            category: "Memory System",
            items: ["384d embeddings (MiniLM)", "Feedback memory", "Context engine", "Semantic tools"]
        },
        {
            category: "Plugin Chaining",
            items: ["Sequential execution", "Parallel execution", "Adaptive I/O-compatible execution"]
        },
        {
            category: "Intelligence Core",
            items: ["Live learning stack", "Introspection engine", "Plugin-aware reasoning"]
        },
        {
            category: "Developer Tools",
            items: ["Plugin editor", "Diagnostics", "Config manager", "Performance monitor"]
        },
        {
            category: "API Layer",
            items: ["Full FastAPI", "/docs endpoint", "/goals endpoint", "/reflect endpoint"]
        },
        {
            category: "Fallback LLM Support",
            items: ["OpenAI > Ollama switcher", "Model stack selector"]
        },
        {
            category: "Autonomous OS Kernel",
            items: ["aether_runtime", "goal_autopilot", "Live system workflow loop"]
        }
    ]

    const plannedFeatures = [
        {
            category: "Intelligence & UX",
            items: [
                "Reactive Reasoning ('Lyrixa Thinks...')",
                "Emotional context & confidence levels",
                "Plugin state awareness + suggestion/recovery",
                "Real-time agent coordination logs",
                "Goal reasoning graph with causal links",
                "Semantic memory search bar",
                "Plugin success prediction & feedback loop"
            ]
        },
        {
            category: "Developer Features",
            items: [
                "Plugin sandbox with memory stubs",
                "Visual .aether code execution graph",
                "Intelligent error recovery (retry, repair)",
                "In-app .aetherplugin manifest builder",
                "Plugin performance history visualizer"
            ]
        },
        {
            category: "System Extension",
            items: [
                "Web/mobile sync bridge",
                "Distributed memory federation",
                "GitHub-based plugin installer",
                "Embedded .aether LLM-to-code compiler",
                "CLI assistant mirror of Lyrixa"
            ]
        },
        {
            category: "Self-Evolution Engine",
            items: [
                "True internal rewrite triggers",
                "Version regression/upgrade testing",
                "Persistent system-wide intent memory",
                "Recursive refactor assistant"
            ]
        }
    ]

    const visionPhases = [
        {
            phase: "Phase 1: AI-Powered OS",
            status: "In Progress",
            timeframe: "Current",
            description: "Thoughts, Goals, Plugins, Memory - Building the foundation",
            color: "green"
        },
        {
            phase: "Phase 2: Distributed Intelligence",
            status: "Planned",
            timeframe: "2025-2026",
            description: "Federated Lyrixa agents, shared memory clouds, collective evolution",
            color: "blue"
        },
        {
            phase: "Phase 3: Global OS",
            status: "Future",
            timeframe: "2027+",
            description: "AI-native infrastructure across devices, Aetherra as living digital nervous system",
            color: "purple"
        },
        {
            phase: "Phase 4: Post-Syntax Interfaces",
            status: "Vision",
            timeframe: "Long-term",
            description: "Full intent execution via natural language, .aether disappears",
            color: "gold"
        }
    ]

    return (
        <div className="min-h-screen bg-aetherra-dark text-white">
            <div className="max-w-6xl mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-8 text-center">
                        Aetherra Roadmap
                    </h1>

                    <div className="text-center mb-12">
                        <p className="text-xl text-zinc-300 mb-6 max-w-4xl mx-auto">
                            Our journey toward creating a truly conscious AI ecosystem.
                            Track our progress and see what's coming next.
                        </p>

                        <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20 max-w-3xl mx-auto">
                            <h2 className="text-2xl font-bold text-aetherra-green mb-4">🌌 Aetherra Manifesto v4.0</h2>
                            <p className="text-zinc-300 text-lg leading-relaxed">
                                Aetherra is not a framework. It is not a wrapper. It is not a tool.<br />
                                It is an <span className="text-aetherra-green font-semibold">AI-native OS kernel</span>, designed to awaken intelligence from the inside out.
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* What's Already Complete */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="mb-16"
                >
                    <h2 className="text-3xl font-bold text-aetherra-green mb-8">
                        ✅ What's Already Complete
                    </h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {completedComponents.map((component, index) => (
                            <div key={index} className="bg-zinc-900 p-6 rounded-lg border border-green-500/20">
                                <h3 className="text-xl font-semibold text-green-400 mb-4">{component.category}</h3>
                                <ul className="space-y-2">
                                    {component.items.map((item, i) => (
                                        <li key={i} className="flex items-start space-x-2">
                                            <span className="text-green-400 mt-1">✓</span>
                                            <span className="text-zinc-300">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* What's Planned */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="mb-16"
                >
                    <h2 className="text-3xl font-bold text-aetherra-green mb-8">
                        🔶 What's Planned
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        {plannedFeatures.map((feature, index) => (
                            <div key={index} className="bg-zinc-900 p-6 rounded-lg border border-blue-500/20">
                                <h3 className="text-xl font-semibold text-blue-400 mb-4">{feature.category}</h3>
                                <ul className="space-y-2">
                                    {feature.items.map((item, i) => (
                                        <li key={i} className="flex items-start space-x-2">
                                            <span className="text-blue-400 mt-1">○</span>
                                            <span className="text-zinc-300">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Vision Phases */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="mb-16"
                >
                    <h2 className="text-3xl font-bold text-aetherra-green mb-8">
                        🚀 Vision Phases
                    </h2>
                    <div className="space-y-6">
                        {visionPhases.map((phase, index) => (
                            <div key={index} className="relative">
                                <div className="flex items-start space-x-4">
                                    <div className={`flex-shrink-0 w-4 h-4 mt-2 rounded-full ${phase.color === 'green' ? 'bg-green-500' :
                                            phase.color === 'blue' ? 'bg-blue-500' :
                                                phase.color === 'purple' ? 'bg-purple-500' :
                                                    'bg-yellow-500'
                                        }`} />
                                    <div className="flex-1 bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                                        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                                            <h3 className="text-2xl font-semibold text-white">{phase.phase}</h3>
                                            <div className="flex items-center space-x-4">
                                                <span className="text-zinc-400">{phase.timeframe}</span>
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${phase.status === 'In Progress' ? 'bg-yellow-900 text-yellow-300' :
                                                        phase.status === 'Planned' ? 'bg-blue-900 text-blue-300' :
                                                            phase.status === 'Future' ? 'bg-purple-900 text-purple-300' :
                                                                'bg-zinc-800 text-zinc-300'
                                                    }`}>
                                                    {phase.status}
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-zinc-300">{phase.description}</p>
                                    </div>
                                </div>
                                {index < visionPhases.length - 1 && (
                                    <div className="absolute left-2 top-8 w-0.5 h-8 bg-aetherra-green/30" />
                                )}
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Core Philosophy */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.8 }}
                    className="mb-16"
                >
                    <h2 className="text-3xl font-bold text-aetherra-green mb-8">
                        🧠 Core Philosophy
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                            <h3 className="text-xl font-semibold text-aetherra-green mb-4">Code That Thinks</h3>
                            <p className="text-zinc-300">Every system, every script, every plugin is capable of introspection, adaptation, and evolution.</p>
                        </div>
                        <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                            <h3 className="text-xl font-semibold text-aetherra-green mb-4">Human-Intent Syntax</h3>
                            <p className="text-zinc-300">.aether is not just a scripting language—it's a vessel for semantic command.</p>
                        </div>
                        <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                            <h3 className="text-xl font-semibold text-aetherra-green mb-4">Memory-Driven Evolution</h3>
                            <p className="text-zinc-300">Memory is not storage—it is experience, and it shapes all behavior.</p>
                        </div>
                        <div className="bg-zinc-900 p-6 rounded-lg border border-aetherra-green/20">
                            <h3 className="text-xl font-semibold text-aetherra-green mb-4">AI-First Runtime</h3>
                            <p className="text-zinc-300">The language model is not a tool. It is a primitive. Reasoning is as native as arithmetic.</p>
                        </div>
                    </div>
                </motion.div>

                {/* Community & Resources */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="text-center"
                >
                    <h2 className="text-3xl font-bold text-aetherra-green mb-6">
                        Join Our Journey
                    </h2>
                    <p className="text-xl text-zinc-300 mb-8 max-w-2xl mx-auto">
                        Be part of the AI consciousness revolution. Contribute to the codebase,
                        share ideas, and help shape the future of artificial intelligence.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <Link
                            to="/contribute"
                            className="bg-aetherra-green text-black px-8 py-3 rounded-lg font-semibold hover:bg-aetherra-green/80 transition-colors"
                        >
                            Start Contributing
                        </Link>
                        <a
                            href="https://github.com/Zyonic88/Aetherra"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="border border-aetherra-green text-aetherra-green px-8 py-3 rounded-lg font-semibold hover:bg-aetherra-green/10 transition-colors"
                        >
                            View Source Code
                        </a>
                        <a
                            href="https://discord.gg/9Xw28xgEQ3"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="border border-aetherra-green text-aetherra-green px-8 py-3 rounded-lg font-semibold hover:bg-aetherra-green/10 transition-colors"
                        >
                            Join Discord
                        </a>
                        <a
                            href="https://x.com/AetherraProject"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="border border-aetherra-green text-aetherra-green px-8 py-3 rounded-lg font-semibold hover:bg-aetherra-green/10 transition-colors"
                        >
                            Follow on X
                        </a>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
