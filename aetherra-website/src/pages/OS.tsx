import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import SystemDiagram from "../components/SystemDiagram";
import usePRM from "../hooks/usePrefersReducedMotion";
import usePrometheus from "../hooks/usePrometheus";

type Metric = { label: string; value: string; hint?: string };
function genMetrics(): Metric[] {
    const rand = (min: number, max: number) =>
        Math.round(min + Math.random() * (max - min));
    return [
        { label: "Memory Ops (p50)", value: `${rand(55, 85)} ms`, hint: "QFAC-enabled" },
        { label: "Plan Depth (avg)", value: `${rand(3, 6)}`, hint: "goal→steps→checks" },
        { label: "Chain Success", value: `${rand(92, 98)}%`, hint: "confidence-aware" },
        { label: "Rollback Time", value: `${rand(60, 120)} ms`, hint: "safety engine" },
    ];
}

function LiveTelemetry() {
    const [metrics, setMetrics] = useState<Metric[]>(genMetrics());
    const { data: prom } = usePrometheus("/metrics", 7000);
    function resolveMetricValue(label: string): string | null {
        if (!prom) return null;
        const find = (pred: (n: string) => boolean) => prom.find(s => pred(s.name))?.value;
        if (label.startsWith("Memory Ops")) {
            const v = find(n => /memory/.test(n) && /(p50|latency|duration)/.test(n));
            return typeof v === 'number' ? `${Math.max(1, v).toFixed(0)} ms` : null;
        }
        if (label.startsWith("Plan Depth")) {
            const v = find(n => /(plan|planner)/.test(n) && /(depth|avg)/.test(n));
            return typeof v === 'number' ? `${v.toFixed(0)}` : null;
        }
        if (label.startsWith("Chain Success")) {
            const v = find(n => /(chain|workflow)/.test(n) && /(success|rate)/.test(n));
            return typeof v === 'number' ? `${Math.min(100, Math.max(0, v)).toFixed(0)}%` : null;
        }
        if (label.startsWith("Rollback Time")) {
            const v = find(n => /(rollback|safety)/.test(n) && /(latency|duration)/.test(n));
            return typeof v === 'number' ? `${Math.max(1, v).toFixed(0)} ms` : null;
        }
        return null;
    }
    useEffect(() => {
        const id = setInterval(() => setMetrics(genMetrics()), 2200);
        return () => clearInterval(id);
    }, []);
    return (
        <section className="mx-auto max-w-7xl px-4 py-8">
            <h2 className="text-2xl md:text-3xl font-bold">Live Telemetry (simulated; wire to SSE/Prometheus)</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {metrics.map((m) => {
                    const override = resolveMetricValue(m.label);
                    const val = override ?? m.value;
                    return (
                        <div key={m.label} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                            <div className="text-xs uppercase tracking-wider text-neutral-400">{m.label}</div>
                            <div className="mt-1 text-2xl font-semibold">{val}</div>
                            {m.hint && <div className="mt-1 text-xs text-neutral-400">{m.hint}</div>}
                        </div>
                    );
                })}
            </div>
            <p className="mt-2 text-xs text-neutral-500">
                These values are placeholders. Wire to your runtime once ready.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-xl border border-white/10 bg-black/40 p-3">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">Telemetry</div>
                    <div className="mt-1 text-sm">
                        <div><span className="text-neutral-400">Prometheus:</span> <code className="text-aether">GET /metrics</code></div>
                        <div><span className="text-neutral-400">AI Stream (SSE):</span> <code className="text-aether">GET /api/ai/stream</code></div>
                    </div>
                </div>
                <div className="rounded-xl border border-white/10 bg-black/40 p-3">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">Memory</div>
                    <div className="mt-1 text-sm">
                        <div><code className="text-aether">GET /api/memory/status</code></div>
                        <div><code className="text-aether">GET /api/memory/audit</code></div>
                        <div><code className="text-aether">GET /api/memory/graph</code></div>
                    </div>
                </div>
                <div className="rounded-xl border border-white/10 bg-black/40 p-3">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">Hub</div>
                    <div className="mt-1 text-sm">
                        <div><code className="text-aether">GET /api/plugins</code></div>
                        <div><code className="text-aether">POST /api/plugins/register</code></div>
                    </div>
                </div>
            </div>
        </section>
    );
}

function Architecture() {
    const cards = [
        {
            title: "Goal Kernel",
            desc:
                "Receives user intent as goals, expands to plans, tracks progress, and manages conflicts with confidence scoring.",
        },
        {
            title: "Memory (QFAC)",
            desc:
                "Quantum Fractal Adaptive Compression for episodic+semantic memory with fidelity scoring and <100ms access paths.",
        },
        {
            title: "Agent Orchestrator",
            desc:
                "Coordinates specialized agents; supports sequential, parallel, and adaptive execution with feedback.",
        },
        {
            title: "Plugin System v2",
            desc:
                "Manifested plugins with I/O types, lifecycle hooks, UI declarations, and chainability via metadata.",
        },
        {
            title: "Safety & Ethics",
            desc:
                "Decision traces, bias checks, rollback, and value alignment scoring—enforced at plan and action boundaries.",
        },
        {
            title: "Unified Cognitive Stack",
            desc:
                "Identity, context bridge, and self-coherence loop keeping memory, ethics, and behavior aligned.",
        },
    ];
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Architecture</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {cards.map((c) => (
                    <motion.div
                        key={c.title}
                        initial={{ opacity: 0, y: 12 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.35 }}
                        className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
                    >
                        <div className="flex items-center gap-2 font-mono text-aether">
                            {c.title.includes('Goal') && <span className="float-slow">🎯</span>}
                            {c.title.includes('Memory') && <span className="pulse-soft">🧠</span>}
                            {c.title.includes('Ethics') && <span className="float-slow">🧭</span>}
                            <span>{c.title}</span>
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">{c.desc}</p>
                    </motion.div>
                ))}
            </div>
        </section>
    );
}

