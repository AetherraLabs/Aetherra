import { motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import usePRM from "../hooks/usePrefersReducedMotion";

type Feature = { title: string; desc: string; meta?: string };

const FEATURES: Feature[] = [
    { title: "Live Reasoning — “Lyrixa Thinks”", desc: "Real-time thought stream with goal/plan/reflect cycles and traceable steps." },
    { title: "Memory + QFAC", desc: "Quantum Fractal Adaptive Compression with episodic recall, narrative threads, and fidelity scoring.", meta: "Target: <100ms memory ops" },
    { title: "Anticipation Engine", desc: "Predicts next steps, suggests actions, and preloads context to reduce latency." },
    { title: "Plugin Chaining", desc: "Sequential/parallel/adaptive chains with I/O type compatibility and confidence-aware routing." },
    { title: "Safety & Ethics Trace", desc: "Decision traces with rollback, bias checks, value alignment scoring and auditability." },
    { title: "Model Router", desc: "Task-aware model selection (reasoning vs. speed vs. cost) with graceful fallbacks." },
];

const THOUGHT_SEEDS = [
    "Scanning plugin graph… found 3 eligible chains",
    "Goal updated: consolidate memory traces → narrative summary",
    "Confidence low on step 4, requesting validation",
    "Latency spike detected; switching to cached embedding set",
    "Prefetching docs for .aether manifest schema",
    "Ethics check: risk=LOW, alignment score=0.94",
    "Suggest next action: run memory_cleanser with dry-run flag",
    "Streaming telemetry to dashboard",
    "Resolved conflict between two traces via vote/merge",
    "Warming model route: gpt-5→gpt-4o fallback ready",
];

function LiveThoughts() {
    const reduced = usePRM();
    const [lines, setLines] = useState<string[]>([]);
    const timer = useRef<number | null>(null);

    useEffect(() => {
        const interval = reduced ? 4000 : 2200;
        timer.current = window.setInterval(() => {
            const next =
                THOUGHT_SEEDS[Math.floor(Math.random() * THOUGHT_SEEDS.length)];
            setLines((prev) => {
                const out = [...prev, `▸ ${next}`];
                return out.slice(-12);
            });
        }, interval);
        return () => {
            if (timer.current) window.clearInterval(timer.current);
        };
    }, [reduced]);

    return (
        <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
            <div className="flex items-center justify-between">
                <h3 className="font-mono text-sm tracking-wider text-soft">
                    LIVE · LYRIXA THINKS
                </h3>
                <div className="text-xs text-neutral-400">
                    {reduced ? "reduced motion" : "streaming"}
                </div>
            </div>
            <div className="mt-3 h-56 overflow-auto rounded-lg bg-black/40 p-3 font-mono text-sm leading-relaxed">
                {lines.length === 0 ? (
                    <div className="text-neutral-400">
                        Waiting for first thought…
                    </div>
                ) : (
                    lines.map((l, i) => (
                        <motion.div
                            key={i}
                            initial={reduced ? false : { opacity: 0, y: 6 }}
                            animate={reduced ? {} : { opacity: 1, y: 0 }}
                            transition={{ duration: 0.25 }}
                            className="text-neutral-200"
                        >
                            {l}
                        </motion.div>
                    ))
                )}
            </div>
            <p className="mt-2 text-xs text-neutral-400">
                Demo simulates real output; wire to your runtime stream when ready.
            </p>
        </div>
    );
}

function FeatureGrid() {
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Capabilities</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {FEATURES.map((f) => (
                    <div
                        key={f.title}
                        className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
                    >
                        <div className="font-mono text-aether">{f.title}</div>
                        <p className="mt-2 text-sm text-neutral-300">{f.desc}</p>
                        {f.meta && (
                            <div className="mt-3 text-xs text-neutral-400">{f.meta}</div>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
}

function ModelRouter() {
    const rows = useMemo(
        () => [
            { task: "Reasoning / TS+React scaffolds", model: "GPT-5 (Preview)", note: "Primary for complex code + planning" },
            { task: "Fast UI iterations / multimodal", model: "GPT-4o", note: "Speedy fixes, image→code" },
            { task: "Docs & long-form polish", model: "Claude Sonnet 3.7/4", note: "Clear explanations and copy" },
            { task: "Cheap automations", model: "o3-mini", note: "Lint/test stubs & small patches" },
        ],
        []
    );
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Model Routing</h2>
            <div className="mt-4 overflow-x-auto">
                <table className="min-w-[640px] w-full text-sm">
                    <thead>
                        <tr className="text-left text-neutral-400">
                            <th className="py-2 pr-4">Task</th>
                            <th className="py-2 pr-4">Preferred Model</th>
                            <th className="py-2">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((r, i) => (
                            <tr key={i} className="border-t border-white/5">
                                <td className="py-3 pr-4">{r.task}</td>
                                <td className="py-3 pr-4 text-aether">{r.model}</td>
                                <td className="py-3">{r.note}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <pre className="mt-4 rounded-xl bg-black/50 p-4 text-xs text-neutral-200 overflow-auto">
                {`// model-router.json (example)
{
  "default": "gpt-5-preview",
  "routes": [
    { "when": { "intent": "code.gen|react|framer-motion|tailwind" }, "use": "gpt-5-preview" },
    { "when": { "intent": "ui.quick|bug.small|image.to.code" }, "use": "gpt-4o" },
    { "when": { "intent": "docs|copy|explain" }, "use": "claude-3.7-sonnet" },
    { "when": { "intent": "lint.fix|test.stub|small.patch" }, "use": "o3-mini" }
  ]
}`}
            </pre>
        </section>
    );
}

function InstallAndHooks() {
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Install & Developer Hooks</h2>
            <div className="mt-4 grid gap-6 lg:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">Launch</div>
                    <pre className="mt-2 rounded bg-black/50 p-3 text-xs overflow-auto">
                        {`# clone + run (example)
git clone https://github.com/AetherraLabs/Aetherra
cd Aetherra && python lyrixa/launcher.py
# or: npm run lyrixa:web (if you expose a web shell)`}
                    </pre>
                    <p className="mt-2 text-xs text-neutral-400">
                        Replace with your real commands; include system requirements and model keys.
                    </p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">.aether Hooks</div>
                    <pre className="mt-2 rounded bg-black/50 p-3 text-xs overflow-auto">
                        {`// plugin manifest snippet
plugin "memory_cleanser" {
  input_types  = ["trace[]", "policy"]
  output_types = ["summary"]
  on_event     = ["memory.decay", "conflict.detected"]
  risk         = "MED"; confidence = 0.92
}`}
                    </pre>
                    <p className="mt-2 text-xs text-neutral-400">
                        Show how plugins declare I/O, events, and risk/confidence so devs can build quickly.
                    </p>
                </div>
            </div>
        </section>
    );
}

export default function Lyrixa() {
    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">LYRIXA · AETHERRA INTERFACE</p>
                <h1 className="mt-2 text-3xl md:text-4xl font-bold">An interface that thinks with you</h1>
                <p className="mt-3 text-neutral-300">
                    Lyrixa is the living interface to the Aetherra AI-native OS — combining live reasoning,
                    quantum-aware memory, anticipation, and safe plugin orchestration in one coherent surface.
                </p>
            </header>

            <div className="mt-8 grid gap-6 lg:grid-cols-2">
                <LiveThoughts />
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">What you’re seeing</div>
                    <ul className="mt-2 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                        <li>Simulated “Lyrixa Thinks” stream (wire to your runtime feed later).</li>
                        <li>Confidence/risk-aware planning and plugin routing.</li>
                        <li>Memory/QFAC and ethics hooks integrated behind the scenes.</li>
                    </ul>
                    <div className="mt-3 text-xs text-neutral-400">
                        Tip: respect <code>prefers-reduced-motion</code> to keep this accessible.
                    </div>
                </div>
            </div>

            <FeatureGrid />
            <ModelRouter />
            <InstallAndHooks />
        </div>
    );
}
