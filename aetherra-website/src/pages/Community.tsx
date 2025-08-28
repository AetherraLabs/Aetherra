import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import usePRM from "../hooks/usePrefersReducedMotion";

type LinkItem = { label: string; href: string; desc: string };
type Track = { id: string; title: string; blurb: string; steps: string[]; cta: { label: string; href: string } };
type Issue = { id: string; title: string; labels: string[]; difficulty: "good-first" | "help-wanted"; url: string };
type Event = { title: string; when: string; desc: string; durationMins: number };
type Plugin = { name: string; desc: string; author: string; confidence: number; tags: string[] };
type Contributor = { name: string; role: string };

function Pill({ children }: { children: React.ReactNode }) {
    return <span className="rounded-md border border-white/10 bg-black/30 px-2 py-0.5 text-xs text-neutral-300">{children}</span>;
}
function DifficultyBadge({ d }: { d: Issue["difficulty"] }) {
    return <span className={`text-xs ${d === "good-first" ? "text-emerald-300" : "text-yellow-300"}`}>{d.replace("-", " ")}</span>;
}
function ConfidenceBar({ value }: { value: number }) {
    return (
        <div className="mt-2">
            <div className="h-2 w-full rounded bg-white/10">
                <div className="h-2 rounded bg-aether" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
            </div>
            <div className="mt-1 text-xs text-neutral-300">{value}% confidence</div>
        </div>
    );
}

const QUICK_LINKS: LinkItem[] = [
    { label: "Discord", href: "/community#discord", desc: "Chat, office hours, and support." },
    { label: "GitHub", href: "https://github.com/AetherraLabs", desc: "Issues, PRs, and project boards." },
    { label: "Docs", href: "/docs", desc: "Language, SDK, and runtime." },
    { label: "Roadmap", href: "/roadmap", desc: "What’s done and what’s next." },
    { label: "Plugins", href: "/plugins", desc: "Explore and submit plugins." },
    { label: "Manifesto", href: "/manifesto", desc: "Philosophy and principles." },
];

const TRACKS: Track[] = [
    {
        id: "builder",
        title: "Builder",
        blurb: "Create plugins and chains for the AI-native OS.",
        steps: [
            "Fork template plugin",
            "Declare input/output types",
            "Write minimal tests",
            "Publish to gallery",
        ],
        cta: { label: "Build a Plugin", href: "/plugins" },
    },
    {
        id: "researcher",
        title: "Researcher",
        blurb: "Run experiments in memory, cognition, and safety.",
        steps: [
            "Pick a Labs experiment",
            "Reproduce results",
            "Share artifacts",
            "Propose an improvement",
        ],
        cta: { label: "Open Labs", href: "/labs" },
    },
    {
        id: "designer",
        title: "Designer",
        blurb: "Shape the interface and experience of Lyrixa.",
        steps: [
            "Review UI kit",
            "Propose interactions",
            "Ship a micro-motion",
            "Document a pattern",
        ],
        cta: { label: "Contribute UX", href: "/lyrixa" },
    },
];

const STARTER_ISSUES: Issue[] = [
    {
        id: "1",
        title: "Add I/O compatibility badges to Plugin cards",
        labels: ["ui", "plugins"],
        difficulty: "good-first",
        url: "#",
    },
    {
        id: "2",
        title: "Expose Telemetry bus types in docs",
        labels: ["docs", "telemetry"],
        difficulty: "help-wanted",
        url: "#",
    },
    {
        id: "3",
        title: "Sample .aether chains for 3 common workflows",
        labels: ["examples", "aether"],
        difficulty: "good-first",
        url: "#",
    },
    {
        id: "4",
        title: "Risk/Confidence visualization polish",
        labels: ["ux", "safety"],
        difficulty: "help-wanted",
        url: "#",
    },
];

const EVENTS: Event[] = [
    { title: "Office Hours: Plugin Chaining", when: "Every Wed 12:00–12:45 (local)", desc: "Bring a plugin idea & get live help.", durationMins: 45 },
    { title: "Labs Sync: QFAC Memory", when: "1st Fri each month 11:00–12:00", desc: "Share results & plan next tests.", durationMins: 60 },
    { title: "Community Demo Day", when: "Last Thu month 16:00–17:00", desc: "Show what you built this month.", durationMins: 60 },
];

const SHOWCASE: Plugin[] = [
    { name: "Workflow Builder", desc: "Compose multi-agent plans with adaptive routing.", author: "Aetherra Labs", confidence: 96, tags: ["planning", "chains"] },
    { name: "Memory Cleanser", desc: "Curates & rewrites memory traces via policy.", author: "Aetherra Labs", confidence: 92, tags: ["memory", "qfac"] },
    { name: "Safety Guardian", desc: "Ethics checks, bias detectors, rollback orchestration.", author: "Aetherra Labs", confidence: 95, tags: ["ethics", "safety"] },
];

