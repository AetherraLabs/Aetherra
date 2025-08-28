import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import usePRM from "../hooks/usePrefersReducedMotion";

type Risk = "LOW" | "MED" | "HIGH";
type Category = "Memory" | "Workflow" | "DevTools" | "Safety";

type Plugin = {
    id: string;
    name: string;
    desc: string;
    author: string;
    version: string;
    category: Category;
    risk: Risk;
    confidence: number; // 0–100
    input_types: string[];
    output_types: string[];
    collaborates_with: string[]; // names
    tags: string[];
    last_updated: string; // ISO
};

const CATALOG: Plugin[] = [
    {
        id: "workflow-builder",
        name: "Workflow Builder",
        desc: "Compose multi-agent plans with sequential/parallel/adaptive chaining.",
        author: "Aetherra Labs",
        version: "1.3.2",
        category: "Workflow",
        risk: "LOW",
        confidence: 96,
        input_types: ["plan", "task[]"],
        output_types: ["result", "trace"],
        collaborates_with: ["Plugin Generator", "Assistant Trainer"],
        tags: ["planning", "chains"],
        last_updated: "2025-07-30"
    },
    {
        id: "assistant-trainer",
        name: "Assistant Trainer",
        desc: "Iterative fine-tuning & eval loops with dataset curation.",
        author: "Aetherra Labs",
        version: "0.9.5",
        category: "DevTools",
        risk: "MED",
        confidence: 93,
        input_types: ["dataset", "prompt"],
        output_types: ["model", "eval_report"],
        collaborates_with: ["Plugin Generator"],
        tags: ["train", "eval"],
        last_updated: "2025-07-28"
    },
    {
        id: "plugin-generator",
        name: "Plugin Generator",
        desc: "Scaffold, validate, version & publish .aether plugins.",
        author: "Aetherra Labs",
        version: "2.1.0",
        category: "DevTools",
        risk: "LOW",
        confidence: 97,
        input_types: ["spec"],
        output_types: ["code", "bundle"],
        collaborates_with: ["Workflow Builder", "Assistant Trainer"],
        tags: ["scaffold", "sdk"],
        last_updated: "2025-07-29"
    },
    {
        id: "memory-cleanser",
        name: "Memory Cleanser",
        desc: "Curates, decays, and rewrites memory traces with policy rules.",
        author: "Aetherra Labs",
        version: "1.0.4",
        category: "Memory",
        risk: "MED",
        confidence: 92,
        input_types: ["trace[]", "policy"],
        output_types: ["summary", "report"],
        collaborates_with: ["Workflow Builder"],
        tags: ["memory", "qfac"],
        last_updated: "2025-07-27"
    },
    {
        id: "safety-guardian",
        name: "Safety Guardian",
        desc: "Ethics checks, bias detectors, rollback orchestration.",
        author: "Aetherra Labs",
        version: "0.8.3",
        category: "Safety",
        risk: "LOW",
        confidence: 95,
        input_types: ["plan", "trace"],
        output_types: ["approval", "rollback_snapshot"],
        collaborates_with: ["Workflow Builder", "Memory Cleanser"],
        tags: ["ethics", "safety"],
        last_updated: "2025-07-31"
    }
];

const CATEGORIES: Category[] = ["Memory", "Workflow", "DevTools", "Safety"];
const RISKS: Risk[] = ["LOW", "MED", "HIGH"];

type FilterState = {
    query: string;
    category: "ALL" | Category;
    risk: "ANY" | Risk;
    minConfidence: number;
    sort: "confidence" | "updated" | "name";
};

function RiskBadge({ risk }: { risk: Risk }) {
    const cls =
        risk === "LOW"
            ? "text-emerald-300"
            : risk === "MED"
                ? "text-yellow-300"
                : "text-red-300";
    return <span className={`text-xs ${cls}`}>{risk}</span>;
}

function ConfidenceBar({ value }: { value: number }) {
    return (
        <div className="mt-2">
            <div className="h-2 w-full rounded bg-white/10">
                <div
                    className="h-2 rounded bg-aether"
                    style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
                />
            </div>
            <div className="mt-1 text-xs text-neutral-300">{value}% confidence</div>
        </div>
    );
}

function Pill({ children }: { children: React.ReactNode }) {
    return (
        <span className="rounded-md border border-white/10 bg-black/30 px-2 py-0.5 text-xs text-neutral-300">
            {children}
        </span>
    );
}

function formatDate(iso: string) {
    try {
        return new Date(iso).toLocaleDateString();
    } catch {
        return iso;
    }
}

