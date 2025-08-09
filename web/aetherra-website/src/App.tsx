import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowRight, Brain, Cpu, Gauge, Github, MonitorCog, PlugZap, ShieldCheck, Twitter, Workflow } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

/**
 * Aetherra Labs – Neon OS Site (Vite + React + Tailwind + Motion)
 * ----------------------------------------------------------------
 * Goal: "More Aetherra Labs-esque" with a wow-factor
 * Design: Neon cyber-lab aesthetic, subtle parallax, animated glow grid,
 *         glass cards, neon strokes, and an interactive .aether terminal.
 * Theme: Aetherra Green #00ff88, Dark #0a0a0a, Gray #1a1a1a, JetBrains Mono
 *
 * How to use:
 * 1) npm create vite@latest aetherra-site -- --template react
 * 2) cd aetherra-site && npm i framer-motion lucide-react
 * 3) Tailwind setup for Vite (docs). Add JetBrains Mono to index.html link tag.
 * 4) Replace src/App.jsx with this file. Start dev server.
 */

// Theme tokens
const COLORS = {
    green: "#00ff88",
    dark: "#0a0a0a",
    gray: "#111111",
};

// --- Shared UI Primitives ----------------------------------------------------
type SectionProps = {
    id?: string;
    className?: string;
    children: React.ReactNode;
};
const Section = ({ id, className = "", children }: SectionProps) => (
    <section id={id} className={`w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>{children}</section>
);

type GlassCardProps = {
    children: React.ReactNode;
    className?: string;
};
const GlassCard = ({ children, className = "" }: GlassCardProps) => (
    <div className={`relative rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm shadow-[0_0_0_1px_rgba(255,255,255,0.06)] ${className}`}>
        {children}
    </div>
);

// Neon grid background
const NeonGrid = () => (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-30">
        <div className="absolute inset-0 opacity-20" style={{
            backgroundImage:
                `linear-gradient(transparent 0, transparent 95%, ${COLORS.green} 100%), linear-gradient(90deg, transparent 0, transparent 95%, ${COLORS.green} 100%)`,
            backgroundSize: "60px 60px",
            maskImage: "radial-gradient(1200px 600px at 50% -10%, black 40%, transparent 70%)"
        }} />
        <div className="absolute inset-0" style={{
            background:
                `radial-gradient(1000px 500px at 90% -10%, ${COLORS.green}22, transparent 60%), radial-gradient(800px 500px at 0% 10%, ${COLORS.green}14, transparent 60%)`
        }} />
    </div>
);

// Parallax wrapper
type ParallaxProps = {
    children: React.ReactNode;
    strength?: number;
};
const Parallax = ({ children, strength = 60 }: ParallaxProps) => {
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
    const y = useTransform(scrollYProgress, [0, 1], [strength, -strength]);
    return (
        <motion.div ref={ref} style={{ y }}>
            {children}
        </motion.div>
    );
};

// Typing demo for .aether terminal
const useTypewriter = (lines: string[], speed = 35, hold = 1500) => {
    const [out, setOut] = useState("");
    const [idx, setIdx] = useState(0);
    useEffect(() => {
        let active = true;
        const write = async () => {
            const text = lines[idx % lines.length];
            for (let i = 0; i <= text.length && active; i++) {
                setOut(text.slice(0, i));
                await new Promise(r => setTimeout(r, speed));
            }
            await new Promise(r => setTimeout(r, hold));
            if (active) setIdx(i => i + 1);
        };
        write();
        return () => { active = false; };
    }, [idx, lines, speed, hold]);
    return out;
};

type NeonButtonProps = {
    children: React.ReactNode;
    href?: string;
    highlight?: boolean;
};
const NeonButton = ({ children, href = "#", highlight = false }: NeonButtonProps) => (
    <a href={href} className={`group inline-flex items-center gap-2 rounded-xl px-5 py-3 border transition ${highlight ? "border-[rgba(0,255,136,0.35)] bg-[rgba(0,255,136,0.08)] hover:bg-[rgba(0,255,136,0.16)]" : "border-white/15 hover:bg-white/10"}`} style={highlight ? { color: COLORS.green } : { color: "#fff" }}>
        {children}
        <ArrowRight className="h-4 w-4 transition -translate-x-0.5 group-hover:translate-x-0" />
    </a>
);

// --- Site Sections -----------------------------------------------------------
const Nav = () => (
    <nav className="sticky top-0 z-40 border-b border-white/10 bg-[rgba(10,10,10,0.65)] backdrop-blur">
        <Section className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full" style={{ background: `conic-gradient(from 180deg, ${COLORS.green}, #0affd2, ${COLORS.green})` }} />
                <span className="font-jetbrains text-[15px] tracking-[0.3em] text-white">AETHERRA LABS</span>
            </div>
            <div className="hidden md:flex items-center gap-6 text-sm">
                <a href="#what" className="text-white/80 hover:text-white">What</a>
                <a href="#features" className="text-white/80 hover:text-white">Features</a>
                <a href="#labs" className="text-white/80 hover:text-white">Labs</a>
                <a href="#roadmap" className="text-white/80 hover:text-white">Roadmap</a>
                <a href="#join" className="text-white/80 hover:text-white">Join</a>
            </div>
            <div className="flex items-center gap-3">
                <a href="https://github.com/AetherraLabs" target="_blank" className="p-2 rounded-lg border border-white/10 hover:border-white/20"><Github className="h-5 w-5 text-white" /></a>
                <a href="https://x.com/AetherraProject" target="_blank" className="p-2 rounded-lg border border-white/10 hover:border-white/20"><Twitter className="h-5 w-5 text-white" /></a>
            </div>
        </Section>
    </nav>
);

const Hero = () => (
    <header className="relative overflow-hidden border-b border-white/10" style={{ background: `linear-gradient(180deg, rgba(0,255,136,0.05), ${COLORS.dark})` }}>
        <NeonGrid />
        <Section className="py-24 sm:py-28">
            <div className="grid lg:grid-cols-12 gap-10 items-center">
                <div className="lg:col-span-7 text-center lg:text-left">
                    <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="font-jetbrains text-4xl sm:text-6xl font-bold text-white tracking-tight">
                        CODE <span style={{ color: COLORS.green }}>AWAKENED</span>
                    </motion.h1>
                    <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.8 }} className="mt-6 text-white/70 max-w-2xl">
                        Aetherra is an AI-native operating system for intelligent computation. It coordinates goals, memory, agents, and plugins through <code className="px-1 rounded bg-white/10 text-white">.aether</code>, forming a living interface that thinks and adapts.
                    </motion.p>
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.8 }} className="mt-10 flex flex-wrap items-center gap-4">
                        <NeonButton highlight href="#features">Explore the OS</NeonButton>
                        <NeonButton href="#join">Get Early Access</NeonButton>
                    </motion.div>
                    <div className="mt-6 text-white/50 text-xs">Subtle parallax, neon grid, and glass UI establish an Aetherra Labs look.</div>
                </div>
                <div className="lg:col-span-5">
                    <Parallax>
                        <GlassCard className="p-5">
                            <div className="aspect-[4/3] w-full rounded-2xl border border-white/10 bg-black/40 overflow-hidden">
                                <NeonTerminal />
                            </div>
                        </GlassCard>
                    </Parallax>
                </div>
            </div>
        </Section>
    </header>
);

