// src/pages/Roadmap.tsx
import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

/** Local reduced-motion hook (so this file is self-contained) */
function usePRM() {
    const [prefers, setPrefers] = useState(false);
    useEffect(() => {
        const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
        const listener = () => setPrefers(mq.matches);
        listener();
        mq.addEventListener?.("change", listener);
        return () => mq.removeEventListener?.("change", listener);
    }, []);
    return prefers;
}

/** Types */
type Status = "Planned" | "Active" | "Blocked" | "Done";
type Workstream = "A" | "B" | "C" | "D" | "E" | "F";
type Milestone = { label: string; done: boolean; link?: string };
type Epic = {
    id: string;            // uuid or slug
    code: string;          // e.g., A1
    workstream: Workstream;
    title: string;
    outcome: string;
    status: Status;
    owner?: string;
    due: string;           // ISO date
    milestones: Milestone[];
    metrics?: string[];
    dependencies?: string[]; // list of epic codes
};

type Scorecard = {
    memoryP50?: number | null;
    memoryP95?: number | null;
    narrativeScore?: number | null;
    pluginSuccess?: number | null;
    agentsActive?: number | null;
    registryP50?: number | null;
    uptime?: number | null;
    timelineEngagement?: number | null;
    securityCritical?: number | null;
};

/** ----- Default data (mirrors Aetherra_Living_Roadmap.md) ----- */
const DEFAULT_EPICS: Epic[] = [
    {
        id: "epic-a1",
        code: "A1",
        workstream: "A",
        title: "Narrative & Reflective Memory in UI",
        outcome: "Daily/weekly stories with causal chains & quality scoring surfaced in Lyrixa.",
        status: "Planned",
        due: "2025-09-30",
        milestones: [
            { label: "Story panel + timeline", done: false },
            { label: "Causality markers", done: false },
            { label: "Quality/coherence scoring UI", done: false },
        ],
        metrics: ["Narrative quality scoring enabled in UI; >70% user rating"],
        dependencies: ["A2"]
    },
    {
        id: "epic-a2",
        code: "A2",
        workstream: "A",
        title: "Memory Performance & Scaling",
        outcome: "<200ms average recall under load; backups & recovery runbook.",
        status: "Active",
        due: "2025-09-15",
        milestones: [
            { label: "FAISS (or equivalent) index", done: false },
            { label: "Lazy loading + enrichment", done: true },
            { label: "Backups + recovery runbook", done: false },
            { label: "Bench harness in CI", done: false },
        ],
        metrics: ["p50 <120ms, p95 <250ms"]
    },
    {
        id: "epic-a3",
        code: "A3",
        workstream: "A",
        title: "Curiosity + Conflict (Night Cycle)",
        outcome: "Contradiction detection, gap questions, shadow-state exploration.",
        status: "Planned",
        due: "2025-10-15",
        milestones: [
            { label: "Contradiction detector wired", done: false },
            { label: "Question generator + priority", done: false },
            { label: "Shadow state + rollback gates", done: false },
        ],
        metrics: [">80% conflict resolution (tests)"]
    },
    {
        id: "epic-b1",
        code: "B1",
        workstream: "B",
        title: "Self-Correction Engine",
        outcome: "Plugin errors diagnosed; fix proposals with confirm-to-apply; pattern memory.",
        status: "Active",
        due: "2025-09-30",
        milestones: [
            { label: "Error monitor", done: true },
            { label: "LLM diagnosis + patch", done: false },
            { label: "Diff preview & apply", done: false },
            { label: "Pattern memory", done: false },
        ],
        metrics: ["≥95% plugin execution success"]
    },
    {
        id: "epic-b2",
        code: "B2",
        workstream: "B",
        title: "Background Agents & Coordinator",
        outcome: "Planner, MemoryAnalyzer, BugHunter, Performance agents w/ scheduler.",
        status: "Planned",
        due: "2025-11-15",
        milestones: [
            { label: "Agent lifecycle + IPC", done: false },
            { label: "Scheduler + priorities", done: false },
            { label: "Coordination + conflicts", done: false },
        ],
        metrics: ["≥3 agents active; ≥70% automated completion"]
    },
    {
        id: "epic-b3",
        code: "B3",
        workstream: "B",
        title: "Permissions & Audit",
        outcome: "Granular permissions, sandboxing, structured audit logs.",
        status: "Planned",
        due: "2025-10-31",
        milestones: [
            { label: "Permission schema + prompts", done: false },
            { label: "Sandbox for untrusted code", done: false },
            { label: "Audit logs", done: false },
        ],
        metrics: ["Zero critical vulns (quarterly)"]
    },
    {
        id: "epic-c1",
        code: "C1",
        workstream: "C",
        title: "Plugin Registry MVP (API + Web)",
        outcome: "Submit, validate, search, rate; security levels + scanning.",
        status: "Active",
        due: "2025-09-30",
        milestones: [
            { label: "REST API + auth", done: false },
            { label: "Submission + validation", done: false },
            { label: "Search & discovery UI", done: false },
            { label: "Security scanner + trust tiers", done: false },
        ],
        metrics: ["API p50 <200ms; 100% scan coverage"]
    },
    {
        id: "epic-c2",
        code: "C2",
        workstream: "C",
        title: "DX & Official Plugins",
        outcome: "Scaffold, tests, docs generator; 20+ official plugins.",
        status: "Planned",
        due: "2025-10-31",
        milestones: [
            { label: "create-aetherra-plugin", done: false },
            { label: "Test harness + CI template", done: false },
            { label: "Docs generator", done: false },
            { label: "20 official plugins", done: false },
        ],
        metrics: ["4.5★ avg rating; >100 downloads"]
    },
    {
        id: "epic-c3",
        code: "C3",
        workstream: "C",
        title: "Community Programs",
        outcome: "Bounty board, mentorship, demo day.",
        status: "Planned",
        due: "2025-11-30",
        milestones: [
            { label: "Bounty board", done: false },
            { label: "Mentorship signups", done: false },
            { label: "Monthly demo day", done: false },
        ],
        metrics: ["50+ active plugin devs"]
    },
    {
        id: "epic-d1",
        code: "D1",
        workstream: "D",
        title: "Memory Timeline & Layout",
        outcome: "Interactive timeline, saved layouts, status strip.",
        status: "Planned",
        due: "2025-09-30",
        milestones: [
            { label: "Cluster view + recall", done: false },
            { label: "Layout presets", done: false },
            { label: "Status strip", done: false },
        ],
        metrics: [">60% timeline engagement"]
    },
    {
        id: "epic-d2",
        code: "D2",
        workstream: "D",
        title: "Task Recipes & Tutorials",
        outcome: "Runnable docs tied to console/playground.",
        status: "Planned",
        due: "2025-10-15",
        milestones: [
            { label: "12 task recipes", done: false },
            { label: "Playground deep links", done: false },
            { label: "Success telemetry", done: false },
        ],
        metrics: ["Reduced time-to-first-success"]
    },
    {
        id: "epic-e1",
        code: "E1",
        workstream: "E",
        title: "IDE Integrations",
        outcome: "VS Code/JetBrains chat, inline actions, project-wide analysis.",
        status: "Planned",
        due: "2026-03-31",
        milestones: [
            { label: "Context-aware chat", done: false },
            { label: "Inline actions", done: false },
            { label: "Project-wide refactors", done: false },
        ],
        metrics: ["10k installs"]
    },
    {
        id: "epic-e2",
        code: "E2",
        workstream: "E",
        title: "Universal Language Bridge",
        outcome: "Interop flows for Python/JS/Rust/Go; cross-stack advisor.",
        status: "Planned",
        due: "2026-06-30",
        milestones: [
            { label: "Interop flows", done: false },
            { label: "Performance advisor", done: false },
        ],
        metrics: ["End-to-end demo apps"]
    },
    {
        id: "epic-e3",
        code: "E3",
        workstream: "E",
        title: "Marketplace v2",
        outcome: "In-app installer, ratings/reviews, verification & versions.",
        status: "Planned",
        due: "2026-04-30",
        milestones: [
            { label: "Installer UI", done: false },
            { label: "Ratings/reviews", done: false },
            { label: "Verification + versions", done: false },
        ]
    },
    {
        id: "epic-f1",
        code: "F1",
        workstream: "F",
        title: "Autonomous Maintenance",
        outcome: "Diagnose→simulate→test→gated deploy; rollback; confidence thresholds.",
        status: "Planned",
        due: "2026-09-30",
        milestones: [
            { label: "Sim testbed", done: false },
            { label: "Gate + rollback", done: false },
            { label: "Confidence policy", done: false },
        ],
        metrics: ["MTTR ↓; auto-remediation rate ↑"]
    },
    {
        id: "epic-f2",
        code: "F2",
        workstream: "F",
        title: "Self-Tuning & Shared Learning",
        outcome: "Behavior optimization; optional shared best-practice propagation.",
        status: "Planned",
        due: "2026-12-31",
        milestones: [
            { label: "Usage-driven tuning", done: false },
            { label: "Opt-in sharing", done: false },
        ],
        metrics: ["Productivity/latency gains"]
    },
];

