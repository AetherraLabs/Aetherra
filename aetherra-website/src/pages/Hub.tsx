import PluginCarousel from "../components/PluginCarousel";

export default function Hub() {
    return (
        <div className="max-w-6xl mx-auto px-6 py-16">
            <div className="text-center mb-12">
                <h1 className="text-display font-display text-aetherra-text-primary mb-4">
                    Plugin Ecosystem
                </h1>
                <p className="text-lg text-aetherra-text-secondary">
                    Composable cognitive capabilities with safety guarantees
                </p>
            </div>

            {/* Featured Plugins */}
            <section className="mb-16">
                <h2 className="text-display font-display text-aetherra-text-primary mb-8">
                    Featured Plugins
                </h2>
                <PluginCarousel />
            </section>

            {/* Plugin Categories */}
            <section className="mb-16">
                <h2 className="text-display font-display text-aetherra-text-primary mb-8">
                    Categories
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Memory & Storage
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Advanced memory management, persistence, and retrieval systems.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            12 plugins available
                        </div>
                    </div>

                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Natural Language
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Text processing, understanding, and generation capabilities.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            8 plugins available
                        </div>
                    </div>

                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Decision Making
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Logic, reasoning, and automated decision frameworks.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            6 plugins available
                        </div>
                    </div>

                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Sensory Input
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Vision, audio, and multimodal input processing systems.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            10 plugins available
                        </div>
                    </div>

                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Task Automation
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Workflow orchestration and automated task execution.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            15 plugins available
                        </div>
                    </div>

                    <div className="card-lab p-6">
                        <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                            Developer Tools
                        </h3>
                        <p className="text-aetherra-text-secondary mb-4">
                            Debugging, monitoring, and development utilities.
                        </p>
                        <div className="text-caption text-aetherra-text-tertiary">
                            9 plugins available
                        </div>
                    </div>
                </div>
            </section>

            {/* Plugin Development */}
            <section className="card-lab p-8 text-center">
                <h2 className="text-display font-display text-aetherra-text-primary mb-4">
                    Build Your Own Plugin
                </h2>
                <p className="text-lg text-aetherra-text-secondary mb-8 max-w-2xl mx-auto">
                    Extend Aetherra's cognitive capabilities with custom plugins.
                    Our framework provides safety guarantees and seamless integration.
                </p>

                <div className="flex flex-wrap gap-4 items-center justify-center">
                    <a href="/docs#plugin-api" className="btn-primary">
                        View Plugin API
                    </a>
                    <a href="https://github.com/AetherraLabs/plugin-examples" className="btn-secondary">
                        Example Plugins
                    </a>
                    <a href="/docs#quickstart" className="btn-ghost">
                        5-Minute Quickstart
                    </a>
                </div>
            </section>

            {/* Manifest & Registration */}
            <section className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card-lab p-6 text-left">
                    <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                        Manifest Schema (minimum)
                    </h3>
                    <div className="rounded-lg bg-black/40 border border-white/10 p-3 text-sm text-left">
                        {`{
  "name": "your-plugin",
  "version": "1.0.0",
  "entry_point": "main.py",
  "dependencies": []
}`}
                    </div>
                    <p className="text-caption text-aetherra-text-tertiary mt-3">
                        Dependencies must be an array of strings. Additional metadata supported.
                    </p>
                </div>
                <div className="card-lab p-6 text-left">
                    <h3 className="text-headline font-display text-aetherra-text-primary mb-3">
                        Registration API
                    </h3>
                    <div className="rounded-lg bg-black/40 border border-white/10 p-3 text-sm">
                        <div><span className="text-aetherra-text-tertiary">GET</span> <code className="text-aether">/api/plugins</code></div>
                        <div><span className="text-aetherra-text-tertiary">POST</span> <code className="text-aether">/api/plugins/register</code></div>
                    </div>
                    <p className="text-caption text-aetherra-text-tertiary mt-3">
                        In strict mode, signatures are validated. See Signing & Trust below.
                    </p>
                </div>
            </section>

            {/* Signing & Trust */}
            <section className="mt-6 card-lab p-6 text-left">
                <h3 className="text-headline font-display text-aetherra-text-primary mb-3">Signing & Trust</h3>
                <ul className="list-disc pl-6 text-aetherra-text-secondary text-sm space-y-1">
                    <li>Strict signing can be enabled via environment flags.</li>
                    <li>When enabled, manifests require a valid signature and public key.</li>
                    <li>Trust zones are computed based on signature verification status.</li>
                </ul>
            </section>
        </div>
    );
}