const NeonTerminal = () => {
    const typed = useTypewriter([
        'goal: "Show cognitive services and current focus"',
        '',
        'services: list_services()',
        'focus: summarize(goals.today)',
        '',
        'if health(services) < 0.9:\n    self_heal()',
        '',
        'narrate()  # AetherRuntime → Lyrixa',
    ]);
    return (
        <div className="h-full w-full p-4 font-jetbrains text-[13px] text-white/90">
            <div className="flex items-center gap-2 mb-3">
                <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
                <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
                <div className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
                <span className="ml-2 text-white/50">.aether — Interactive</span>
            </div>
            <pre className="whitespace-pre-wrap leading-relaxed">{typed}<span className="animate-pulse">▌</span></pre>
        </div>
    );
};

const What = () => (
    <Section id="what" className="py-24">
        <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
                <h2 className="font-jetbrains text-3xl text-white">What is Aetherra?</h2>
                <p className="mt-4 text-white/70 leading-relaxed">
                    Aetherra is an AI-first OS that manages <strong>thoughts</strong>, <strong>goals</strong>, and <strong>intelligent behaviors</strong> instead of just files and processes. It orchestrates plugins, agents, and memory through the <span style={{ color: COLORS.green }}>AetherRuntime</span>.
                </p>
                <ul className="mt-6 space-y-3 text-white/80">
                    <li className="flex gap-3"><ShieldCheck className="h-5 w-5" style={{ color: COLORS.green }} /> Persistent cognitive state with reflective safety</li>
                    <li className="flex gap-3"><Workflow className="h-5 w-5" style={{ color: COLORS.green }} /> Intent-first orchestration via <span className="font-jetbrains">.aether</span></li>
                    <li className="flex gap-3"><PlugZap className="h-5 w-5" style={{ color: COLORS.green }} /> Dynamic plugin ecosystem with live GUI zones</li>
                </ul>
            </div>
            <GlassCard className="p-6">
                <div className="rounded-2xl border border-white/10 bg-black/40 p-4">
                    <pre className="text-white text-sm md:text-base overflow-auto font-jetbrains"><code>{`goal: "Summarize system logs and reflect on anomalies"

memory: load_logs("today")
summary: summarize(memory)
anoms: detect_anomalies(summary)

if anoms:
    reflect_on(anoms)
    escalate_to("Lyrixa")
else:
    store(summary, tag="daily_digest")`}</code></pre>
                </div>
            </GlassCard>
        </div>
    </Section>
);