function Benchmarks() {
    const rows = useMemo(
        () => [
            { metric: "Memory Retrieval (p50)", now: "60–90 ms", target: "< 60 ms", notes: "QFAC cache + locality" },
            { metric: "Plan Compile Time", now: "120–200 ms", target: "< 120 ms", notes: "warm context + router" },
            { metric: "Chain Success Rate", now: "93–98%", target: "≥ 98%", notes: "confidence gating" },
            { metric: "Rollback (safety)", now: "60–120 ms", target: "< 80 ms", notes: "pre-indexed traces" },
        ],
        []
    );
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Benchmarks</h2>
            <div className="mt-4 overflow-x-auto">
                <table className="min-w-[720px] w-full text-sm">
                    <thead>
                        <tr className="text-left text-neutral-400">
                            <th className="py-2 pr-4">Metric</th>
                            <th className="py-2 pr-4">Current</th>
                            <th className="py-2 pr-4">Target</th>
                            <th className="py-2">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((r, i) => (
                            <tr key={i} className="border-t border-white/5">
                                <td className="py-3 pr-4">{r.metric}</td>
                                <td className="py-3 pr-4">{r.now}</td>
                                <td className="py-3 pr-4 text-aether">{r.target}</td>
                                <td className="py-3">{r.notes}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <p className="mt-2 text-xs text-neutral-500">
                Replace with live measurements when wired to the OS runtime.
            </p>
        </section>
    );
}

function Diagram() {
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">System Diagram</h2>
            <div className="mt-6 rounded-2xl border border-white/10 bg-black/40 p-4">
                <SystemDiagram />
            </div>
        </section>
    );
}

function AetherExample() {
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">.aether in Practice</h2>
            <p className="mt-2 text-neutral-300 max-w-3xl">
                A tiny example of declaring a goal, letting the kernel plan, and running a safe chain with confidence gating.
            </p>
            <pre className="mt-4 rounded-2xl bg-black/50 p-4 text-xs text-neutral-200 overflow-auto">
                {`goal "summarize_daily_logs" {
  intent: "Compress system logs into a digest with alerts"
  success: "Digest saved, anomalies flagged"
}

chain "digest_pipeline" {
  steps = [
    { use: "log_collector",   out: "raw_logs" },
    { use: "noise_filter",    in: "raw_logs", out: "clean_logs" },
    { use: "digest_builder",  in: "clean_logs", out: "digest" },
    { use: "anomaly_checker", in: "digest", fail_on: risk > MED }
  ]
  confidence_min = 0.9
  rollback_on_fail = true
}

run "digest_pipeline" for goal "summarize_daily_logs"`}
            </pre>
        </section>
    );
}

function GettingStarted() {
    return (
        <section className="mx-auto max-w-7xl px-4 py-10">
            <h2 className="text-2xl md:text-3xl font-bold">Getting Started</h2>
            <div className="mt-4 grid gap-6 lg:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">Launch</div>
                    <pre className="mt-2 rounded bg-black/50 p-3 text-xs overflow-auto">
                        {`# boot the OS runtime (example)
python aetherra/launcher.py
# verify core workflows
.aether run goal_autopilot.aether
.aether run plugin_watchdog.aether
.aether run daily_reflector.aether`}
                    </pre>
                    <p className="mt-2 text-xs text-neutral-400">
                        Replace with your real paths/commands; list model keys and OS deps as needed.
                    </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">Safety & Ethics</div>
                    <ul className="mt-2 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                        <li>Every plan/action gets a trace with alignment score.</li>
                        <li>Confidence thresholds block unsafe chains.</li>
                        <li>Rollback snapshots allow reversible changes.</li>
                        <li>All decisions include a human-readable rationale.</li>
                    </ul>
                </div>
            </div>
        </section>
    );
}

export default function OSPage() {
    const reduced = usePRM();
    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">AETHERRA · AI-NATIVE OS</p>
                <motion.h1
                    initial={reduced ? false : { opacity: 0, y: 12 }}
                    animate={reduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                    className="mt-2 text-3xl md:text-4xl font-bold"
                >
                    An operating system that thinks
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Goals, memory, agents, plugins, and safety—bound together by a unified cognitive stack.
                </p>
            </header>
            <Architecture />
            <LiveTelemetry />
            <Benchmarks />
            <Diagram />
            <AetherExample />
            <GettingStarted />
        </div>
    );
}
