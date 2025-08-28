import { motion } from "framer-motion";
import { useEffect, useState } from "react";

type Card = { title: string; desc: string; href: string; tag?: string };
type Featured = { title: string; href: string; blurb: string; cta?: { label: string; href: string } };

const QUICKSTARTS: Card[] = [
    { title: "Developers", desc: "Install, run, first .aether program.", href: "/docs/getting-started" },
    { title: "Plugin Authors", desc: "Manifest, hooks, validation, publish.", href: "/docs/plugins" },
    { title: "Researchers", desc: "Labs experiments & telemetry.", href: "/docs/labs" },
    { title: "Ops & Security", desc: "Permissions, sandboxing, audit.", href: "/docs/security" },
];

const CATEGORIES: Card[] = [
    { title: ".aether Language", desc: "Syntax, types, chains, errors.", href: "/docs/aether" },
    { title: "Plugin SDK", desc: "Schema, lifecycle, testing.", href: "/docs/plugins/sdk" },
    { title: "Runtime & CLI", desc: "Commands, config, exit codes.", href: "/docs/runtime" },
    { title: "Memory & Cognition", desc: "QFAC, FractalMesh, timeline.", href: "/docs/memory" },
    { title: "Safety & Ethics", desc: "Alignment, bias, rollback.", href: "/docs/safety" },
    { title: "API / Registry", desc: "Endpoints, auth, limits.", href: "/docs/api" },
    { title: "Tutorials & Recipes", desc: "Common tasks, copy-paste.", href: "/docs/recipes" },
    { title: "Changelog & Versioning", desc: "Releases, migrations.", href: "/docs/changelog" },
];

const FEATURED: Featured[] = [
    { title: "Build your first plugin", blurb: "Scaffold, implement I/O, validate, publish.", href: "/docs/tutorials/first-plugin", cta: { label: "Try in Playground", href: "/playground?example=first-plugin" } },
    { title: "Chain two plugins", blurb: "I/O compatibility, confidence thresholds.", href: "/docs/tutorials/chain-plugins", cta: { label: "Open Chain Designer", href: "/plugins#designer" } },
    { title: "Memory recall in chat", blurb: "Hybrid recall & context injection.", href: "/docs/tutorials/memory-chat", cta: { label: "Run Console", href: "/console" } },
];

export default function Docs() {
    const [q, setQ] = useState("");
    const [status, setStatus] = useState<{ api?: string; release?: string }>({});

    useEffect(() => {
        // Optionally fetch status JSON later
        fetch("/status.json").then(r => r.ok ? r.json() : null).then(j => j && setStatus(j)).catch(() => { });
    }, []);

    const all = [...QUICKSTARTS, ...CATEGORIES];
    const results = q
        ? all.filter(c => (c.title + c.desc).toLowerCase().includes(q.toLowerCase()))
        : [];

    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">DOCS · AETHERRA</p>
                <motion.h1 initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }} className="mt-2 text-3xl md:text-4xl font-bold">
                    Documentation hub
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Learn the language, build plugins, understand the runtime and memory model, and ship safely.
                </p>
                <div className="mt-4 flex gap-2">
                    <input
                        placeholder="Search docs…"
                        className="w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-aether/40"
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                    />
                    <a href="https://github.com/AetherraLabs/Aetherra/tree/main/docs" className="rounded-lg border border-white/10 px-3 py-2 text-sm hover:border-aether/40">Edit</a>
                    <a href="https://github.com/AetherraLabs/Aetherra/issues/new?template=doc_issue.md" className="rounded-lg border border-white/10 px-3 py-2 text-sm hover:border-aether/40">Report</a>
                </div>
                {q && (
                    <div className="mt-2 rounded-xl border border-white/10 bg-black/40 p-3 text-sm">
                        <div className="text-xs text-neutral-400 mb-1">Results</div>
                        <div className="flex flex-wrap gap-2">
                            {results.map((r) => (
                                <a key={r.href} className="rounded-md border border-white/10 px-2 py-1 hover:border-aether/40" href={r.href}>
                                    {r.title}
                                </a>
                            ))}
                            {!results.length && <div className="text-neutral-500">No matches</div>}
                        </div>
                    </div>
                )}
            </header>

            <section className="mt-8 grid gap-4 md:grid-cols-4">
                {QUICKSTARTS.map((c) => (
                    <a key={c.title} href={c.href} className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow">
                        <div className="font-mono text-aether">{c.title}</div>
                        <p className="mt-1 text-sm text-neutral-300">{c.desc}</p>
                    </a>
                ))}
            </section>

            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Browse by category</h2>
                <div className="mt-4 grid gap-4 md:grid-cols-3 lg:grid-cols-4">
                    {CATEGORIES.map((c) => (
                        <a key={c.title} href={c.href} className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow">
                            <div className="font-mono text-aether">{c.title}</div>
                            <p className="mt-1 text-sm text-neutral-300">{c.desc}</p>
                        </a>
                    ))}
                </div>
            </section>

            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Featured tutorials</h2>
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                    {FEATURED.map((f) => (
                        <div key={f.title} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                            <div className="font-mono text-aether">{f.title}</div>
                            <p className="mt-2 text-sm text-neutral-300">{f.blurb}</p>
                            <div className="mt-3 flex gap-2">
                                <a href={f.href} className="rounded-lg border border-white/10 px-3 py-1.5 text-sm hover:border-aether/40">Read</a>
                                {f.cta && (
                                    <a href={f.cta.href} className="rounded-lg bg-aether px-3 py-1.5 text-sm text-black"> {f.cta.label} </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <section className="mt-10 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether mb-2">Core Endpoints</div>
                    <ul className="text-sm text-neutral-300 space-y-1">
                        <li><code className="text-aether">GET /metrics</code> — Prometheus plaintext metrics</li>
                        <li><code className="text-aether">GET /api/ai/stream</code> — AI output via SSE</li>
                        <li><code className="text-aether">GET /api/memory/status</code> — Memory health</li>
                        <li><code className="text-aether">GET /api/memory/audit</code> — Deterministic audit view</li>
                        <li><code className="text-aether">GET /api/memory/graph</code> — Memory graph snapshot</li>
                        <li><code className="text-aether">GET /api/plugins</code> — List registered plugins</li>
                        <li><code className="text-aether">POST /api/plugins/register</code> — Register plugin</li>
                    </ul>
                </div>
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether mb-2">Signing & Trust</div>
                    <ul className="text-sm text-neutral-300 space-y-1">
                        <li>Strict signing is optional in dev; enable via environment flags for production.</li>
                        <li>When strict, manifests must include a valid signature and public key.</li>
                        <li>Trust zones are derived from signature verification and policy.</li>
                    </ul>
                </div>
            </section>

            <section className="mt-10 grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">API status</div>
                    <div className="mt-1 text-2xl font-semibold">{status.api || "—"}</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">Latest release</div>
                    <div className="mt-1 text-2xl font-semibold">{status.release || "—"}</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">Glossary</div>
                    <a href="/docs/glossary" className="mt-1 inline-block underline decoration-aether/60 underline-offset-4 hover:text-aether">Open glossary</a>
                </div>
            </section>

            <p className="mt-6 text-xs text-neutral-500">
                Prefer fewer clicks? Use global search (⌘/Ctrl+K). Docs are versioned; switch in the footer.
            </p>
        </div>
    );
}