const Features = () => (
    <Section id="features" className="py-24">
        <h2 className="font-jetbrains text-3xl text-white text-center">Core Features</h2>
        <p className="text-white/70 text-center mt-3">OS-level intelligence, dynamic UI, and reflective cognition.</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
            <Feature icon={Brain} title="Cognitive Memory" desc="Episodic + semantic state with narrative continuity." />
            <Feature icon={Workflow} title=".aether Orchestration" desc="Intent-first scripts route plugins, agents, and memory." />
            <Feature icon={PlugZap} title="Plugin Ecosystem" desc="Install/uninstall with live tab injection and UI zones." />
            <Feature icon={MonitorCog} title="Cognitive Dashboard" desc="Live OS monitoring – see goals, services, events." />
            <Feature icon={Cpu} title="Distributed Services" desc="Cross-process registry with heartbeats and persistence." />
            <Feature icon={Gauge} title="Confidence & Safety" desc="Static/runtime analysis with thresholds & enforcement." />
        </div>
    </Section>
);

type FeatureProps = {
    icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
    title: string;
    desc: string;
};
const Feature = ({ icon: Icon, title, desc }: FeatureProps) => (
    <GlassCard className="p-6 hover:bg-white/10 transition">
        <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg border border-white/10 bg-white/5">
                <Icon className="h-5 w-5" style={{ color: COLORS.green }} />
            </div>
            <div>
                <h3 className="text-white font-medium font-jetbrains">{title}</h3>
                <p className="text-white/70 text-sm mt-1">{desc}</p>
            </div>
        </div>
    </GlassCard>
);

const LabsShowcase = () => (
    <Section id="labs" className="py-24">
        <h2 className="font-jetbrains text-3xl text-white text-center">Aetherra Labs Experiments</h2>
        <p className="text-white/70 text-center mt-3">A living collection of internal prototypes and research builds.</p>
        <div className="grid md:grid-cols-3 gap-6 mt-12">
            {[
                { title: "Quantum Fractal Memory", tag: "QFAC", desc: "Observer-aware compression with fidelity scoring and causal branching." },
                { title: "Self-Reflection Engine", tag: "Introspector", desc: "Night cycles, safe experimentation, rollback, ethics trace." },
                { title: "Plugin Chaining", tag: "Orchestrator", desc: "Sequential, parallel, adaptive chains with confidence gating." },
            ].map((x, i) => (
                <GlassCard key={i} className="p-6">
                    <div className="text-xs tracking-widest" style={{ color: COLORS.green }}>{x.tag}</div>
                    <h3 className="text-white font-jetbrains mt-1">{x.title}</h3>
                    <p className="text-white/70 text-sm mt-2">{x.desc}</p>
                    <div className="mt-4">
                        <NeonButton href="#">Read Notes</NeonButton>
                    </div>
                </GlassCard>
            ))}
        </div>
    </Section>
);

const Roadmap = () => (
    <Section id="roadmap" className="py-24">
        <h2 className="font-jetbrains text-3xl text-white text-center">Roadmap</h2>
        <div className="mt-12 grid md:grid-cols-3 gap-6">
            {[
                { title: "v4.1 – Validated AI OS", body: "Distributed services, cognitive dashboard, night cycles." },
                { title: "v4.2 – Voice & Mobile", body: "Voice interface, mobile companion, push insights." },
                { title: "v4.3 – .aether-native Kernel", body: "Transpile core workflows to .aether; boot via AetherRuntime." },
            ].map((r, i) => (
                <GlassCard key={i} className="p-6">
                    <h3 className="text-white font-jetbrains">{r.title}</h3>
                    <p className="text-white/70 text-sm mt-2">{r.body}</p>
                </GlassCard>
            ))}
        </div>
    </Section>
);

const Join = () => (
    <Section id="join" className="py-24">
        <GlassCard className="p-10 text-center">
            <h2 className="font-jetbrains text-3xl text-white">Join the Build</h2>
            <p className="mt-3 text-white/70">Get early access, developer updates, and plugin SDK announcements.</p>
            <form className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
                <input className="w-full sm:w-96 px-4 py-3 rounded-xl bg-[#121212] border border-white/10 text-white outline-none focus:border-white/20" placeholder="you@domain.com" />
                <button className="px-5 py-3 rounded-xl border border-[rgba(0,255,136,0.35)] bg-[rgba(0,255,136,0.08)] hover:bg-[rgba(0,255,136,0.16)]" style={{ color: COLORS.green }}>Subscribe</button>
            </form>
            <div className="mt-4 text-white/50 text-xs">By subscribing you agree to receive updates from Aetherra Labs.</div>
        </GlassCard>
    </Section>
);

const Footer = () => (
    <footer className="border-t border-white/10 py-12">
        <Section className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full" style={{ background: `conic-gradient(from 180deg, ${COLORS.green}, #0affd2, ${COLORS.green})` }} />
                <span className="font-jetbrains text-white/80 text-sm">Aetherra Labs — CODE AWAKENED</span>
            </div>
            <div className="text-white/50 text-xs">© {new Date().getFullYear()} Aetherra Labs. All rights reserved.</div>
        </Section>
    </footer>
);

export default function App() {
    return (
        <div className="min-h-screen" style={{ background: COLORS.dark, fontFamily: 'JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace' }}>
            <NeonGrid />
            <Nav />
            <Hero />
            <What />
            <Features />
            <LabsShowcase />
            <Roadmap />
            <Join />
            <Footer />
        </div>
    );
}