const DEFAULT_SCORECARD: Scorecard = {
    memoryP50: null, memoryP95: null, narrativeScore: null, pluginSuccess: null,
    agentsActive: null, registryP50: null, uptime: null, timelineEngagement: null,
    securityCritical: 0
};

/** ----- UI helpers ----- */
function cls(...xs: (string | false | null | undefined)[]) { return xs.filter(Boolean).join(" "); }

function StatusBadge({ s }: { s: Status }) {
    const map: Record<Status, string> = {
        Active: "text-emerald-300",
        Planned: "text-yellow-300",
        Blocked: "text-red-300",
        Done: "text-neutral-300",
    };
    return <span className={cls("text-xs", map[s])}>{s}</span>;
}

function ProgressRing({ value }: { value: number }) {
    const size = 40, stroke = 5, r = (size - stroke) / 2, c = 2 * Math.PI * r;
    const dash = c * (1 - Math.max(0, Math.min(1, value)));
    return (
        <svg width={size} height={size} className="shrink-0">
            <circle cx={size / 2} cy={size / 2} r={r} stroke="currentColor" className="text-white/15" strokeWidth={stroke} fill="none" />
            <circle cx={size / 2} cy={size / 2} r={r} stroke="currentColor" className="text-aether" strokeWidth={stroke} fill="none" strokeDasharray={c} strokeDashoffset={dash} strokeLinecap="round" />
        </svg>
    );
}

