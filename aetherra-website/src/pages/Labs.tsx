import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import usePRM from "../hooks/usePrefersReducedMotion";

/** ─────────────────────────────────────────────────────────────
 * Small utilities
 * ────────────────────────────────────────────────────────────*/
type TrendPoint = { t: number; v: number };

function useSparkline(seed = 50, jitter = 5, len = 24, periodMs = 2000) {
    const [data, setData] = useState<TrendPoint[]>(() =>
        Array.from({ length: len }, (_, i) => ({ t: i, v: seed + Math.random() * jitter }))
    );
    useEffect(() => {
        const id = setInterval(() => {
            setData((prev) => {
                const last = prev[prev.length - 1]?.v ?? seed;
                const next = Math.max(0, last + (Math.random() - 0.5) * jitter * 1.5);
                const d = [...prev.slice(1), { t: (prev[prev.length - 1]?.t ?? 0) + 1, v: next }];
                return d;
            });
        }, periodMs);
        return () => clearInterval(id);
    }, [seed, jitter, periodMs]);
    return data;
}

function Sparkline({ points, width = 160, height = 48 }: { points: TrendPoint[]; width?: number; height?: number }) {
    if (!points.length) return null;
    const min = Math.min(...points.map((p) => p.v));
    const max = Math.max(...points.map((p) => p.v));
    const span = Math.max(1, max - min);
    const path = points
        .map((p, i) => {
            const x = (i / (points.length - 1)) * width;
            const y = height - ((p.v - min) / span) * height;
            return `${i === 0 ? "M" : "L"} ${x},${y}`;
        })
        .join(" ");
    return (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-12">
            <path d={path} fill="none" stroke="currentColor" className="text-aether/80" strokeWidth={2} />
        </svg>
    );
}

function Pill({ children }: { children: React.ReactNode }) {
    return <span className="rounded-md border border-white/10 bg-black/30 px-2 py-0.5 text-xs text-neutral-300">{children}</span>;
}

function StatusBadge({ s }: { s: "ACTIVE" | "PAUSED" | "COMPLETED" }) {
    const m =
        s === "ACTIVE" ? "text-emerald-300" : s === "PAUSED" ? "text-yellow-300" : "text-neutral-300";
    return <span className={`text-xs ${m}`}>{s}</span>;
}

/** ─────────────────────────────────────────────────────────────
 * Page
 * ────────────────────────────────────────────────────────────*/
type Experiment = {
    id: string;
    title: string;
    summary: string;
    status: "ACTIVE" | "PAUSED" | "COMPLETED";
    lastUpdated: string;
    tags: string[];
    metrics: { label: string; value: string }[];
};

const EXPTS: Experiment[] = [
    {
        id: "qfac-memory",
        title: "QFAC Memory Fidelity",
        summary:
            "Evaluates Quantum Fractal Adaptive Compression: fidelity vs. latency, decay policy effects, and retrieval coherence.",
        status: "ACTIVE",
        lastUpdated: "2025-08-10",
        tags: ["memory", "qfac", "fidelity", "latency"],
        metrics: [
            { label: "p50 read", value: "72 ms" },
            { label: "fidelity", value: "0.94" },
            { label: "coherence", value: "93%" }
        ]
    },
    {
        id: "unified-cognition",
        title: "Unified Cognitive Stack",
        summary:
            "Measures self-coherence across Identity, Ethics, and Memory; checks drift under long-running goal execution.",
        status: "ACTIVE",
        lastUpdated: "2025-08-09",
        tags: ["coherence", "agents", "identity"],
        metrics: [
            { label: "coherence", value: "94.5%" },
            { label: "cross-agent eff.", value: "100%" },
            { label: "drift index", value: "0.06" }
        ]
    },
    {
        id: "ethics-engine",
        title: "Ethical Cognition & Safety",
        summary:
            "Tracks value alignment scoring, bias detectors, and rollback latency under risk-gated plans.",
        status: "COMPLETED",
        lastUpdated: "2025-08-06",
        tags: ["ethics", "safety", "rollback"],
        metrics: [
            { label: "alignment", value: "0.95" },
            { label: "rollback", value: "78 ms" },
            { label: "blocks", value: "12" }
        ]
    }
];

