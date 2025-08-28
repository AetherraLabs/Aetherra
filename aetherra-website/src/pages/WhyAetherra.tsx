import { motion } from 'framer-motion';

export default function WhyAetherra() {
    return (
        <div className="mx-auto max-w-4xl px-6 py-16">
            <header className="text-center mb-10">
                <h1 className="text-3xl md:text-4xl font-bold">How Aetherra is Different from Other AI</h1>
                <p className="mt-2 text-neutral-300">Aetherra is an AI-native Operating System — a living foundation for intelligence.</p>
            </header>

            <section className="prose prose-invert max-w-none">
                <p>Artificial Intelligence is everywhere today. From chatbots to coding assistants, most systems people interact with are built on <strong>large language models (LLMs)</strong> like ChatGPT, Claude, Gemini, and others. These tools are impressive — but they all share the same fundamental limitations.</p>
                <p><strong>Aetherra is different.</strong> It is not just another model or assistant. It is the <strong>world’s first validated AI-native Operating System</strong> — designed to think, learn, and evolve.</p>
            </section>

            <hr className="my-8 border-white/10" />

            <section>
                <h2 className="text-2xl font-bold">How Most AI Systems Work</h2>
                <ul className="mt-3 list-disc pl-6 text-neutral-300 space-y-1">
                    <li><strong>Pattern Prediction:</strong> Trained on massive datasets of text, these systems generate answers by predicting the most likely sequence of words.</li>
                    <li><strong>Static Knowledge:</strong> Knowledge is frozen at train time. No continuous learning by default.</li>
                    <li><strong>Short-Term Context:</strong> Context persists within a session, not across time.</li>
                    <li><strong>Reactive Only:</strong> They respond to prompts; they don’t set goals or improve themselves autonomously.</li>
                </ul>
                <p className="mt-3 text-neutral-300">These limitations make most AI tools useful assistants — but not true <strong>operating systems for intelligence</strong>.</p>
            </section>

            <hr className="my-8 border-white/10" />

            <section>
                <h2 className="text-2xl font-bold">How Aetherra is Different</h2>
                <p className="mt-2 text-neutral-300">Aetherra was built from the ground up to be an <strong>AI-native OS</strong>. It doesn’t just generate answers — it <strong>thinks, remembers, reflects, and grows</strong>.</p>

                <div className="mt-6 grid gap-4 md:grid-cols-2">
                    <motion.div initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🧠</span>
                            <div className="font-mono text-aether">Continuous Memory</div>
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">Stores experiences, reflections, and knowledge as living memories using <strong>QFAC</strong>, preserving meaning and causality across time; learns continuously.</p>
                    </motion.div>
                    <motion.div initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🎯</span>
                            <div className="font-mono text-aether">Goal-Oriented Intelligence</div>
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">Works toward long-term goals, coordinating specialized agents and plugins; plans, executes, and refines complex tasks.</p>
                    </motion.div>
                    <motion.div initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🌙</span>
                            <div className="font-mono text-aether">Self-Improvement Cycles</div>
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">Nightly reflection cycles consolidate memory, rewrite weak reasoning, and evolve behavior — Aetherra gets smarter over time.</p>
                    </motion.div>
                    <motion.div initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🧭</span>
                            <div className="font-mono text-aether">Ethics & Alignment</div>
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">Tracks decisions against multiple ethical frameworks, mitigates bias, and maintains alignment with core values.</p>
                    </motion.div>
                </div>
            </section>

            <section className="mt-8 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <div className="font-mono text-aether">Open and Validated</div>
                <ul className="mt-2 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                    <li>Open-source and community-driven.</li>
                    <li>Validated through <strong>213 test cases</strong> with a <strong>97.2% success rate</strong> across subsystems.</li>
                    <li>A foundational layer — like Linux for computing, Aetherra for intelligent systems.</li>
                </ul>
            </section>

            <section className="mt-8">
                <h2 className="text-2xl font-bold">In Short</h2>
                <ul className="mt-3 list-disc pl-6 text-neutral-300 space-y-1">
                    <li><strong>Other AI systems:</strong> reactive tools trained on static data, without memory or self-evolution.</li>
                    <li><strong>Aetherra:</strong> a living operating system that remembers, reflects, learns, and grows.</li>
                </ul>
                <blockquote className="mt-4 border-l-2 border-aether pl-4 text-neutral-200">Aetherra isn’t just an assistant. It’s the foundation for a new era of intelligent computing.</blockquote>
            </section>

            <footer className="mt-10 text-center text-sm text-neutral-400">
                <div>🌐 Learn more at <a className="underline decoration-aether/60" href="https://aetherra.dev">aetherra.dev</a></div>
                <div>💻 Explore the code on <a className="underline decoration-aether/60" href="https://github.com/AetherraLabs/Aetherra">GitHub</a></div>
            </footer>
        </div>
    );
}