function pctDone(ms: Milestone[]) {
    if (!ms.length) return 0;
    const done = ms.filter(m => m.done).length;
    return done / ms.length;
}

function daysUntil(iso: string) {
    const d = new Date(iso).getTime();
    const now = Date.now();
    const diff = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
    return diff;
}

/** Exporters */
function exportICS(epics: Epic[]) {
    const lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Aetherra Labs//Roadmap//EN"
    ];
    const upcoming = epics.filter(e => ["Active", "Planned"].includes(e.status) && daysUntil(e.due) >= -30);
    for (const e of upcoming) {
        const start = new Date(e.due);
        const dt = start.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
        const end = new Date(start.getTime() + 60 * 60 * 1000).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
        lines.push(
            "BEGIN:VEVENT",
            `UID:${e.code}@aetherra`,
            `SUMMARY:${e.code} · ${e.title}`,
            `DESCRIPTION:${e.outcome}`,
            `DTSTART:${dt}`,
            `DTEND:${end}`,
            "END:VEVENT"
        );
    }
    lines.push("END:VCALENDAR");
    const blob = new Blob([lines.join("\n")], { type: "text/calendar" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "aetherra-roadmap.ics"; a.click();
    URL.revokeObjectURL(url);
}

function exportCSV(epics: Epic[]) {
    const header = ["code", "workstream", "title", "status", "due", "owner", "progress", "dependencies"].join(",");
    const rows = epics.map(e => {
        const p = Math.round(pctDone(e.milestones) * 100) + "%";
        return [
            e.code, e.workstream, `"${e.title.replace(/"/g, '""')}"`, e.status, e.due, e.owner || "", p,
            `"${(e.dependencies || []).join(" ")}"`
        ].join(",");
    });
    const blob = new Blob([header + "\n" + rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "aetherra-roadmap.csv"; a.click();
    URL.revokeObjectURL(url);
}

/** ----- Page ----- */
export default function Roadmap() {
    const reduced = usePRM();

    // Data: try to fetch /roadmap.json (optional), else use defaults
    const [epics, setEpics] = useState<Epic[]>(DEFAULT_EPICS);
    const [score, setScore] = useState<Scorecard>(DEFAULT_SCORECARD);

    useEffect(() => {
        fetch("/roadmap.json", { cache: "no-store" })
            .then(r => r.ok ? r.json() : null)
            .then((j) => {
                if (!j) return;
                if (Array.isArray(j?.epics)) setEpics(j.epics);
                if (j?.scorecard) setScore({ ...DEFAULT_SCORECARD, ...j.scorecard });
            })
            .catch(() => {/* silent fallback */ });
    }, []);

    // Filters / sort
    const [q, setQ] = useState("");
    const [w, setW] = useState<"ALL" | Workstream>("ALL");
    const [s, setS] = useState<"ALL" | Status>("ALL");
    const [sort, setSort] = useState<"due" | "status" | "progress">("due");
    const filtered = useMemo(() => {
        let list = [...epics];
        if (q.trim()) {
            const t = q.toLowerCase();
            list = list.filter(e => (e.title + e.outcome + e.code).toLowerCase().includes(t));
        }
        if (w !== "ALL") list = list.filter(e => e.workstream === w);
        if (s !== "ALL") list = list.filter(e => e.status === s);
        switch (sort) {
            case "status":
                const order: Status[] = ["Active", "Planned", "Blocked", "Done"];
                list.sort((a, b) => order.indexOf(a.status) - order.indexOf(b.status));
                break;
            case "progress":
                list.sort((a, b) => pctDone(b.milestones) - pctDone(a.milestones));
                break;
            case "due":
            default:
                list.sort((a, b) => new Date(a.due).getTime() - new Date(b.due).getTime());
        }
        return list;
    }, [epics, q, w, s, sort]);

    const byDue = useMemo(() => [...filtered].sort((a, b) => new Date(a.due).getTime() - new Date(b.due).getTime()), [filtered]);
    const now = new Date();

    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            {/* Header */}
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">ROADMAP · DELIVERY</p>
                <motion.h1
                    initial={reduced ? false : { opacity: 0, y: 12 }}
                    animate={reduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.45 }}
                    className="mt-2 text-3xl md:text-4xl font-bold"
                >
                    Living roadmap & status
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Filter by workstream, status, and due date. Export calendar invites or CSV for planning.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                    <button onClick={() => exportICS(filtered)} className="rounded-lg bg-aether px-4 py-2 text-black font-medium shadow-glow">Export .ics</button>
                    <button onClick={() => exportCSV(filtered)} className="rounded-lg border border-white/10 px-4 py-2 hover:border-aether/40">Export CSV</button>
                </div>
            </header>

            {/* Scorecard */}
            <section className="mt-8 grid gap-4 md:grid-cols-3">
                <CardMetric label="Memory p50" value={fmtMs(score.memoryP50)} hint="lower is better" />
                <CardMetric label="Plugin success" value={fmtPct(score.pluginSuccess)} hint="last 7d" />
                <CardMetric label="Registry p50" value={fmtMs(score.registryP50)} hint="API latency" />
                <CardMetric label="Timeline engagement" value={fmtPct(score.timelineEngagement)} hint="UI usage" />
                <CardMetric label="Agents active" value={fmtNum(score.agentsActive)} hint="concurrent" />
                <CardMetric label="Security critical" value={fmtNum(score.securityCritical)} hint="this quarter" />
            </section>

            {/* Filters */}
            <section className="mt-8 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <div className="grid gap-3 md:grid-cols-5">
                    <input
                        placeholder="Search epics…"
                        className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-aether/40"
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                    />
                    <select className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm" value={w} onChange={(e) => setW(e.target.value as any)}>
                        <option value="ALL">All workstreams</option>
                        {(["A", "B", "C", "D", "E", "F"] as Workstream[]).map(x => <option key={x} value={x}>{x}</option>)}
                    </select>
                    <select className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm" value={s} onChange={(e) => setS(e.target.value as any)}>
                        <option value="ALL">All statuses</option>
                        {(["Active", "Planned", "Blocked", "Done"] as Status[]).map(x => <option key={x} value={x}>{x}</option>)}
                    </select>
                    <select className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm" value={sort} onChange={(e) => setSort(e.target.value as any)}>
                        <option value="due">Sort: Due date</option>
                        <option value="status">Sort: Status</option>
                        <option value="progress">Sort: Progress</option>
                    </select>
                    <div className="text-sm text-neutral-400 flex items-center">
                        {filtered.length} results
                    </div>
                </div>
            </section>

            {/* Grid */}
            <section className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filtered.map((e, i) => (
                    <motion.div
                        key={e.id}
                        initial={reduced ? false : { opacity: 0, y: 12 }}
                        whileInView={reduced ? {} : { opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.03 }}
                        className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div>
                                <div className="font-mono text-aether">{e.code} · WS {e.workstream}</div>
                                <div className="text-xs text-neutral-400">Due {new Date(e.due).toLocaleDateString()}</div>
                            </div>
                            <StatusBadge s={e.status} />
                        </div>
                        <h3 className="mt-1 font-semibold">{e.title}</h3>
                        <p className="mt-1 text-sm text-neutral-300">{e.outcome}</p>
                        <div className="mt-3 flex items-center gap-3">
                            <ProgressRing value={pctDone(e.milestones)} />
                            <div className="text-xs text-neutral-400">
                                {Math.round(pctDone(e.milestones) * 100)}% · {e.milestones.filter(m => m.done).length}/{e.milestones.length} milestones
                                <div className="mt-1">
                                    {e.milestones.slice(0, 3).map((m, idx) => (
                                        <div key={idx} className={cls("flex items-center gap-2", m.done ? "text-neutral-300" : "text-neutral-500")}>
                                            <span>{m.done ? "✓" : "•"}</span><span>{m.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        {!!(e.dependencies && e.dependencies.length) && (
                            <div className="mt-3 text-xs text-neutral-400">
                                Depends on: <span className="text-neutral-300">{e.dependencies.join(", ")}</span>
                            </div>
                        )}
                    </motion.div>
                ))}
            </section>

            {/* Timeline */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Timeline</h2>
                <div className="mt-4 relative">
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/10" />
                    <div className="grid gap-6">
                        {byDue.map((e, idx) => (
                            <div key={e.id} className={cls("grid md:grid-cols-2 gap-6 items-center")}>
                                <div className={cls("order-2 md:order-1", idx % 2 ? "md:col-start-1" : "md:col-start-1")}>
                                    <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
                                        <div className="flex items-center justify-between">
                                            <div className="font-mono text-aether">{e.code}</div>
                                            <StatusBadge s={e.status} />
                                        </div>
                                        <div className="text-xs text-neutral-400">Due {new Date(e.due).toLocaleString()}</div>
                                        <div className="mt-1 text-sm text-neutral-300">{e.title}</div>
                                    </div>
                                </div>
                                <div className="order-1 md:order-2 flex md:justify-center">
                                    <div className="relative">
                                        <div className="w-3 h-3 rounded-full bg-aether shadow-glow" />
                                        <div className="text-xs text-neutral-400 mt-2 text-center">
                                            {relDue(e.due, now)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Dependencies matrix */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Dependencies</h2>
                <div className="mt-3 overflow-x-auto">
                    <table className="min-w-[720px] w-full text-sm">
                        <thead>
                            <tr className="text-left text-neutral-400">
                                <th className="py-2 pr-4">Epic</th>
                                <th className="py-2 pr-4">Depends on</th>
                                <th className="py-2 pr-4">Status</th>
                                <th className="py-2 pr-4">Due</th>
                                <th className="py-2">Risk</th>
                            </tr>
                        </thead>
                        <tbody>
                            {epics.map(e => (
                                <tr key={e.id} className="border-t border-white/5">
                                    <td className="py-3 pr-4 font-mono text-aether">{e.code}</td>
                                    <td className="py-3 pr-4">{(e.dependencies && e.dependencies.length) ? e.dependencies.join(", ") : "—"}</td>
                                    <td className="py-3 pr-4"><StatusBadge s={e.status} /></td>
                                    <td className="py-3 pr-4">{new Date(e.due).toLocaleDateString()}</td>
                                    <td className="py-3">{riskHint(e)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <p className="mt-2 text-xs text-neutral-500">Hint: prioritize A2 → A1/B2; C1 → C2/E3; B3 → F1.</p>
            </section>
        </div>
    );
}

/** Small display components */
function CardMetric({ label, value, hint }: { label: string; value: string; hint?: string }) {
    return (
        <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
            <div className="text-xs uppercase tracking-wider text-neutral-400">{label}</div>
            <div className="mt-1 text-2xl font-semibold">{value}</div>
            {hint && <div className="text-xs text-neutral-500">{hint}</div>}
        </div>
    );
}

function fmtMs(v?: number | null) { return v == null ? "—" : `${Math.round(v)} ms`; }
function fmtPct(v?: number | null) { return v == null ? "—" : `${Math.round(v)}%`; }
function fmtNum(v?: number | null) { return v == null ? "—" : String(v); }

function relDue(iso: string, now: Date) {
    const d = new Date(iso);
    const days = Math.round((d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return "due today";
    if (days > 0) return `in ${days} day${days === 1 ? "" : "s"}`;
    return `${Math.abs(days)} day${days === -1 ? "" : "s"} ago`;
}

function riskHint(e: Epic) {
    const left = daysUntil(e.due);
    const prog = pctDone(e.milestones);
    if (e.status === "Blocked") return "High (blocked)";
    if (e.status === "Active" && left < 14 && prog < 0.5) return "Medium (behind)";
    if (e.status === "Planned" && left < 21) return "Medium (tight window)";
    return "Low";
}