const CONTRIBUTORS: Contributor[] = [
    { name: "You?", role: "Core Contributor" },
    { name: "Early Adopter", role: "Plugin Author" },
    { name: "Research Partner", role: "Labs" },
];

export default function Community() {
    const reduced = usePRM();
    const [diff, setDiff] = useState<"all" | Issue["difficulty"]>("all");
    const [newsletter, setNewsletter] = useState<{ email: string; done: boolean }>({ email: "", done: false });

    const filteredIssues = useMemo(
        () => STARTER_ISSUES.filter((i) => (diff === "all" ? true : i.difficulty === diff)),
        [diff]
    );

    function addToCalendar() {
        const ics = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Aetherra Labs//Community//EN",
            ...EVENTS.map((ev, idx) => {
                const uid = `aetherra-${idx}@labs`;
                // Single placeholder DTSTART/DTEND (replace with real times)
                return [
                    "BEGIN:VEVENT",
                    `UID:${uid}`,
                    `SUMMARY:${ev.title}`,
                    `DESCRIPTION:${ev.desc}`,
                    "DTSTART:20250101T170000Z",
                    `DTEND:20250101T${(17 * 100 + Math.floor(ev.durationMins / 60) + 1)
                        .toString()
                        .padStart(4, "0")}00Z`,
                    "END:VEVENT",
                ].join("\n");
            }),
            "END:VCALENDAR",
        ].join("\n");
        const blob = new Blob([ics], { type: "text/calendar" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "aetherra-community.ics";
        a.click();
        URL.revokeObjectURL(url);
    }

    return (
        <div className="mx-auto max-w-7xl px-4 py-10">
            {/* HERO */}
            <header className="max-w-3xl">
                <p className="font-mono tracking-widest text-soft">COMMUNITY · BUILD WITH US</p>
                <motion.h1
                    initial={reduced ? false : { opacity: 0, y: 10 }}
                    animate={reduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                    className="mt-2 text-3xl md:text-4xl font-bold"
                >
                    From idea → plugin → OS capability
                </motion.h1>
                <p className="mt-3 text-neutral-300">
                    Join Aetherra Labs to shape the AI-native OS. Pick a track, grab a starter issue, and ship something real.
                </p>
                <div className="mt-6 flex flex-wrap gap-3">
                    <a href="#join" className="px-4 py-2 rounded-lg bg-aether text-black font-medium shadow-glow">Join the Discord</a>
                    <a href="https://github.com/AetherraLabs" className="px-4 py-2 rounded-lg border border-white/10 hover:border-aether/40">Open GitHub</a>
                </div>
            </header>

            {/* QUICK LINKS */}
            <section className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {QUICK_LINKS.map((l) => (
                    <a key={l.label} href={l.href} className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow">
                        <div className="font-mono text-aether">{l.label}</div>
                        <p className="mt-1 text-sm text-neutral-300">{l.desc}</p>
                    </a>
                ))}
            </section>

            {/* TRACKS */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Choose your path</h2>
                <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {TRACKS.map((t) => (
                        <div key={t.id} className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                            <div className="font-mono text-aether">{t.title}</div>
                            <p className="mt-2 text-sm text-neutral-300">{t.blurb}</p>
                            <ul className="mt-3 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                                {t.steps.map((s, i) => <li key={i}>{s}</li>)}
                            </ul>
                            <a href={t.cta.href} className="mt-4 inline-block rounded-lg border border-white/10 px-3 py-1.5 text-sm hover:border-aether/40">
                                {t.cta.label}
                            </a>
                        </div>
                    ))}
                </div>
            </section>

            {/* STARTER ISSUES */}
            <section className="mt-10">
                <div className="mb-3 flex items-end justify-between">
                    <h2 className="text-2xl md:text-3xl font-bold">Starter issues</h2>
                    <div className="flex items-center gap-2 text-sm">
                        <button
                            onClick={() => setDiff("all")}
                            className={`rounded-md border px-2 py-1 ${diff === "all" ? "border-aether/50 text-aether" : "border-white/10 hover:border-aether/30"}`}
                        >
                            All
                        </button>
                        <button
                            onClick={() => setDiff("good-first")}
                            className={`rounded-md border px-2 py-1 ${diff === "good-first" ? "border-aether/50 text-aether" : "border-white/10 hover:border-aether/30"}`}
                        >
                            Good first issue
                        </button>
                        <button
                            onClick={() => setDiff("help-wanted")}
                            className={`rounded-md border px-2 py-1 ${diff === "help-wanted" ? "border-aether/50 text-aether" : "border-white/10 hover:border-aether/30"}`}
                        >
                            Help wanted
                        </button>
                    </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                    {filteredIssues.map((i) => (
                        <a key={i.id} href={i.url} className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow">
                            <div className="flex items-start justify-between gap-3">
                                <div className="font-mono text-aether">{i.title}</div>
                                <DifficultyBadge d={i.difficulty} />
                            </div>
                            <div className="mt-2 flex flex-wrap gap-1.5">
                                {i.labels.map((l) => <Pill key={l}>{l}</Pill>)}
                            </div>
                            <div className="mt-3 text-xs text-neutral-400">Opens in GitHub</div>
                        </a>
                    ))}
                </div>
            </section>

            {/* EVENTS */}
            <section className="mt-10 rounded-2xl border border-white/10 bg-surface/60 p-4">
                <div className="flex items-end justify-between">
                    <h2 className="text-2xl font-bold">Events & Office Hours</h2>
                    <button onClick={addToCalendar} className="text-sm underline decoration-aether/60 underline-offset-4 hover:text-aether">
                        Add to Calendar (.ics)
                    </button>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                    {EVENTS.map((e) => (
                        <div key={e.title} className="rounded-xl border border-white/10 bg-black/30 p-3">
                            <div className="font-mono text-aether">{e.title}</div>
                            <div className="text-xs text-neutral-400">{e.when}</div>
                            <p className="mt-2 text-sm text-neutral-300">{e.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* SHOWCASE */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Community showcase</h2>
                <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {SHOWCASE.map((p) => (
                        <div key={p.name} className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow">
                            <div className="flex items-start justify-between">
                                <div className="font-mono text-aether">{p.name}</div>
                                <Pill>{p.author}</Pill>
                            </div>
                            <p className="mt-2 text-sm text-neutral-300">{p.desc}</p>
                            <div className="mt-2 flex flex-wrap gap-1.5">
                                {p.tags.map((t) => <Pill key={t}>{t}</Pill>)}
                            </div>
                            <ConfidenceBar value={p.confidence} />
                        </div>
                    ))}
                </div>
            </section>

            {/* NEWSLETTER / UPDATES (mock) */}
            <section id="join" className="mt-10 grid gap-6 lg:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">Get updates</div>
                    {newsletter.done ? (
                        <p className="mt-2 text-sm text-emerald-300">Thanks! You’re on the list (mock).</p>
                    ) : (
                        <form
                            className="mt-2 flex gap-2"
                            onSubmit={(e) => {
                                e.preventDefault();
                                setNewsletter({ email: "", done: true });
                            }}
                        >
                            <input
                                required
                                type="email"
                                placeholder="you@domain.com"
                                className="flex-1 rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-aether/40"
                                value={newsletter.email}
                                onChange={(e) => setNewsletter((s) => ({ ...s, email: e.target.value }))}
                            />
                            <button className="rounded-lg bg-aether px-4 py-2 text-black font-medium shadow-glow">Subscribe</button>
                        </form>
                    )}
                    <p className="mt-2 text-xs text-neutral-400">No spam. Just milestones, calls for testing, and events.</p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-surface/60 p-4">
                    <div className="font-mono text-aether">Code of Conduct & Governance</div>
                    <ul className="mt-2 list-disc pl-6 text-sm text-neutral-300 space-y-1">
                        <li>Be respectful. Assume good intent.</li>
                        <li>Document decisions; prefer RFCs for larger changes.</li>
                        <li>Safety-first: disclose risks; enable rollbacks.</li>
                        <li>Credit contributors and cite sources.</li>
                    </ul>
                    <div className="mt-3 text-xs">
                        <a className="underline decoration-aether/60 underline-offset-4 hover:text-aether" href="#">
                            Read full Code of Conduct
                        </a>
                        <span className="mx-2 text-neutral-600">·</span>
                        <a className="underline decoration-aether/60 underline-offset-4 hover:text-aether" href="#">
                            Propose an RFC
                        </a>
                    </div>
                </div>
            </section>

            {/* RECOGNITION */}
            <section className="mt-10">
                <h2 className="text-2xl md:text-3xl font-bold">Recent contributors</h2>
                <div className="mt-4 flex flex-wrap gap-3">
                    {CONTRIBUTORS.map((c) => (
                        <div key={c.name} className="rounded-xl border border-white/10 bg-surface/60 px-3 py-2 text-sm">
                            <span className="font-mono text-aether">{c.name}</span>
                            <span className="mx-2 text-neutral-600">·</span>
                            <span className="text-neutral-300">{c.role}</span>
                        </div>
                    ))}
                </div>
            </section>

            {/* FINAL CTA */}
            <section className="mt-10 rounded-2xl border border-white/10 bg-surface/60 p-4 text-center">
                <div className="font-mono tracking-widest text-soft">READY?</div>
                <h3 className="mt-1 text-2xl font-bold">Pick a track, grab an issue, and ship.</h3>
                <div className="mt-4 flex justify-center gap-3">
                    <a href="/plugins" className="px-4 py-2 rounded-lg bg-aether text-black font-medium shadow-glow">Build a Plugin</a>
                    <a href="/labs" className="px-4 py-2 rounded-lg border border-white/10 hover:border-aether/40">Run an Experiment</a>
                </div>
            </section>

            <p className="mt-4 text-xs text-neutral-500">
                Some links are placeholders—wire to your Discord invite, issue templates, and docs when ready.
            </p>
        </div>
    );
}