const PAPERS = [
    { title: "Aetherra Manifesto v4.0", kind: "Whitepaper", tags: ["vision", "architecture"] },
    { title: "Quantum Fractal Adaptive Compression (QFAC)", kind: "Research Notes", tags: ["memory", "compression"] },
    { title: "Unified Cognitive Stack & Self-Coherence", kind: "Tech Brief", tags: ["identity", "ethics", "agents"] },
    { title: "Plugin Confidence & Safety System", kind: "Design Doc", tags: ["plugins", "safety"] }
];

const ARTIFACTS = [
    { name: "qfac_fidelity_eval.ipynb", size: "182 KB", checksum: "sha256…", note: "Repro notebook (simulated data)" },
    { name: "coherence_timeseries.csv", size: "64 KB", checksum: "sha256…", note: "Sample metrics for charts" },
    { name: "ethics_trace_examples.json", size: "41 KB", checksum: "sha256…", note: "Redacted decision traces" }
];

export default function Labs() {
    const reduced = usePRM();

    // Live-ish telemetry for three metrics with sparklines
    const memSeries = useSparkline(70, 10);
    const cohSeries = useSparkline(93, 2);
    const rbSeries = useSparkline(90, 8);

    const [seed, setSeed] = useState<number>(() => Math.floor(Math.random() * 1000));
    const refresh = () => setSeed((s) => s + 1);
    const now = useMemo(() => new Date().toLocaleString(), [seed]);

    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            {/* Header */}
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">LABS · RESEARCH & EXPERIMENTS</p>
                <motion.h1
                    initial={reduced ? false : { opacity: 0, y: 10 }}
                    animate={reduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                    className="mt-2 text-3xl md:text-4xl font-bold"
                >
                    Where the OS learns to think better
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Aetherra Labs explores memory (QFAC), unified cognition, safe planning, and plugin ecosystems with
                    reproducible experiments and transparent telemetry.
                </p>
            </header>

            {/* Featured Experiments */}
            <section className="mt-8">
                <div className="mb-3 flex items-end justify-between">
                    <h2 className="text-2xl md:text-3xl font-bold">Featured Experiments</h2>
                    <button onClick={refresh} className="text-sm underline decoration-aether/60 underline-offset-4 hover:text-aether">
                        Refresh
                    </button>
                </div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {EXPTS.map((e, i) => (
                        <motion.div
                            key={e.id}
                            initial={reduced ? false : { opacity: 0, y: 12 }}
                            whileInView={reduced ? {} : { opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.05 }}
                            className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <div className="font-mono text-aether">{e.title}</div>
                                    <div className="text-xs text-neutral-400">Updated {e.lastUpdated}</div>
                                </div>
                                <StatusBadge s={e.status} />
                            </div>
                            <p className="mt-2 text-sm text-neutral-300">{e.summary}</p>
                            <div className="mt-3 flex flex-wrap gap-1.5">
                                {e.tags.map((t) => (
                                    <Pill key={t}>{t}</Pill>
                                ))}
                            </div>
                            <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-neutral-300">
                                {e.metrics.map((m) => (
                                    <div key={m.label} className="rounded-lg border border-white/10 bg-black/30 p-2">
                                        <div className="text-neutral-400">{m.label}</div>
                                        <div className="font-semibold">{m.value}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-3 flex items-center justify-between text-xs">
                                <a className="underline decoration-aether/60 underline-offset-4 hover:text-aether" href="#">
                                    Open notes
                                </a>
                                <a className="underline decoration-aether/60 underline-offset-4 hover:text-aether" href="#">
                                    Replication kit
                                </a>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Live Telemetry (simulated) */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Telemetry (simulated)</h2>
                <p className="text-xs text-neutral-400">Last refresh: {now}</p>
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="text-xs uppercase tracking-wider text-neutral-400">Memory Retrieval p50</div>
                        <div className="mt-1 text-2xl font-semibold">~{Math.round(memSeries[memSeries.length - 1]?.v || 72)} ms</div>
                        <Sparkline points={memSeries} />
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="text-xs uppercase tracking-wider text-neutral-400">Coherence Index</div>
                        <div className="mt-1 text-2xl font-semibold">
                            {Math.min(100, Math.max(0, Math.round(cohSeries[cohSeries.length - 1]?.v || 94)))}%
                        </div>
                        <Sparkline points={cohSeries} />
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                        <div className="text-xs uppercase tracking-wider text-neutral-400">Rollback Latency</div>
                        <div className="mt-1 text-2xl font-semibold">~{Math.round(rbSeries[rbSeries.length - 1]?.v || 80)} ms</div>
                        <Sparkline points={rbSeries} />
                    </div>
                </div>
                <p className="mt-2 text-xs text-neutral-500">Wire these to your runtime bus when ready.</p>
            </section>

            {/* Papers & Notes */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Papers & Notes</h2>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                    {PAPERS.map((p) => (
                        <div key={p.title} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                            <div className="flex items-center justify-between">
                                <div className="font-mono text-aether">{p.title}</div>
                                <Pill>{p.kind}</Pill>
                            </div>
                            <div className="mt-2 flex flex-wrap gap-1.5">
                                {p.tags.map((t) => (
                                    <Pill key={t}>{t}</Pill>
                                ))}
                            </div>
                            <div className="mt-3 text-xs">
                                <a href="#" className="underline decoration-aether/60 underline-offset-4 hover:text-aether">
                                    View
                                </a>
                                <span className="mx-2 text-neutral-600">·</span>
                                <a href="#" className="underline decoration-aether/60 underline-offset-4 hover:text-aether">
                                    Cite
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Datasets & Artifacts */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Datasets & Artifacts</h2>
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                    {ARTIFACTS.map((a) => (
                        <div key={a.name} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                            <div className="font-mono text-aether">{a.name}</div>
                            <div className="mt-1 text-xs text-neutral-400">
                                {a.size} · {a.checksum}
                            </div>
                            <p className="mt-2 text-sm text-neutral-300">{a.note}</p>
                            <div className="mt-3 text-xs">
                                <a href="#" className="underline decoration-aether/60 underline-offset-4 hover:text-aether">
                                    Download
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
                <p className="mt-2 text-xs text-neutral-500">Checksums are placeholders—fill with real hashes.</p>
            </section>

            {/* Start an Experiment */}
            <section className="mt-10 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <h2 className="text-2xl font-bold">Start an Experiment</h2>
                <div className="mt-4 grid gap-6 lg:grid-cols-2">
                    <div>
                        <div className="font-mono text-aether">QFAC Fidelity (example)</div>
                        <pre className="mt-2 rounded bg-black/50 p-3 text-xs text-neutral-200 overflow-auto">
                            {`# 1) bootstrap runtime
python aetherra/launcher.py

# 2) run experiment (simulated)
.aether run qfac_fidelity_eval.aether --dataset=mem_traces.csv --policy=decay_v3

# 3) export artifacts
.aether export results --out=./labs/qfac_fidelity_eval
`}
                        </pre>
                        <p className="mt-2 text-xs text-neutral-400">Replace with your real commands and paths.</p>
                    </div>

                    <div>
                        <div className="font-mono text-aether">Safety & Ethics Checklist</div>
                        <ul className="mt-2 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                            <li>Log alignment score + rationale for each plan boundary.</li>
                            <li>Enable rollback snapshots for every mutating action.</li>
                            <li>Record model routes and confidence thresholds.</li>
                            <li>Redact sensitive traces before publishing artifacts.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <div className="mt-8 flex items-center justify-between">
                <p className="text-xs text-neutral-500">All data above is simulated until wired to your runtime.</p>
                <a href="/community" className="text-sm underline decoration-aether/60 underline-offset-4 hover:text-aether">
                    Propose an experiment
                </a>
            </div>
        </div>
    );
}