function compatible(a: Plugin | null, b: Plugin | null) {
    if (!a || !b) return { ok: false, reasons: ["Select two plugins"] };
    const matches = a.output_types.filter((t) => b.input_types.includes(t));
    const ok = matches.length > 0;
    return {
        ok,
        matches,
        reasons: ok
            ? []
            : [
                `No I/O overlap. ${a.name} outputs ${a.output_types.join(
                    ", "
                )}, but ${b.name} expects ${b.input_types.join(", ")}.`
            ]
    };
}

export default function Plugins() {
    const reduced = usePRM();
    const [filters, setFilters] = useState<FilterState>({
        query: "",
        category: "ALL",
        risk: "ANY",
        minConfidence: 0,
        sort: "confidence"
    });
    const [selectA, setSelectA] = useState<string>("");
    const [selectB, setSelectB] = useState<string>("");

    const filtered = useMemo(() => {
        let list = [...CATALOG];
        if (filters.query) {
            const q = filters.query.toLowerCase();
            list = list.filter(
                (p) =>
                    p.name.toLowerCase().includes(q) ||
                    p.desc.toLowerCase().includes(q) ||
                    p.tags.join(" ").toLowerCase().includes(q)
            );
        }
        if (filters.category !== "ALL") {
            list = list.filter((p) => p.category === filters.category);
        }
        if (filters.risk !== "ANY") {
            list = list.filter((p) => p.risk === filters.risk);
        }
        list = list.filter((p) => p.confidence >= filters.minConfidence);

        switch (filters.sort) {
            case "updated":
                list.sort(
                    (a, b) =>
                        new Date(b.last_updated).getTime() -
                        new Date(a.last_updated).getTime()
                );
                break;
            case "name":
                list.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case "confidence":
            default:
                list.sort((a, b) => b.confidence - a.confidence);
        }
        return list;
    }, [filters]);

    const pluginA = useMemo(
        () => CATALOG.find((p) => p.id === selectA) ?? null,
        [selectA]
    );
    const pluginB = useMemo(
        () => CATALOG.find((p) => p.id === selectB) ?? null,
        [selectB]
    );
    const compat = compatible(pluginA, pluginB);

    const codeSnippet = useMemo(() => {
        if (!pluginA || !pluginB || !compat.ok) return "";
        const match = compat.matches[0];
        return `chain "prototype_chain" {
  steps = [
    { use: "${pluginA.id}", out: "${match}" },
    { use: "${pluginB.id}", in: "${match}" }
  ]
  confidence_min = 0.9
  rollback_on_fail = true
}`;
    }, [pluginA, pluginB, compat]);

    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">PLUGINS · ECOSYSTEM</p>
                <motion.h1
                    initial={reduced ? false : { opacity: 0, y: 10 }}
                    animate={reduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                    className="mt-2 text-3xl md:text-4xl font-bold"
                >
                    Build, chain, and evolve capabilities
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Discover plugins with declared I/O types, confidence scores, and risk levels.
                    Chain by compatibility and ship intelligent workflows.
                </p>
            </header>

            {/* FILTERS */}
            <section className="mt-8 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <div className="grid gap-3 md:grid-cols-4">
                    <input
                        placeholder="Search plugins…"
                        className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-aether/40"
                        value={filters.query}
                        onChange={(e) =>
                            setFilters((f) => ({ ...f, query: e.target.value }))
                        }
                    />
                    <select
                        className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm"
                        value={filters.category}
                        onChange={(e) =>
                            setFilters((f) => ({
                                ...f,
                                category: e.target.value as FilterState["category"]
                            }))
                        }
                    >
                        <option value="ALL">All Categories</option>
                        {CATEGORIES.map((c) => (
                            <option key={c} value={c}>
                                {c}
                            </option>
                        ))}
                    </select>
                    <select
                        className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm"
                        value={filters.risk}
                        onChange={(e) =>
                            setFilters((f) => ({
                                ...f,
                                risk: e.target.value as FilterState["risk"]
                            }))
                        }
                    >
                        <option value="ANY">Any Risk</option>
                        {RISKS.map((r) => (
                            <option key={r} value={r}>
                                {r}
                            </option>
                        ))}
                    </select>
                    <select
                        className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm"
                        value={filters.sort}
                        onChange={(e) =>
                            setFilters((f) => ({
                                ...f,
                                sort: e.target.value as FilterState["sort"]
                            }))
                        }
                    >
                        <option value="confidence">Sort: Confidence</option>
                        <option value="updated">Sort: Recently Updated</option>
                        <option value="name">Sort: Name</option>
                    </select>
                </div>
                <div className="mt-3 flex items-center gap-3">
                    <label className="text-xs text-neutral-400">Min confidence</label>
                    <input
                        type="range"
                        min={0}
                        max={100}
                        step={5}
                        value={filters.minConfidence}
                        onChange={(e) =>
                            setFilters((f) => ({
                                ...f,
                                minConfidence: Number(e.target.value)
                            }))
                        }
                    />
                    <span className="text-xs text-neutral-300">
                        {filters.minConfidence}%
                    </span>
                </div>
            </section>

            {/* GRID */}
            <section className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filtered.map((p, i) => (
                    <motion.div
                        key={p.id}
                        initial={reduced ? false : { opacity: 0, y: 12 }}
                        whileInView={reduced ? {} : { opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.04 }}
                        className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div>
                                <div className="font-mono text-aether">{p.name}</div>
                                <div className="text-xs text-neutral-400">
                                    v{p.version} · {p.category}
                                </div>
                            </div>
                            <RiskBadge risk={p.risk} />
                        </div>
                        <p className="mt-2 text-sm text-neutral-300">{p.desc}</p>

                        <div className="mt-3 flex flex-wrap gap-1.5">
                            {p.input_types.map((t) => (
                                <Pill key={`in-${p.id}-${t}`}>in:{t}</Pill>
                            ))}
                            {p.output_types.map((t) => (
                                <Pill key={`out-${p.id}-${t}`}>out:{t}</Pill>
                            ))}
                        </div>

                        <ConfidenceBar value={p.confidence} />

                        <div className="mt-3 flex items-center justify-between text-xs text-neutral-400">
                            <div>Updated {formatDate(p.last_updated)}</div>
                            <button
                                onClick={() =>
                                    setSelectA((sel) => (sel === p.id ? "" : p.id))
                                }
                                className={`rounded-md border px-2 py-1 ${selectA === p.id
                                        ? "border-aether/50 text-aether"
                                        : "border-white/10 hover:border-aether/30"
                                    }`}
                                title="Add as Chain Step A"
                            >
                                {selectA === p.id ? "Selected A" : "Select as A"}
                            </button>
                        </div>
                    </motion.div>
                ))}
            </section>

            {/* CHAIN DESIGNER */}
            <section className="mt-10 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <div className="flex items-end justify-between gap-3">
                    <h2 className="text-2xl font-bold">Chain Designer</h2>
                    <a
                        href="/community"
                        className="text-sm underline decoration-aether/60 underline-offset-4 hover:text-aether"
                    >
                        Submit a Plugin
                    </a>
                </div>

                <div className="mt-4 grid gap-4 md:grid-cols-3">
                    <div>
                        <label className="text-xs text-neutral-400">Step A</label>
                        <select
                            className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm"
                            value={selectA}
                            onChange={(e) => setSelectA(e.target.value)}
                        >
                            <option value="">Select plugin…</option>
                            {CATALOG.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="text-xs text-neutral-400">Step B</label>
                        <select
                            className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm"
                            value={selectB}
                            onChange={(e) => setSelectB(e.target.value)}
                        >
                            <option value="">Select plugin…</option>
                            {CATALOG.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-black/40 p-3 text-sm">
                        <div className="text-neutral-400">Compatibility</div>
                        {pluginA && pluginB ? (
                            compat.ok ? (
                                <div className="mt-1">
                                    <div className="text-aether">Compatible ✅</div>
                                    <div className="mt-1 text-neutral-300">
                                        I/O match: <code>{compat.matches.join(", ")}</code>
                                    </div>
                                </div>
                            ) : (
                                <div className="mt-1 text-red-300">
                                    Incompatible ❌
                                    <div className="mt-1 text-neutral-300 text-xs">
                                        {compat.reasons[0]}
                                    </div>
                                </div>
                            )
                        ) : (
                            <div className="mt-1 text-neutral-300">Pick Step A and Step B.</div>
                        )}
                    </div>
                </div>

                <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div className="rounded-xl border border-white/10 bg-black/40 p-3">
                        <div className="text-sm text-neutral-400">Suggested Chain</div>
                        <pre className="mt-2 h-40 overflow-auto rounded bg-black/60 p-3 text-xs text-neutral-200">
                            {codeSnippet || "// Select two compatible plugins to generate a chain"}
                        </pre>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-black/40 p-3">
                        <div className="text-sm text-neutral-400">Manifest Spec (excerpt)</div>
                        <pre className="mt-2 h-40 overflow-auto rounded bg-black/60 p-3 text-xs text-neutral-200">
                            {`plugin "${pluginA?.id || "your_plugin"}" {
  version = "1.0.0"
  category = "${pluginA?.category || "Memory"}"
  input_types  = ["trace[]", "policy"]
  output_types = ["summary"]
  risk = "MED"; confidence = 0.92
  collaborates_with = ["workflow-builder", "safety-guardian"]
}`}
                        </pre>
                    </div>
                </div>
            </section>

            {/* FOOTNOTE */}
            <p className="mt-4 text-xs text-neutral-500">
                All data above is simulated. Wire this view to your Plugin Registry when ready.
            </p>
        </div>
    );
}
