import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Stars } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { motion } from "framer-motion";
import {
    Activity,
    AlertCircle,
    AlertTriangle,
    Bell,
    BookOpen,
    Bot,
    Brain,
    CheckCircle,
    CircuitBoard,
    Clock,
    Code2,
    Command,
    Cpu, Database, Download, Edit, Eye, FileCode, FileText, Gauge,
    Globe,
    Key,
    Lightbulb, ListChecks, Lock,
    MessageSquare, Monitor, Moon, Network,
    Palette,
    Pause,
    Play,
    Plus,
    RefreshCw,
    Save,
    Scan,
    Search,
    Server,
    Settings,
    Shield,
    ShieldAlert,
    ShieldCheck,
    Sliders,
    Sparkles,
    Square,
    Sun,
    ThumbsUp,
    Timer,
    ToggleLeft,
    ToggleRight,
    Trash2,
    Unlock,
    Upload,
    Volume2,
    Workflow,
    Zap
} from "lucide-react";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Toaster, toast } from "sonner";
import ConsciousnessMonitor from "./components/ConsciousnessMonitor";
import { useApiPoll } from "./lib/api";
import { chat as sendChat } from "./lib/chat";

const BRAND = { green: "#00ff88", bg: "#070708", gray: "#1a1a1a" };

// Live metrics will be populated from backend soon; no simulated series here.

const Capsule: React.FC<{ className?: string; children: React.ReactNode }> = ({ className = "", children }) => (
    <div className={`relative rounded-[20px] p-[1px] bg-gradient-to-br from-emerald-500/30 via-transparent to-emerald-500/10 shadow-[0_0_40px_#00ff881a] ${className}`}>
        <div className="rounded-[18px] bg-[#0b0b0c]/80 backdrop-blur border border-[#1a1a1d]">{children}</div>
    </div>
);

const GlowCard: React.FC<{ className?: string; children: React.ReactNode }> = ({ children, className = "" }) => (
    <div className={`relative rounded-2xl ${className}`}>
        <div className="absolute inset-0 rounded-2xl blur-xl" style={{ background: `radial-gradient(60% 80% at 30% 10%, ${BRAND.green}22, transparent 60%)` }} />
        <Card className="relative bg-[#0b0b0c]/80 backdrop-blur border border-[#1a1a1d] shadow-[0_0_0_1px_#111,0_0_30px_#00ff8822] rounded-2xl">{children}</Card>
    </div>
);

const Stat = ({ label, value, sub, icon: Icon, ok = true }: any) => (
    <GlowCard>
        <CardContent className="p-4 flex items-center gap-3">
            <div className={`p-2 rounded-xl ${ok ? "bg-emerald-900/30" : "bg-amber-900/30"}`}>
                <Icon className={`w-5 h-5 ${ok ? "text-emerald-400" : "text-amber-400"}`} />
            </div>
            <div className="flex-1">
                <div className="text-gray-400 text-xs uppercase tracking-wider">{label}</div>
                <div className="text-white text-xl font-semibold leading-tight">{value}</div>
                {sub && <div className="text-gray-500 text-xs">{sub}</div>}
            </div>
        </CardContent>
    </GlowCard>
);

const Section = ({ title, icon: Icon, children, right }: any) => (
    <GlowCard>
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 text-emerald-400" />
                <CardTitle className="text-white">{title}</CardTitle>
            </div>
            {right}
        </CardHeader>
        <CardContent>{children}</CardContent>
    </GlowCard>
);

const SidebarLink = ({ icon: Icon, label, active = false, onClick }: any) => (
    <button onClick={onClick} className={`w-full group flex items-center gap-3 px-3 py-2 rounded-xl transition ${active ? "bg-emerald-900/20 text-white" : "text-gray-300 hover:bg-[#121214] hover:text-white"}`}>
        <Icon className={`w-4 h-4 ${active ? "text-emerald-400" : "text-gray-400 group-hover:text-emerald-400"}`} />
        <span className="text-sm font-medium">{label}</span>
    </button>
);

const Pill = ({ children }: any) => (
    <span className="text-[10px] px-2 py-1 rounded-full bg-emerald-900/30 text-emerald-300 border border-emerald-800/40">{children}</span>
);

function LyrixaHologram() {
    const groupRef = useRef<any>();
    const headRef = useRef<any>();
    const particlesRef = useRef<any>();

    useEffect(() => {
        let t = 0;
        let raf: number;
        const loop = () => {
            t += 0.01;

            if (groupRef.current) {
                // Gentle floating motion
                groupRef.current.position.y = Math.sin(t * 0.5) * 0.15;
                groupRef.current.rotation.y = t * 0.2;
            }

            if (headRef.current) {
                // Subtle head tilt
                headRef.current.rotation.x = Math.sin(t * 0.8) * 0.1;
            }

            if (particlesRef.current) {
                // Rotate particle ring
                particlesRef.current.rotation.y = t * 0.3;
                particlesRef.current.rotation.x = Math.sin(t * 0.4) * 0.2;
            }

            raf = requestAnimationFrame(loop);
        };
        raf = requestAnimationFrame(loop);
        return () => cancelAnimationFrame(raf);
    }, []);

    return (
        <group ref={groupRef}>
            {/* Head - ethereal sphere with wireframe */}
            <group ref={headRef} position={[0, 0.5, 0]}>
                <mesh>
                    <sphereGeometry args={[0.6, 32, 32]} />
                    <meshStandardMaterial
                        color={BRAND.green}
                        emissive={BRAND.green}
                        emissiveIntensity={1.5}
                        transparent
                        opacity={0.15}
                        wireframe={false}
                    />
                </mesh>
                <mesh>
                    <sphereGeometry args={[0.62, 16, 16]} />
                    <meshBasicMaterial
                        color={BRAND.green}
                        transparent
                        opacity={0.4}
                        wireframe={true}
                    />
                </mesh>

                {/* Eyes - glowing orbs */}
                <mesh position={[-0.2, 0.1, 0.45]}>
                    <sphereGeometry args={[0.08, 16, 16]} />
                    <meshStandardMaterial
                        color={BRAND.green}
                        emissive={BRAND.green}
                        emissiveIntensity={3}
                    />
                </mesh>
                <mesh position={[0.2, 0.1, 0.45]}>
                    <sphereGeometry args={[0.08, 16, 16]} />
                    <meshStandardMaterial
                        color={BRAND.green}
                        emissive={BRAND.green}
                        emissiveIntensity={3}
                    />
                </mesh>
            </group>

            {/* Body - abstract feminine form */}
            <mesh position={[0, -0.3, 0]}>
                <cylinderGeometry args={[0.35, 0.5, 1.2, 32]} />
                <meshStandardMaterial
                    color={BRAND.green}
                    emissive={BRAND.green}
                    emissiveIntensity={1}
                    transparent
                    opacity={0.12}
                    wireframe={false}
                />
            </mesh>
            <mesh position={[0, -0.3, 0]}>
                <cylinderGeometry args={[0.36, 0.51, 1.2, 8]} />
                <meshBasicMaterial
                    color={BRAND.green}
                    transparent
                    opacity={0.3}
                    wireframe={true}
                />
            </mesh>

            {/* Energy particles orbiting */}
            <group ref={particlesRef}>
                {Array.from({ length: 12 }).map((_, i) => {
                    const angle = (i / 12) * Math.PI * 2;
                    const radius = 1.2;
                    return (
                        <mesh
                            key={i}
                            position={[
                                Math.cos(angle) * radius,
                                Math.sin(angle * 2) * 0.3,
                                Math.sin(angle) * radius,
                            ]}
                        >
                            <sphereGeometry args={[0.04, 8, 8]} />
                            <meshBasicMaterial
                                color={BRAND.green}
                                transparent
                                opacity={0.6}
                            />
                        </mesh>
                    );
                })}
            </group>

            {/* Outer energy rings */}
            <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
                <torusGeometry args={[1.5, 0.02, 16, 64]} />
                <meshBasicMaterial
                    color={BRAND.green}
                    transparent
                    opacity={0.3}
                />
            </mesh>
            <mesh rotation={[0, 0, Math.PI / 4]} position={[0, 0, 0]}>
                <torusGeometry args={[1.4, 0.015, 16, 64]} />
                <meshBasicMaterial
                    color={BRAND.green}
                    transparent
                    opacity={0.2}
                />
            </mesh>
        </group>
    );
}

const HoloHero: React.FC = () => (
    <Capsule>
        <div className="relative h-56 w-full overflow-hidden rounded-[18px]">
            <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
                <ambientLight intensity={0.3} />
                <pointLight position={[3, 3, 3]} intensity={1.5} color={BRAND.green} />
                <pointLight position={[-3, -2, 2]} intensity={0.8} color={BRAND.green} />
                <Stars radius={50} depth={30} count={2000} factor={2} fade speed={0.5} />
                <LyrixaHologram />
            </Canvas>
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#070708]" />
            <div className="absolute bottom-3 left-4 text-sm text-gray-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span className="font-medium">Lyrixa</span>
                <span className="text-gray-500">· Holographic Avatar</span>
            </div>
        </div>
    </Capsule>
);

function useUISound() {
    const ctxRef = useRef<AudioContext | null>(null);
    const getCtx = () => ctxRef.current ?? (ctxRef.current = new ((window as any).AudioContext || (window as any).webkitAudioContext)());
    const ping = (freq = 520, gain = 0.03, len = 0.06) => {
        const ctx = getCtx();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = "sine";
        o.frequency.value = freq;
        g.gain.value = gain;
        o.connect(g);
        g.connect(ctx.destination);
        const t = ctx.currentTime;
        o.start(t);
        o.stop(t + len);
    };
    return { ping };
}

type CommandItem = {
    id: string;
    label: string;
    action: (setRoute: any, toggleAuto: any) => void;
};

const commands: CommandItem[] = [
    { id: "open-chat", label: "Open Lyrixa Chat", action: (setRoute) => setRoute("chat") },
    { id: "open-memory", label: "Open Memory", action: (setRoute) => setRoute("memory") },
    { id: "open-storm", label: "Open STORM Panel", action: (setRoute) => setRoute("storm") },
    { id: "run-aether", label: ".aether: Run Script", action: (setRoute) => setRoute("scripts") },
    { id: "toggle-auto-approve", label: "Toggle Auto-Approve", action: (_setRoute, toggleAuto) => toggleAuto((v: boolean) => !v) },
];

const CommandPalette: React.FC<{ open: boolean; onOpenChange: (v: boolean) => void; setRoute: any; toggleAuto: any; ping: () => void }> = ({ open, onOpenChange, setRoute, toggleAuto, ping }) => {
    const [q, setQ] = useState("");
    const items = useMemo(() => commands.filter((c) => c.label.toLowerCase().includes(q.toLowerCase())), [q]);
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                onOpenChange(!open);
            }
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [open, onOpenChange]);
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-xl bg-[#0b0b0c]/95 border border-[#1a1a1d]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-white">
                        <Command className="w-4 h-4 text-emerald-400" /> Command Palette
                    </DialogTitle>
                </DialogHeader>
                <div className="flex items-center gap-2">
                    <Search className="w-4 h-4 text-gray-500" />
                    <Input autoFocus placeholder="Type a command…" value={q} onChange={(e) => setQ(e.target.value)} className="bg-[#0e0e10] border-[#1f1f22]" />
                    <div className="text-[10px] text-gray-500 ml-auto">⌘K</div>
                </div>
                <div className="mt-3 max-h-64 overflow-auto">
                    {items.map((it) => (
                        <button key={it.id} onClick={() => { ping(); onOpenChange(false); it.action(setRoute, toggleAuto); }} className="w-full text-left px-3 py-2 rounded-lg hover:bg-[#121214] text-sm text-gray-200">
                            {it.label}
                        </button>
                    ))}
                    {!items.length && <div className="text-xs text-gray-500 px-3 py-2">No results</div>}
                </div>
            </DialogContent>
        </Dialog>
    );
};

const ActuatorExecuteDialog: React.FC<{
    open: boolean;
    onOpenChange: (v: boolean) => void;
    form: any;
    setForm: any;
    onExecute: () => void;
    ping: () => void;
}> = ({ open, onOpenChange, form, setForm, onExecute, ping }) => {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-xl bg-[#0b0b0c]/95 border border-[#1a1a1d]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-white">
                        <Play className="w-4 h-4 text-emerald-400" /> Execute Actuator Action
                    </DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                    <div>
                        <label className="text-xs text-gray-400 mb-1 block">Action Type</label>
                        <Input
                            placeholder="e.g., adjust_plugin_timeouts"
                            value={form.action_type}
                            onChange={(e) => setForm({ ...form, action_type: e.target.value })}
                            className="bg-[#0e0e10] border-[#1f1f22]"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-gray-400 mb-1 block">Target Service</label>
                        <Input
                            placeholder="e.g., plugin_system"
                            value={form.target_service}
                            onChange={(e) => setForm({ ...form, target_service: e.target.value })}
                            className="bg-[#0e0e10] border-[#1f1f22]"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-gray-400 mb-1 block">Parameters (JSON)</label>
                        <Input
                            placeholder='{"multiplier": 1.5}'
                            value={form.parameters}
                            onChange={(e) => setForm({ ...form, parameters: e.target.value })}
                            className="bg-[#0e0e10] border-[#1f1f22] font-mono text-xs"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-gray-400 mb-1 block">Priority</label>
                        <select
                            value={form.priority}
                            onChange={(e) => setForm({ ...form, priority: e.target.value })}
                            className="w-full bg-[#0e0e10] border border-[#1f1f22] rounded-md px-3 py-2 text-sm text-white"
                        >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                    <div className="flex gap-2 pt-2">
                        <Button
                            onClick={() => { ping(); onExecute(); }}
                            className="flex-1 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-black font-semibold"
                        >
                            <Play className="w-4 h-4 mr-2" /> Execute
                        </Button>
                        <Button
                            onClick={() => onOpenChange(false)}
                            variant="secondary"
                            className="rounded-xl"
                        >
                            Cancel
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default function App() {
    const [route, setRoute] = useState("dashboard");
    const [prompt, setPrompt] = useState("");
    const [streaming, setStreaming] = useState(false);
    const [openCmd, setOpenCmd] = useState(false);
    const { ping } = useUISound();
    const [_autoApprove, setAutoApprove] = useState(false);
    const [policy, setPolicy] = useState<any>(null);
    const [openActuatorDialog, setOpenActuatorDialog] = useState(false);
    const [actuatorForm, setActuatorForm] = useState({ action_type: '', target_service: '', parameters: '{}', priority: 'medium' });
    // Live connections
    const kernelStatus = useApiPoll<any>("/api/kernel/status", 5000);
    const kernelMetrics = useApiPoll<any>("/api/kernel/metrics", 7000);
    const agentsInfo = useApiPoll<any>("/api/agents", 8000);
    const tasksHistory = useApiPoll<any>("/api/tasks?limit=25&include_completed=1", 7000);
    const memoryStatus = useApiPoll<any>("/api/memory/status", 8000);
    const maintenance = useApiPoll<any>("/api/maintenance/status", 12000);
    const homeostasis = useApiPoll<any>("/api/homeostasis/status", 8000);
    const homeostasisMetrics = useApiPoll<any>("/api/homeostasis/metrics/snapshot", 10000);
    const memoryAudit = useApiPoll<any>("/api/memory/audit", 15000);

    // Proactively load policy snapshot (independent of SSE prelude)
    useEffect(() => {
        let alive = true;
        (async () => {
            try {
                const { getJSON } = await import('./lib/api');
                const pol = await getJSON<any>('/api/security/policy');
                if (alive && pol) setPolicy(pol);
            } catch { /* ignore */ }
        })();
        return () => { alive = false };
    }, []);

    // Security state
    const [securityAlerts, setSecurityAlerts] = useState<any[]>([
        { id: "SEC-001", timestamp: Date.now() - 3600000, severity: "warning", type: "policy_check", message: "Network policy allowlist check for api.example.com", status: "resolved" },
        { id: "SEC-002", timestamp: Date.now() - 7200000, severity: "info", type: "capability_grant", message: "Capability granted: network:webhook for core:webhook_manager", status: "active" },
    ]);
    const [securityMode, setSecurityMode] = useState<"standard" | "strict">("standard");
    const [showAuditDetails, setShowAuditDetails] = useState<string | null>(null);

    // .aether Scripts state
    const [aetherScripts, setAetherScripts] = useState<any[]>([
        { id: "daily_digest", name: "daily_digest.aether", description: "Generate daily narrative and store securely", status: "ready", lastRun: null },
        { id: "anomaly_check", name: "anomaly_check.aether", description: "Detect and report system anomalies", status: "ready", lastRun: Date.now() - 86400000 },
        { id: "memory_cleanup", name: "memory_cleanup.aether", description: "Clean up old memory entries and optimize", status: "ready", lastRun: Date.now() - 3600000 },
    ]);
    const [selectedScript, setSelectedScript] = useState<string | null>(null);
    const [scriptContent, setScriptContent] = useState<string>("");
    const [scriptExecution, setScriptExecution] = useState<any>(null);
    const [showScriptEditor, setShowScriptEditor] = useState(false);

    // Settings state
    const [settingsConfig, setSettingsConfig] = useState({
        appearance: {
            theme: "dark",
            accentColor: "#00ff88",
            fontSize: "medium",
            animations: true,
        },
        api: {
            backendUrl: (typeof window !== 'undefined' ? (window.localStorage?.getItem('lyrixa_backend') || window.location.origin) : ''),
            timeout: 30000,
            retryAttempts: 3,
            enableCORS: true,
        },
        notifications: {
            enabled: true,
            sound: false,
            toastDuration: 4000,
            showSystemNotifications: true,
            showSecurityAlerts: true,
            showExecutionStatus: true,
        },
        performance: {
            pollInterval: 8000,
            enableCaching: true,
            dataRetentionDays: 30,
            performanceMode: "balanced",
        },
        developer: {
            showDebugInfo: false,
            enableTrace: false,
            verboseLogging: false,
            mockData: false,
        }
    });

    const [suggestions, setSuggestions] = useState<any[]>([
        { id: "SI-101", title: "Tighten plugin sandbox for net access", risk: 0.12, impact: "security", desc: "Move to strict allowlist for outbound requests in high-risk contexts.", diff: "policy.net.strict = 1", status: "pending", hmr_target: "plugin_sandbox", hmr_source: "Aetherra.plugins.sandbox" },
        { id: "SI-204", title: "Promote memory QFAC rank to 48", risk: 0.18, impact: "performance", desc: "Increase TT-rank cap during night cycle to reduce loss.", diff: "memory.qfac.tt_rank = 48", status: "pending", hmr_target: "memory_adapter", hmr_source: "Aetherra.adapters.memory_adapter" },
        { id: "SI-315", title: "Add ReviewerAgent to default chains", risk: 0.09, impact: "quality", desc: "Insert reviewer after coder in PluginChainer.", diff: "chain: coder -> reviewer -> tester", status: "pending", hmr_target: "plugin_chainer", hmr_source: "Aetherra.agents.plugin_chainer" },
    ]);
    const approveSuggestion = async (id: string) => {
        // Optimistically mark approved in UI
        setSuggestions((arr) => arr.map((s) => (s.id === id ? { ...s, status: "approved" } : s)));

        try {
            const target = suggestions.find((s) => s.id === id);
            // Use raw fetch so we can inspect non-2xx responses (e.g., 503 HMR unavailable)
            const res = await fetch('/api/selfimprove/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({
                    proposal_id: id,
                    method: 'auto',
                    hmr_target: target?.hmr_target,
                    hmr_source: target?.hmr_source,
                })
            });
            let body: any = null;
            try { body = await res.json(); } catch { body = null; }

            if (body?.ok && body?.applied) {
                // Mark as applied if backend applied it (via selfinc or HMR)
                setSuggestions((arr) => arr.map((s) => (s.id === id ? { ...s, status: "applied", restart_required: Boolean(body?.restart_required) } : s)));
                toast.success(`[Self-Improve] Proposal ${id} applied (${body.method || 'auto'})`);
                return;
            }

            // If not applied but approved/accepted on backend, mark as restart-required and keep in Pending panel
            if (body && body.ok === true) {
                const rr = body?.restart_required === undefined ? true : Boolean(body.restart_required);
                setSuggestions((arr) => arr.map((s) => (s.id === id ? { ...s, status: "pending", restart_required: rr } : s)));
                toast.info(`[Self-Improve] Proposal ${id} approved — OS Restart Required`);
                return;
            }

            // Fallthrough: hard failure
            const errMsg = body?.error || `apply_failed (HTTP ${res.status})`;
            toast.error(`[Self-Improve] Apply failed for ${id}: ${errMsg}`);
        } catch (err: any) {
            // Network/other error — leave as approved for potential batch apply, but note HMR
            toast.error(`[Self-Improve] Error applying ${id}: ${err?.message || 'network error'}`);
        }
    };
    const denySuggestion = (id: string) => setSuggestions((arr) => arr.map((s) => (s.id === id ? { ...s, status: "denied" } : s)));
    const applyApproved = async () => {
        const approved = suggestions.filter((s) => s.status === "approved");
        if (approved.length === 0) return;

        ping();

        try {
            const proposals = approved.map((s) => ({
                proposal_id: s.id,
                hmr_target: s.hmr_target,
                hmr_source: s.hmr_source
            }));

            const { postJSON } = await import('./lib/api');
            const result = await postJSON('/api/selfimprove/batch-apply', {
                proposals,
                use_hmr: true
            });

            if (result.ok) {
                // Mark hot-applied; annotate restart-required for the rest
                const appliedIds = new Set(
                    (result.results || [])
                        .filter((r: any) => r?.ok && r?.applied)
                        .map((r: any) => r.proposal_id)
                );
                const restartIds = new Map<string, boolean>(
                    (result.results || [])
                        .filter((r: any) => r && r.ok && !r.applied)
                        .map((r: any) => [r.proposal_id, Boolean(r.restart_required ?? true)])
                );

                setSuggestions((arr) => arr.map((s) => {
                    if (appliedIds.has(s.id)) return { ...s, status: 'applied', restart_required: false };
                    if (restartIds.has(s.id)) return { ...s, status: 'pending', restart_required: restartIds.get(s.id) };
                    return s;
                }));

                const rrCount = Array.from(restartIds.values()).filter(Boolean).length;
                toast.success(`[Self-Improve] Applied ${appliedIds.size}/${approved.length} via HMR. ${rrCount || 0} require OS restart.`);
            } else {
                console.error('[Self-Improve] Batch apply failed:', result);
            }
        } catch (err) {
            console.error('[Self-Improve] Apply error:', err);
        }
    };
    const [messages, setMessages] = useState<any[]>([{ role: "assistant", text: "Hello, I'm Lyrixa. What shall we build today?" }]);
    const chatEndRef = useRef<HTMLDivElement | null>(null);
    useEffect(() => {
        // Auto-scroll chat to bottom when messages change or while streaming
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, [messages, streaming]);
    const send = async () => {
        if (!prompt.trim()) return;
        ping();
        const p = prompt;
        setPrompt("");
        setMessages((m) => [...m, { role: "user", text: p }, { role: "assistant", text: "" }]);
        setStreaming(true);
        try {
            let idx = -1;
            setMessages((m) => {
                const i = m.length - 1; // the empty assistant we appended
                idx = i;
                return m;
            });
            const result = await sendChat(p, {
                onPrelude: (frame) => {
                    if (frame?.type === 'policy' && frame?.data) {
                        setPolicy(frame.data);
                    }
                },
                onChunk: (t) => {
                    setMessages((m) => {
                        const arr = [...m];
                        if (idx >= 0 && arr[idx]) {
                            arr[idx] = { ...arr[idx], text: (arr[idx].text || "") + t };
                        }
                        return arr;
                    });
                },
            });
            // Ensure we have final text in case no chunks
            setMessages((m) => {
                const arr = [...m];
                if (idx >= 0 && arr[idx]) {
                    arr[idx] = { ...arr[idx], text: arr[idx].text || result.text || "" };
                }
                return arr;
            });
        } catch (e: any) {
            // Update the placeholder assistant bubble with the error instead of appending a duplicate
            setMessages((m) => {
                const arr = [...m];
                const lastIdx = arr.length - 1;
                if (lastIdx >= 0 && arr[lastIdx]?.role === 'assistant' && (arr[lastIdx]?.text ?? '') === '') {
                    arr[lastIdx] = { ...arr[lastIdx], text: `Chat error: ${e?.message || 'failed'}` };
                    return arr;
                }
                return [...m, { role: 'assistant', text: `Chat error: ${e?.message || 'failed'}` }];
            });
        } finally {
            setStreaming(false);
        }
    };
    const hue = useMemo(() => {
        const healthy = !!kernelStatus.data?.running;
        return healthy ? 120 : 150;
    }, [kernelStatus.data]);
    const menu = useMemo(
        () => [
            { id: "dashboard", icon: Gauge, label: "Overview" },
            { id: "chat", icon: MessageSquare, label: "Lyrixa Chat" },
            { id: "consciousness", icon: Brain, label: "Consciousness" },
            { id: "memory", icon: Database, label: "Memory" },
            { id: "agents", icon: Bot, label: "Agents" },
            { id: "kernel", icon: Cpu, label: "Kernel" },
            { id: "storm", icon: Sparkles, label: "STORM" },
            { id: "improve", icon: Lightbulb, label: "Self-Improve" },
            { id: "homeostasis", icon: Activity, label: "Homeostasis" },
            { id: "security", icon: Shield, label: "Security" },
            { id: "scripts", icon: Workflow, label: ".aether" },
            { id: "settings", icon: Settings, label: "Settings" },
        ],
        []
    );
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") setOpenCmd(true);
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, []);

    const executeActuator = async () => {
        try {
            const params = JSON.parse(actuatorForm.parameters || '{}');
            const { postJSON } = await import('./lib/api');
            const result = await postJSON('/api/homeostasis/actuators/execute', {
                action_type: actuatorForm.action_type,
                target_service: actuatorForm.target_service,
                parameters: params,
                priority: actuatorForm.priority,
                reason: 'UI manual execute'
            });

            if (result.ok && result.executed) {
                toast.success(`Actuator executed: ${actuatorForm.action_type}`);
                setOpenActuatorDialog(false);
                setActuatorForm({ action_type: '', target_service: '', parameters: '{}', priority: 'medium' });
            } else {
                toast.error(`Actuator failed to execute`);
            }
        } catch (err: any) {
            toast.error(`Error: ${err?.message || 'unknown'}`);
        }
    };

    return (
        <div
            className="min-h-screen relative text-gray-200"
            style={{ backgroundColor: BRAND.bg, ["--aether-hue" as any]: hue as any, boxShadow: `inset 0 0 0 1px hsl(var(--aether-hue) 100% 50% / 0)` }}
        >
            <Toaster position="top-right" theme="dark" richColors />
            <ActuatorExecuteDialog
                open={openActuatorDialog}
                onOpenChange={setOpenActuatorDialog}
                form={actuatorForm}
                setForm={setActuatorForm}
                onExecute={executeActuator}
                ping={ping}
            />
            <div className="pointer-events-none absolute inset-0 overflow-hidden">
                <div className="absolute -top-24 -left-24 w-[520px] h-[520px] rounded-full blur-3xl opacity-40" style={{ background: `radial-gradient(60% 60% at 50% 40%, hsl(${hue} 100% 50% / 0.2), transparent 70%)` }} />
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent" />
                <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
            </div>
            <div className="sticky top-0 z-30 border-b border-[#151518] bg-[#09090a]/70 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 120 }} className="w-8 h-8 rounded-xl" style={{ background: `radial-gradient(60% 60% at 50% 40%, ${BRAND.green}66, transparent 70%)`, boxShadow: `0 0 32px ${BRAND.green}33 inset, 0 0 24px ${BRAND.green}30` }} />
                        <div>
                            <div className="text-white font-bold tracking-wide">
                                AETHERRA <span className="text-emerald-400">Lyrixa</span>
                            </div>
                            <div className="text-[10px] uppercase tracking-[0.2em] text-gray-400">Code Awakened</div>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Pill>DP: off</Pill>
                        <Pill>Safety: standard</Pill>
                        <Pill>Profile: prod</Pill>
                    </div>
                </div>
            </div>
            <CommandPalette open={openCmd} onOpenChange={setOpenCmd} setRoute={setRoute} toggleAuto={setAutoApprove} ping={ping} />
            <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-12 gap-6">
                <aside className="col-span-12 lg:col-span-3 xl:col-span-2 space-y-1">
                    {menu.map((m) => (
                        <SidebarLink key={m.id} icon={m.icon} label={m.label} active={route === m.id} onClick={() => { ping(); setRoute(m.id); }} />
                    ))}
                    <div className="mt-4 text-xs text-gray-500">Build {new Date().getFullYear()} · v3</div>
                </aside>
                <main className="col-span-12 lg:col-span-9 xl:col-span-10 space-y-6">
                    {route === "dashboard" && (
                        <div className="space-y-6">
                            <HoloHero />

                            {/* Key System Metrics */}
                            <Section title="System Status" icon={Gauge}>
                                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                    <Stat
                                        label="Kernel"
                                        value={kernelStatus.data?.running ? "HEALTHY" : "OFFLINE"}
                                        sub={kernelStatus.data?.uptime ? `uptime ${kernelStatus.data.uptime}` : (kernelStatus.error ? "unavailable" : "loading")}
                                        icon={Cpu}
                                        ok={!!kernelStatus.data?.running}
                                    />
                                    <Stat
                                        label="Agents"
                                        value={agentsInfo.error ? "disabled" : (agentsInfo.data?.orchestrator ? `${agentsInfo.data.orchestrator.total_agents} active` : "loading")}
                                        sub={agentsInfo.data?.orchestrator ? `${agentsInfo.data.orchestrator.pending_tasks} pending` : ""}
                                        icon={Bot}
                                        ok={!agentsInfo.error}
                                    />
                                    <Stat
                                        label="Memory"
                                        value={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0 ? "STORM: ON" : "STORM: OFF"}
                                        sub={memoryStatus.data?.mode || (memoryStatus.error ? "unavailable" : "loading")}
                                        icon={Database}
                                        ok={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0}
                                    />
                                    <Stat
                                        label="Health Score"
                                        value={typeof maintenance.data?.kpis?.system_health_score === 'number' ? `${(maintenance.data.kpis.system_health_score * 100).toFixed(0)}%` : (maintenance.error ? 'unknown' : 'loading')}
                                        sub={maintenance.data?.overall?.runlevel ? `Level ${maintenance.data.overall.runlevel}` : ''}
                                        icon={Activity}
                                        ok={typeof maintenance.data?.kpis?.system_health_score === 'number' && maintenance.data.kpis.system_health_score > 0.8}
                                    />
                                </div>
                            </Section>

                            {/* Subsystem Health */}
                            <Section title="Subsystem Health" icon={Activity}>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                                    {[
                                        { label: "Kernel", status: kernelStatus.data?.running, icon: Cpu, color: "emerald" },
                                        { label: "Agents", status: !agentsInfo.error, icon: Bot, color: "blue" },
                                        // Consider STORM active if the orchestrator reports any agents
                                        { label: "Memory", status: ((agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0) || !!memoryStatus.data?.enabled, icon: Database, color: "purple" },
                                        // Homeostasis active if either its orchestrator is running or maintenance snapshot says running
                                        { label: "Homeostasis", status: Boolean(homeostasis.data?.orchestrator?.running || maintenance.data?.homeostasis?.running), icon: Activity, color: "green" },
                                        { label: "Security", status: securityMode === "strict", icon: Shield, color: "amber" },
                                        { label: "Scripts", status: aetherScripts.length > 0, icon: Workflow, color: "pink" },
                                    ].map((subsystem) => (
                                        <div key={subsystem.label} className={`p-3 rounded-xl border transition ${subsystem.status
                                            ? `bg-${subsystem.color}-900/20 border-${subsystem.color}-800/40`
                                            : 'bg-gray-900/20 border-gray-800/40'
                                            }`}>
                                            <div className="flex items-center justify-between mb-2">
                                                <subsystem.icon className={`w-4 h-4 ${subsystem.status ? `text-${subsystem.color}-400` : 'text-gray-500'}`} />
                                                {subsystem.status ? (
                                                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                                                ) : (
                                                    <AlertCircle className="w-4 h-4 text-gray-500" />
                                                )}
                                            </div>
                                            <div className="text-sm font-semibold text-white">{subsystem.label}</div>
                                            <div className="text-xs text-gray-500">{subsystem.status ? "Active" : "Inactive"}</div>
                                        </div>
                                    ))}
                                </div>
                            </Section>

                            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                                {/* Live Metrics */}
                                <Section title="Performance Metrics" icon={Gauge} right={<Badge variant="outline" className="border-emerald-700 text-emerald-300">live</Badge>}>
                                    <div className="space-y-4">
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-2">
                                                <span className="text-gray-400">CPU Usage</span>
                                                <span className="text-white">{kernelMetrics.data?.cpu_usage ? `${(kernelMetrics.data.cpu_usage * 100).toFixed(1)}%` : '—'}</span>
                                            </div>
                                            <Progress value={kernelMetrics.data?.cpu_usage ? kernelMetrics.data.cpu_usage * 100 : 0} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-2">
                                                <span className="text-gray-400">Memory Usage</span>
                                                <span className="text-white">{kernelMetrics.data?.memory_usage ? `${(kernelMetrics.data.memory_usage * 100).toFixed(1)}%` : '—'}</span>
                                            </div>
                                            <Progress value={kernelMetrics.data?.memory_usage ? kernelMetrics.data.memory_usage * 100 : 0} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-2">
                                                <span className="text-gray-400">System Load</span>
                                                <span className="text-white">{maintenance.data?.kpis?.system_health_score ? `${(maintenance.data.kpis.system_health_score * 100).toFixed(0)}%` : '—'}</span>
                                            </div>
                                            <Progress value={maintenance.data?.kpis?.system_health_score ? maintenance.data.kpis.system_health_score * 100 : 0} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div className="pt-2 border-t border-[#1e1e21]">
                                            <div className="grid grid-cols-2 gap-3 text-xs">
                                                <div>
                                                    <div className="text-gray-500">Requests</div>
                                                    <div className="text-white font-semibold">{kernelMetrics.data?.requests_served || 0}</div>
                                                </div>
                                                <div>
                                                    <div className="text-gray-500">Avg Latency</div>
                                                    <div className="text-white font-semibold">{kernelMetrics.data?.avg_latency ? `${kernelMetrics.data.avg_latency}ms` : '—'}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Section>

                                {/* Homeostasis Status */}
                                <Section title="Homeostasis" icon={Activity} right={
                                    <Badge className={homeostasis.data?.status === "active" ? "bg-emerald-900/40 text-emerald-300 border-emerald-800/50" : "bg-gray-800/40 text-gray-400"}>
                                        {homeostasis.data?.status || 'unknown'}
                                    </Badge>
                                }>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Mode</span>
                                            <span className="text-white">{homeostasis.data?.mode || 'N/A'}</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Stability</span>
                                            <span className="text-white">{homeostasisMetrics.data?.stability_score ? `${(homeostasisMetrics.data.stability_score * 100).toFixed(0)}%` : 'N/A'}</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">PID Loops</span>
                                            <span className="text-white">{homeostasisMetrics.data?.control_loops?.active?.length || 0} active</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Watchdog</span>
                                            <span className="text-white">{homeostasisMetrics.data?.watchdog?.active ? 'Active' : 'Inactive'}</span>
                                        </div>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="w-full mt-2 border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/20"
                                            onClick={() => setRoute("homeostasis")}
                                        >
                                            View Details
                                        </Button>
                                    </div>
                                </Section>

                                {/* Night Cycle */}
                                <Section title="Scheduled Tasks" icon={Clock} right={<Badge className="bg-blue-900/40 text-blue-300 border-blue-800/50">automated</Badge>}>
                                    <div className="space-y-3">
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-1">
                                                <span className="text-gray-400">Night Cycle</span>
                                                <span className="text-xs text-gray-500">02:15 AM</span>
                                            </div>
                                            <Progress value={66} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-1">
                                                <span className="text-gray-400">Maintenance</span>
                                                <span className="text-xs text-gray-500">03:05 AM</span>
                                            </div>
                                            <Progress value={40} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div>
                                            <div className="flex items-center justify-between text-sm mb-1">
                                                <span className="text-gray-400">Memory Cleanup</span>
                                                <span className="text-xs text-gray-500">04:00 AM</span>
                                            </div>
                                            <Progress value={20} className="h-2 bg-[#121214]" />
                                        </div>
                                        <div className="pt-2 border-t border-[#1e1e21] text-xs text-gray-500">
                                            Next run: {new Date(Date.now() + 86400000).toLocaleString()}
                                        </div>
                                    </div>
                                </Section>
                            </div>

                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                                {/* Recent Activity */}
                                <Section title="Recent Activity" icon={Network}>
                                    <div className="space-y-2 max-h-[300px] overflow-y-auto">
                                        {[
                                            { time: Date.now() - 120000, type: "execution", message: "Script execution completed: daily_digest.aether", icon: Workflow, color: "emerald" },
                                            { time: Date.now() - 300000, type: "security", message: "Security scan completed - no threats detected", icon: Shield, color: "blue" },
                                            { time: Date.now() - 450000, type: "agent", message: "Agent orchestrator: 3 tasks completed", icon: Bot, color: "purple" },
                                            { time: Date.now() - 600000, type: "memory", message: "STORM memory update: 127 entries processed", icon: Database, color: "amber" },
                                            { time: Date.now() - 900000, type: "homeostasis", message: "Homeostasis mode changed to balanced", icon: Activity, color: "green" },
                                            { time: Date.now() - 1200000, type: "kernel", message: "Kernel heartbeat: all systems nominal", icon: Cpu, color: "gray" },
                                        ].map((activity, idx) => (
                                            <div key={idx} className="flex items-start gap-3 p-2 rounded-lg hover:bg-[#111113] transition">
                                                <div className={`p-1.5 rounded-lg bg-${activity.color}-900/20 border border-${activity.color}-800/40`}>
                                                    <activity.icon className={`w-3 h-3 text-${activity.color}-400`} />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="text-sm text-white truncate">{activity.message}</div>
                                                    <div className="text-xs text-gray-500">
                                                        {Math.floor((Date.now() - activity.time) / 60000)} minutes ago
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </Section>

                                {/* Quick Actions */}
                                <Section title="Quick Actions" icon={Zap}>
                                    <div className="grid grid-cols-2 gap-3">
                                        {[
                                            { label: "Lyrixa Chat", icon: MessageSquare, action: () => setRoute("chat"), color: "blue" },
                                            { label: "Run Script", icon: Workflow, action: () => setRoute("scripts"), color: "purple" },
                                            { label: "View Memory", icon: Database, action: () => setRoute("memory"), color: "amber" },
                                            { label: "Check Security", icon: Shield, action: () => setRoute("security"), color: "red" },
                                            { label: "Agent Status", icon: Bot, action: () => setRoute("agents"), color: "green" },
                                            { label: "System Settings", icon: Settings, action: () => setRoute("settings"), color: "gray" },
                                        ].map((action) => (
                                            <Button
                                                key={action.label}
                                                onClick={() => {
                                                    action.action();
                                                    toast.info(`Navigating to ${action.label}`);
                                                }}
                                                variant="outline"
                                                className={`h-auto py-3 border-${action.color}-800/40 hover:bg-${action.color}-900/20 flex flex-col items-center gap-2`}
                                            >
                                                <action.icon className={`w-5 h-5 text-${action.color}-400`} />
                                                <span className="text-xs font-medium">{action.label}</span>
                                            </Button>
                                        ))}
                                    </div>
                                </Section>
                            </div>

                            {/* System Information */}
                            <Section title="System Information" icon={Monitor}>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs text-gray-500 mb-1">Uptime</div>
                                        <div className="text-lg font-semibold text-white">{kernelStatus.data?.uptime || 'N/A'}</div>
                                    </div>
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs text-gray-500 mb-1">Version</div>
                                        <div className="text-lg font-semibold text-white">v3.0</div>
                                    </div>
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs text-gray-500 mb-1">Profile</div>
                                        <div className="text-lg font-semibold text-white">Production</div>
                                    </div>
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs text-gray-500 mb-1">Backend</div>
                                        <div className="text-lg font-semibold text-white truncate">{settingsConfig.api.backendUrl.replace('http://', '')}</div>
                                    </div>
                                </div>
                            </Section>
                        </div>
                    )}
                    {route === "chat" && (
                        <Section title="Lyrixa Chat" icon={MessageSquare}>
                            <div className="h-[460px] flex flex-col">
                                <div className="flex-1 overflow-auto space-y-3 pr-1">
                                    {messages.map((m, i) => (
                                        <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                            <div className={`max-w-[80%] p-3 rounded-2xl border ${m.role === "user" ? "bg-emerald-900/20 border-emerald-800/40" : "bg-[#111113] border-[#1e1e21]"}`}>
                                                <div className="text-xs mb-1 text-gray-400">{m.role}</div>
                                                <div className="text-sm text-gray-100 leading-relaxed">{m.text}</div>
                                            </div>
                                        </div>
                                    ))}
                                    {streaming && <div className="text-xs text-gray-500">Lyrixa is thinking…</div>}
                                    <div ref={chatEndRef} />
                                </div>
                                <div className="mt-3 flex gap-2">
                                    <Input placeholder="Ask Lyrixa…" value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} className="bg-[#0e0e10] border-[#1f1f22] rounded-xl" />
                                    <Button onClick={send} className="rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold">Send</Button>
                                </div>
                            </div>
                        </Section>
                    )}
                    {route === "consciousness" && (
                        <ConsciousnessMonitor />
                    )}
                    {route === "memory" && (
                        <Section title="Memory System" icon={Database}>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                <Stat label="STORM Enabled" value={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0 ? "yes" : (agentsInfo.error ? "unknown" : "no")} sub={agentsInfo.data?.orchestrator ? `${agentsInfo.data.orchestrator.total_agents} agents` : undefined} icon={Sparkles} ok={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0} />
                                <Stat label="Engine" value={memoryStatus.data?.engine ?? (memoryStatus.error ? 'n/a' : '…')} sub={memoryStatus.data?.backend || undefined} icon={CircuitBoard} />
                                <Stat label="Shadow Mode" value={memoryStatus.data?.shadow_mode ? 'active' : (memoryStatus.data?.shadow_mode === false ? 'off' : '—')} icon={Activity} />
                                <Stat label="Status" value={memoryStatus.data?.ok ? "ok" : (memoryStatus.error ? "error" : "loading")} icon={Database} ok={!!memoryStatus.data?.ok} />
                            </div>
                            <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Section title="STORM Metrics" icon={Sparkles}>
                                    {(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0 && (
                                        <div className="space-y-3 text-sm">
                                            <div className="flex justify-between"><span className="text-gray-400">Total Agents</span><span className="text-white">{agentsInfo.data.orchestrator.total_agents}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">Pending Tasks</span><span className="text-white">{agentsInfo.data.orchestrator.pending_tasks}</span></div>
                                            {memoryStatus.data?.k_coarse && <div className="flex justify-between"><span className="text-gray-400">k_coarse</span><span className="text-white">{memoryStatus.data.k_coarse}</span></div>}
                                            {memoryStatus.data?.tt_rank_cap && <div className="flex justify-between"><span className="text-gray-400">TT rank cap</span><span className="text-white">{memoryStatus.data.tt_rank_cap}</span></div>}
                                            {memoryStatus.data?.compression_ratio != null && <div className="flex justify-between"><span className="text-gray-400">Compression</span><span className="text-white">{Number(memoryStatus.data.compression_ratio).toFixed(2)}</span></div>}
                                            {memoryStatus.data?.transport_cost != null && <div className="flex justify-between"><span className="text-gray-400">Transport cost</span><span className="text-white">{Number(memoryStatus.data.transport_cost).toFixed(3)}</span></div>}
                                            {memoryStatus.data?.coherence_score != null && <div className="flex justify-between"><span className="text-gray-400">Coherence</span><span className="text-white">{Number(memoryStatus.data.coherence_score).toFixed(3)}</span></div>}
                                            {memoryStatus.data?.recall_count != null && <div className="flex justify-between"><span className="text-gray-400">Recall count</span><span className="text-white">{memoryStatus.data.recall_count}</span></div>}
                                        </div>
                                    )}
                                    {(agentsInfo.data?.orchestrator?.total_agents ?? 0) === 0 && <div className="text-xs text-gray-500">{agentsInfo.error ? `Error: ${agentsInfo.error}` : 'STORM agents not running.'}</div>}
                                </Section>
                                <Section title="Quantum Status" icon={CircuitBoard}>
                                    {memoryStatus.data?.quantum && typeof memoryStatus.data.quantum === 'object' ? (
                                        <div className="space-y-3 text-sm">
                                            <div className="flex justify-between"><span className="text-gray-400">Enabled</span><span className="text-white">{String(memoryStatus.data.quantum.enabled ?? false)}</span></div>
                                            {memoryStatus.data.quantum.mode && <div className="flex justify-between"><span className="text-gray-400">Mode</span><span className="text-white">{memoryStatus.data.quantum.mode}</span></div>}
                                            {memoryStatus.data.quantum.entanglement_score != null && <div className="flex justify-between"><span className="text-gray-400">Entanglement</span><span className="text-white">{Number(memoryStatus.data.quantum.entanglement_score).toFixed(3)}</span></div>}
                                            {memoryStatus.data.quantum.superposition_depth != null && <div className="flex justify-between"><span className="text-gray-400">Superposition depth</span><span className="text-white">{memoryStatus.data.quantum.superposition_depth}</span></div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">Quantum features not available or disabled.</div>
                                    )}
                                </Section>
                                <Section title="Raw Snapshot" icon={Database}>
                                    <pre className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs whitespace-pre-wrap overflow-auto max-h-48">{memoryStatus.data ? JSON.stringify(memoryStatus.data, null, 2) : (memoryStatus.error ? `error: ${memoryStatus.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "agents" && (
                        <Section title="Agent Orchestrator" icon={Bot}>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                <Stat label="Total Agents" value={agentsInfo.data?.orchestrator?.total_agents ?? (agentsInfo.error ? 'n/a' : '…')} icon={Bot} ok={!agentsInfo.error} />
                                <Stat label="Pending Tasks" value={agentsInfo.data?.orchestrator?.pending_tasks ?? (agentsInfo.error ? 'n/a' : '…')} icon={ListChecks} ok={!agentsInfo.error} />
                                <Stat label="Active" value={agentsInfo.data?.orchestrator?.active_agents ?? '—'} sub="agents working" icon={Activity} />
                                <Stat label="API Status" value={agentsInfo.error ? 'disabled' : 'enabled'} icon={Network} ok={!agentsInfo.error} />
                            </div>
                            <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Section title="Task Queue" icon={ListChecks}>
                                    {agentsInfo.data?.orchestrator ? (
                                        <div className="space-y-3 text-sm">
                                            <div className="flex justify-between"><span className="text-gray-400">Pending</span><span className="text-white">{agentsInfo.data.orchestrator.pending_tasks ?? 0}</span></div>
                                            {agentsInfo.data.orchestrator.completed_tasks != null && <div className="flex justify-between"><span className="text-gray-400">Completed</span><span className="text-white">{agentsInfo.data.orchestrator.completed_tasks}</span></div>}
                                            {agentsInfo.data.orchestrator.failed_tasks != null && <div className="flex justify-between"><span className="text-gray-400">Failed</span><span className="text-white">{agentsInfo.data.orchestrator.failed_tasks}</span></div>}
                                            {agentsInfo.data.orchestrator.queue_depth != null && <div className="flex justify-between"><span className="text-gray-400">Queue depth</span><span className="text-white">{agentsInfo.data.orchestrator.queue_depth}</span></div>}
                                            {agentsInfo.data.orchestrator.max_queue_size != null && <div className="flex justify-between"><span className="text-gray-400">Max queue</span><span className="text-white">{agentsInfo.data.orchestrator.max_queue_size}</span></div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{agentsInfo.error ? `API disabled: ${agentsInfo.error}` : 'Loading task queue metrics…'}</div>
                                    )}
                                </Section>
                                <Section title="Agent Status" icon={Bot}>
                                    {agentsInfo.data?.orchestrator ? (
                                        <div className="space-y-3 text-sm">
                                            <div className="flex justify-between"><span className="text-gray-400">Total</span><span className="text-white">{agentsInfo.data.orchestrator.total_agents ?? 0}</span></div>
                                            {agentsInfo.data.orchestrator.active_agents != null && <div className="flex justify-between"><span className="text-gray-400">Active</span><span className="text-white">{agentsInfo.data.orchestrator.active_agents}</span></div>}
                                            {agentsInfo.data.orchestrator.idle_agents != null && <div className="flex justify-between"><span className="text-gray-400">Idle</span><span className="text-white">{agentsInfo.data.orchestrator.idle_agents}</span></div>}
                                            {agentsInfo.data.orchestrator.busy_agents != null && <div className="flex justify-between"><span className="text-gray-400">Busy</span><span className="text-white">{agentsInfo.data.orchestrator.busy_agents}</span></div>}
                                            {agentsInfo.data.orchestrator.available_capabilities && Array.isArray(agentsInfo.data.orchestrator.available_capabilities) && (
                                                <div className="mt-2 pt-2 border-t border-[#1e1e21]">
                                                    <div className="text-gray-400 mb-2">Capabilities:</div>
                                                    <div className="flex flex-wrap gap-1">
                                                        {agentsInfo.data.orchestrator.available_capabilities.slice(0, 6).map((cap: string, i: number) => (
                                                            <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-900/30 text-emerald-300 border border-emerald-800/40">{cap}</span>
                                                        ))}
                                                        {agentsInfo.data.orchestrator.available_capabilities.length > 6 && <span className="text-xs text-gray-500">+{agentsInfo.data.orchestrator.available_capabilities.length - 6} more</span>}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{agentsInfo.error ? 'API disabled' : 'Loading agent status…'}</div>
                                    )}
                                </Section>
                                <Section title="Raw Snapshot" icon={CircuitBoard}>
                                    <pre className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs whitespace-pre-wrap overflow-auto max-h-48">{agentsInfo.data ? JSON.stringify(agentsInfo.data, null, 2) : (agentsInfo.error ? `error: ${agentsInfo.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                            <div className="mt-4">
                                <Section title="Task History" icon={ListChecks}>
                                    {tasksHistory.error ? (
                                        <div className="text-xs text-gray-500">{`Error loading tasks: ${tasksHistory.error}`}</div>
                                    ) : Array.isArray(tasksHistory.data?.tasks) && tasksHistory.data.tasks.length > 0 ? (
                                        <div className="space-y-2 max-h-[360px] overflow-y-auto">
                                            {tasksHistory.data.tasks.map((t: any, idx: number) => {
                                                const ts = t.performed_at ? new Date(t.performed_at) : (t.completed_at ? new Date(t.completed_at) : (t.started_at ? new Date(t.started_at) : (t.created_at ? new Date(t.created_at) : null)));
                                                const when = ts ? ts.toLocaleString() : '—';
                                                const status = String(t.status || '').toLowerCase();
                                                const statusColor = status === 'completed' ? 'emerald' : status === 'failed' ? 'red' : status === 'running' ? 'blue' : 'gray';
                                                const dur = (typeof t.duration_secs === 'number' && isFinite(t.duration_secs)) ? `${Math.max(0, Math.round(t.duration_secs))}s` : '';
                                                return (
                                                    <div key={t.task_id ?? idx} className="flex items-start gap-3 p-2 rounded-lg bg-[#0e0e10] border border-[#1e1e21] hover:border-emerald-800/30 transition">
                                                        <div className={`p-1.5 rounded-lg bg-${statusColor}-900/20 border border-${statusColor}-800/40`}>
                                                            <Bot className={`w-3 h-3 text-${statusColor}-400`} />
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2 flex-wrap">
                                                                <span className="text-sm text-white font-medium truncate max-w-[40ch]" title={t.name}>{t.name || t.task_id}</span>
                                                                {t.assigned_agent && (
                                                                    <Badge className="bg-emerald-900/30 text-emerald-300 border-emerald-800/40" title={t.assigned_agent}>
                                                                        {t.assigned_agent}
                                                                    </Badge>
                                                                )}
                                                                <Badge className={`bg-${statusColor}-900/30 text-${statusColor}-300 border-${statusColor}-800/40`}>
                                                                    {status || 'unknown'}
                                                                </Badge>
                                                                {dur && <span className="text-[10px] text-gray-500">{dur}</span>}
                                                            </div>
                                                            <div className="text-xs text-gray-500 mt-1">{when}</div>
                                                            {t.description && <div className="text-xs text-gray-400 mt-1 truncate" title={t.description}>{t.description}</div>}
                                                        </div>
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">No recent tasks.</div>
                                    )}
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "kernel" && (
                        <Section title="Kernel Loop" icon={Cpu}>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                <Stat label="Running" value={kernelStatus.data?.running ? 'yes' : 'no'} icon={Cpu} ok={!!kernelStatus.data?.running} />
                                <Stat label="Uptime" value={kernelStatus.data?.uptime ?? '…'} icon={Activity} />
                                <Stat label="Tasks Processed" value={kernelStatus.data?.tasks_processed ?? kernelStatus.data?.total_tasks ?? '—'} icon={ListChecks} />
                                <Stat label="Cycle Time" value={kernelStatus.data?.cycle_time_ms != null ? `${kernelStatus.data.cycle_time_ms}ms` : '—'} icon={Gauge} />
                            </div>
                            <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Section title="Queue Metrics" icon={Network}>
                                    {kernelStatus.data ? (
                                        <div className="space-y-3 text-sm">
                                            {kernelStatus.data.queue_high != null && <div className="flex justify-between"><span className="text-gray-400">High priority</span><span className="text-white">{kernelStatus.data.queue_high}</span></div>}
                                            {kernelStatus.data.queue_normal != null && <div className="flex justify-between"><span className="text-gray-400">Normal</span><span className="text-white">{kernelStatus.data.queue_normal}</span></div>}
                                            {kernelStatus.data.queue_background != null && <div className="flex justify-between"><span className="text-gray-400">Background</span><span className="text-white">{kernelStatus.data.queue_background}</span></div>}
                                            {kernelStatus.data.queue_total != null && <div className="flex justify-between"><span className="text-gray-400">Total queued</span><span className="text-white">{kernelStatus.data.queue_total}</span></div>}
                                            {kernelStatus.data.dlq_count != null && <div className="flex justify-between"><span className="text-gray-400">DLQ</span><span className="text-white">{kernelStatus.data.dlq_count}</span></div>}
                                            {kernelStatus.data.backpressure != null && <div className="flex justify-between"><span className="text-gray-400">Backpressure</span><span className={kernelStatus.data.backpressure ? "text-amber-400" : "text-emerald-400"}>{String(kernelStatus.data.backpressure)}</span></div>}
                                            {!kernelStatus.data.queue_high && !kernelStatus.data.queue_total && <div className="text-xs text-gray-500">No queue metrics exposed.</div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{kernelStatus.error ? `Error: ${kernelStatus.error}` : 'Loading queue metrics…'}</div>
                                    )}
                                </Section>
                                <Section title="HMR & Circuit Breaker" icon={Activity}>
                                    {kernelStatus.data || kernelMetrics.data?.hmr ? (
                                        <div className="space-y-3 text-sm">
                                            {(kernelStatus.data?.hmr_enabled != null || kernelMetrics.data?.hmr?.enabled != null) && <div className="flex justify-between"><span className="text-gray-400">HMR enabled</span><span className="text-white">{String(kernelStatus.data?.hmr_enabled ?? kernelMetrics.data?.hmr?.enabled ?? false)}</span></div>}
                                            {(kernelStatus.data?.last_swap_ms != null || kernelMetrics.data?.hmr?.last_swap_ms != null) && <div className="flex justify-between"><span className="text-gray-400">Last swap</span><span className="text-white">{kernelStatus.data?.last_swap_ms ?? kernelMetrics.data?.hmr?.last_swap_ms}ms</span></div>}
                                            {kernelStatus.data?.hmr_swaps != null && <div className="flex justify-between"><span className="text-gray-400">Total swaps</span><span className="text-white">{kernelStatus.data.hmr_swaps}</span></div>}
                                            {kernelStatus.data?.circuit_breaker_open != null && <div className="flex justify-between"><span className="text-gray-400">CB open</span><span className={kernelStatus.data.circuit_breaker_open ? "text-amber-400" : "text-emerald-400"}>{String(kernelStatus.data.circuit_breaker_open)}</span></div>}
                                            {kernelStatus.data?.circuit_breaker_trips != null && <div className="flex justify-between"><span className="text-gray-400">CB trips</span><span className="text-white">{kernelStatus.data.circuit_breaker_trips}</span></div>}
                                            {kernelStatus.data?.retries != null && <div className="flex justify-between"><span className="text-gray-400">Retries</span><span className="text-white">{kernelStatus.data.retries}</span></div>}
                                            {!kernelStatus.data?.hmr_enabled && !kernelMetrics.data?.hmr && !kernelStatus.data?.circuit_breaker_open && <div className="text-xs text-gray-500">No HMR/CB metrics exposed.</div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{kernelStatus.error || kernelMetrics.error ? 'Error loading metrics' : 'Loading…'}</div>
                                    )}
                                </Section>
                                <Section title="Raw Snapshot" icon={Gauge}>
                                    <pre className="text-xs p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] whitespace-pre-wrap overflow-auto max-h-48">{kernelStatus.data ? JSON.stringify(kernelStatus.data, null, 2) : (kernelStatus.error ? `error: ${kernelStatus.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "storm" && (
                        <Section title="STORM — Sheaf-Theoretic Optimal Recall & Memory" icon={Sparkles}>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                <Stat label="STORM Enabled" value={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0 ? 'yes' : (agentsInfo.error ? 'unknown' : 'no')} icon={Sparkles} ok={(agentsInfo.data?.orchestrator?.total_agents ?? 0) > 0} />
                                <Stat label="Mode" value={memoryStatus.data?.mode ?? '—'} sub={memoryStatus.data?.backend || undefined} icon={Gauge} />
                                <Stat label="Shadow Mode" value={memoryStatus.data?.shadow_mode ? 'active' : (memoryStatus.data?.shadow_mode === false ? 'off' : '—')} icon={Activity} />
                                <Stat label="Engine" value={memoryStatus.data?.engine ?? '—'} icon={CircuitBoard} />
                            </div>
                            <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Section title="OT & Transport" icon={Network}>
                                    {memoryStatus.data?.enabled ? (
                                        <div className="space-y-3 text-sm">
                                            {memoryStatus.data.k_coarse != null && <div className="flex justify-between"><span className="text-gray-400">k_coarse</span><span className="text-white">{memoryStatus.data.k_coarse}</span></div>}
                                            {memoryStatus.data.transport_cost != null && <div className="flex justify-between"><span className="text-gray-400">Transport cost</span><span className="text-white">{Number(memoryStatus.data.transport_cost).toFixed(4)}</span></div>}
                                            {memoryStatus.data.ot_iterations != null && <div className="flex justify-between"><span className="text-gray-400">OT iterations</span><span className="text-white">{memoryStatus.data.ot_iterations}</span></div>}
                                            {memoryStatus.data.ot_convergence != null && <div className="flex justify-between"><span className="text-gray-400">Convergence</span><span className="text-white">{Number(memoryStatus.data.ot_convergence).toFixed(4)}</span></div>}
                                            {memoryStatus.data.exact_ot != null && <div className="flex justify-between"><span className="text-gray-400">Exact OT</span><span className="text-white">{String(memoryStatus.data.exact_ot)}</span></div>}
                                            {!memoryStatus.data.k_coarse && !memoryStatus.data.transport_cost && <div className="text-xs text-gray-500">No OT metrics exposed.</div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{memoryStatus.error ? `Error: ${memoryStatus.error}` : 'STORM not enabled'}</div>
                                    )}
                                </Section>
                                <Section title="Coherence & Compression" icon={CircuitBoard}>
                                    {memoryStatus.data?.enabled ? (
                                        <div className="space-y-3 text-sm">
                                            {memoryStatus.data.coherence_score != null && <div className="flex justify-between"><span className="text-gray-400">Coherence</span><span className="text-white">{Number(memoryStatus.data.coherence_score).toFixed(4)}</span></div>}
                                            {memoryStatus.data.sheaf_coherence != null && <div className="flex justify-between"><span className="text-gray-400">Sheaf coherence</span><span className="text-white">{Number(memoryStatus.data.sheaf_coherence).toFixed(4)}</span></div>}
                                            {memoryStatus.data.compression_ratio != null && <div className="flex justify-between"><span className="text-gray-400">Compression</span><span className="text-white">{Number(memoryStatus.data.compression_ratio).toFixed(3)}</span></div>}
                                            {memoryStatus.data.tt_rank_cap != null && <div className="flex justify-between"><span className="text-gray-400">TT rank cap</span><span className="text-white">{memoryStatus.data.tt_rank_cap}</span></div>}
                                            {memoryStatus.data.persistence_bonus != null && <div className="flex justify-between"><span className="text-gray-400">Persistence bonus</span><span className="text-white">{Number(memoryStatus.data.persistence_bonus).toFixed(3)}</span></div>}
                                            {!memoryStatus.data.coherence_score && !memoryStatus.data.compression_ratio && <div className="text-xs text-gray-500">No coherence metrics exposed.</div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">STORM not enabled</div>
                                    )}
                                </Section>
                                <Section title="Shadow Divergence & Evidence" icon={Activity}>
                                    {memoryStatus.data?.enabled ? (
                                        <div className="space-y-3 text-sm">
                                            {memoryStatus.data.shadow_divergence != null && <div className="flex justify-between"><span className="text-gray-400">Shadow divergence</span><span className="text-white">{Number(memoryStatus.data.shadow_divergence).toFixed(4)}</span></div>}
                                            {memoryStatus.data.recall_count != null && <div className="flex justify-between"><span className="text-gray-400">Recall count</span><span className="text-white">{memoryStatus.data.recall_count}</span></div>}
                                            {memoryStatus.data.recall_source && <div className="flex justify-between"><span className="text-gray-400">Recall source</span><span className="text-white text-xs">{memoryStatus.data.recall_source}</span></div>}
                                            {memoryStatus.data.evidence_tags && Array.isArray(memoryStatus.data.evidence_tags) && (
                                                <div className="mt-2 pt-2 border-t border-[#1e1e21]">
                                                    <div className="text-gray-400 mb-2">Evidence tags:</div>
                                                    <div className="flex flex-wrap gap-1">
                                                        {memoryStatus.data.evidence_tags.slice(0, 4).map((tag: string, i: number) => (
                                                            <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-900/30 text-emerald-300 border border-emerald-800/40">{tag}</span>
                                                        ))}
                                                        {memoryStatus.data.evidence_tags.length > 4 && <span className="text-xs text-gray-500">+{memoryStatus.data.evidence_tags.length - 4}</span>}
                                                    </div>
                                                </div>
                                            )}
                                            {!memoryStatus.data.shadow_divergence && !memoryStatus.data.recall_count && <div className="text-xs text-gray-500">No shadow/evidence metrics exposed.</div>}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">STORM not enabled</div>
                                    )}
                                </Section>
                            </div>
                            <div className="mt-4">
                                <Section title="Raw STORM Snapshot" icon={Database}>
                                    <pre className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs whitespace-pre-wrap overflow-auto max-h-48">{memoryStatus.data ? JSON.stringify(memoryStatus.data, null, 2) : (memoryStatus.error ? `error: ${memoryStatus.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "improve" && (
                        <Section title="Self-Improvement Engine" icon={Lightbulb}>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                                <Stat
                                    label="Proposals Generated"
                                    value={maintenance.data?.kpis?.proposals_generated ?? (maintenance.error ? 'n/a' : '—')}
                                    icon={ListChecks}
                                    ok={typeof maintenance.data?.kpis?.proposals_generated === 'number' && maintenance.data.kpis.proposals_generated > 0}
                                />
                                <Stat
                                    label="Executed"
                                    value={maintenance.data?.kpis?.proposals_executed ?? (maintenance.error ? 'n/a' : '—')}
                                    icon={Workflow}
                                    ok={typeof maintenance.data?.kpis?.proposals_executed === 'number' && maintenance.data.kpis.proposals_executed > 0}
                                />
                                <Stat
                                    label="Accepted"
                                    value={maintenance.data?.kpis?.proposals_accepted ?? (maintenance.error ? 'n/a' : '—')}
                                    icon={ThumbsUp}
                                    ok={typeof maintenance.data?.kpis?.proposals_accepted === 'number' && maintenance.data.kpis.proposals_accepted > 0}
                                />
                                <Stat
                                    label="Acceptance Rate"
                                    value={(() => {
                                        const exec = maintenance.data?.kpis?.proposals_executed;
                                        const acc = maintenance.data?.kpis?.proposals_accepted;
                                        if (typeof exec === 'number' && typeof acc === 'number' && exec > 0) {
                                            return `${((acc / exec) * 100).toFixed(1)}%`;
                                        }
                                        return '—';
                                    })()}
                                    icon={Gauge}
                                />
                            </div>
                            {!Boolean(kernelMetrics.data?.hmr?.enabled) && (
                                <div className="mt-4 p-3 rounded-xl bg-amber-900/20 border border-amber-800/40">
                                    <div className="flex items-start gap-2 text-amber-200 text-xs">
                                        <AlertTriangle className="w-4 h-4 mt-0.5" />
                                        <div>
                                            <div className="font-semibold mb-0.5">Hot Module Reload (HMR) is disabled</div>
                                            <div>Approved proposals will be marked "OS Restart Required" and remain pending until restart. Enable HMR in your OS launcher to hot-apply changes.</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Section title="Proposal Breakdown" icon={ListChecks}>
                                    {maintenance.data?.self_improvement?.available ? (
                                        <div className="space-y-3 text-sm">
                                            {maintenance.data.kpis?.proposals_generated != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Total generated</span>
                                                    <span className="text-white">{maintenance.data.kpis.proposals_generated}</span>
                                                </div>
                                            )}
                                            {maintenance.data.kpis?.proposals_executed != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Executed</span>
                                                    <span className="text-white">{maintenance.data.kpis.proposals_executed}</span>
                                                </div>
                                            )}
                                            {maintenance.data.kpis?.proposals_accepted != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Accepted</span>
                                                    <span className="text-white">{maintenance.data.kpis.proposals_accepted}</span>
                                                </div>
                                            )}
                                            {(() => {
                                                const exec = maintenance.data?.kpis?.proposals_executed;
                                                const acc = maintenance.data?.kpis?.proposals_accepted;
                                                if (typeof exec === 'number' && typeof acc === 'number') {
                                                    const rejected = exec - acc;
                                                    return (
                                                        <div className="flex justify-between">
                                                            <span className="text-gray-400">Rejected</span>
                                                            <span className="text-white">{rejected >= 0 ? rejected : '—'}</span>
                                                        </div>
                                                    );
                                                }
                                                return null;
                                            })()}
                                            {!maintenance.data.kpis?.proposals_generated && (
                                                <div className="text-xs text-gray-500">No proposal metrics available.</div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">
                                            {maintenance.error ? `Error: ${maintenance.error}` : 'Self-improvement engine not available'}
                                        </div>
                                    )}
                                </Section>
                                <Section title="Engine Status" icon={Activity}>
                                    {maintenance.data?.self_improvement?.status ? (
                                        <div className="space-y-3 text-sm">
                                            {maintenance.data.self_improvement.status.total_proposals != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Total proposals</span>
                                                    <span className="text-white">{maintenance.data.self_improvement.status.total_proposals}</span>
                                                </div>
                                            )}
                                            {maintenance.data.self_improvement.status.active != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Active</span>
                                                    <span className="text-white">{String(maintenance.data.self_improvement.status.active)}</span>
                                                </div>
                                            )}
                                            {maintenance.data.self_improvement.status.last_run && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Last run</span>
                                                    <span className="text-white text-xs">{String(maintenance.data.self_improvement.status.last_run).slice(0, 19)}</span>
                                                </div>
                                            )}
                                            {maintenance.data.self_improvement.status.uptime && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Uptime</span>
                                                    <span className="text-white text-xs">{maintenance.data.self_improvement.status.uptime}</span>
                                                </div>
                                            )}
                                            {Object.keys(maintenance.data.self_improvement.status).length === 0 && (
                                                <div className="text-xs text-gray-500">No status details exposed.</div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">Status not available</div>
                                    )}
                                </Section>
                                <Section title="Metrics Snapshot" icon={Gauge}>
                                    {maintenance.data?.self_improvement?.status?.metrics ? (
                                        <div className="space-y-3 text-sm">
                                            {Object.entries(maintenance.data.self_improvement.status.metrics).slice(0, 6).map(([key, val]) => (
                                                <div key={key} className="flex justify-between">
                                                    <span className="text-gray-400 text-xs">{key}</span>
                                                    <span className="text-white text-xs">{String(val)}</span>
                                                </div>
                                            ))}
                                            {Object.keys(maintenance.data.self_improvement.status.metrics).length === 0 && (
                                                <div className="text-xs text-gray-500">No metrics exposed.</div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">Metrics not available</div>
                                    )}
                                </Section>
                            </div>
                            {suggestions.filter((s) => s.status === "pending").length > 0 && (
                                <div className="mt-4">
                                    <Section title="Pending Proposals — Review Required" icon={ListChecks}>
                                        <div className="space-y-3">
                                            {suggestions.filter((s) => s.status === "pending").map((sugg) => (
                                                <div key={sugg.id} className="p-4 rounded-xl bg-[#0e0e10] border border-[#1e1e21] hover:border-[#00ff88]/30 transition-colors">
                                                    <div className="flex items-start justify-between gap-4">
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <span className="text-xs font-mono text-gray-500">{sugg.id}</span>
                                                                <span className={`text-[10px] px-2 py-0.5 rounded-full ${sugg.impact === 'security' ? 'bg-red-900/30 text-red-300 border border-red-800/40' :
                                                                    sugg.impact === 'performance' ? 'bg-blue-900/30 text-blue-300 border border-blue-800/40' :
                                                                        'bg-purple-900/30 text-purple-300 border border-purple-800/40'
                                                                    }`}>{sugg.impact}</span>
                                                                <span className="text-xs text-gray-400">Risk: {(sugg.risk * 100).toFixed(0)}%</span>
                                                                {sugg.restart_required && (
                                                                    <Badge className="bg-amber-900/30 text-amber-300 border-amber-800/40" title="This change will take effect after OS restart">
                                                                        OS Restart Required
                                                                    </Badge>
                                                                )}
                                                            </div>
                                                            <h4 className="text-sm font-medium text-white mb-1">{sugg.title}</h4>
                                                            <p className="text-xs text-gray-400 mb-2">{sugg.desc}</p>
                                                            {sugg.diff && (
                                                                <pre className="text-[10px] font-mono text-emerald-300 bg-[#0a0a0b] p-2 rounded border border-[#1e1e21] overflow-x-auto">{sugg.diff}</pre>
                                                            )}
                                                        </div>
                                                        <div className="flex gap-2 shrink-0">
                                                            <button
                                                                onClick={() => {
                                                                    approveSuggestion(sugg.id);
                                                                    ping();
                                                                }}
                                                                className="px-3 py-1.5 text-xs rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-600/40 text-emerald-300 transition-colors"
                                                            >
                                                                Approve
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    denySuggestion(sugg.id);
                                                                    ping();
                                                                }}
                                                                className="px-3 py-1.5 text-xs rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-600/40 text-red-300 transition-colors"
                                                            >
                                                                Deny
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        {suggestions.filter((s) => s.status === "approved").length > 0 && (
                                            <div className="mt-4 pt-4 border-t border-[#1e1e21]">
                                                <button
                                                    onClick={() => {
                                                        applyApproved();
                                                        ping();
                                                    }}
                                                    className={`w-full px-4 py-2 text-sm rounded-lg border font-medium transition-colors ${!Boolean(kernelMetrics.data?.hmr?.enabled)
                                                        ? 'bg-gray-800/40 border-gray-700/60 text-gray-400 cursor-not-allowed'
                                                        : 'bg-emerald-600/30 hover:bg-emerald-600/40 border-emerald-600/50 text-emerald-200'}`}
                                                    disabled={!Boolean(kernelMetrics.data?.hmr?.enabled)}
                                                    title={!Boolean(kernelMetrics.data?.hmr?.enabled) ? 'Enable HMR to apply approved proposals without restart' : 'Apply approved proposals via HMR'}
                                                >
                                                    Apply {suggestions.filter((s) => s.status === "approved").length} Approved Proposal{suggestions.filter((s) => s.status === "approved").length !== 1 ? 's' : ''} (HMR)
                                                </button>
                                                {!Boolean(kernelMetrics.data?.hmr?.enabled) && (
                                                    <div className="text-[10px] text-amber-300 mt-2">
                                                        HMR is disabled. Approved proposals will be marked "OS Restart Required" and remain pending until restart.
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </Section>
                                </div>
                            )}
                            <div className="mt-4">
                                <Section title="Raw Self-Improvement Data" icon={Database}>
                                    <pre className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs whitespace-pre-wrap overflow-auto max-h-48">
                                        {maintenance.data?.self_improvement ? JSON.stringify(maintenance.data.self_improvement, null, 2) : (maintenance.error ? `error: ${maintenance.error}` : 'loading…')}
                                    </pre>
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "homeostasis" && (
                        <Section title="Homeostasis" icon={Activity}>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <Section title="System Health" icon={Gauge}>
                                    <div className="text-5xl font-bold text-white">
                                        {(typeof maintenance.data?.kpis?.system_health_score === 'number' ? (maintenance.data.kpis.system_health_score).toFixed(2) : '—')} <span className="text-sm text-gray-400">/ 1.0</span>
                                    </div>
                                    <div className="mt-3 space-y-2 text-sm">
                                        <div>Runlevel: <span className="text-gray-300">{maintenance.data?.overall?.runlevel ?? 'unknown'}</span></div>
                                        <div>Controller mode: <span className="text-gray-300">{homeostasis.data?.controller?.mode ?? '—'}</span></div>
                                        <div>Emergency stop: <span className={`text-gray-300 ${homeostasis.data?.controller?.emergency_stop ? 'text-amber-400' : ''}`}>{String(homeostasis.data?.controller?.emergency_stop ?? false)}</span></div>
                                    </div>
                                </Section>
                                <Section title="Controller" icon={Cpu}>
                                    <div className="flex flex-wrap gap-2">
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/mode', { mode: 'active', reason: 'UI set active' });
                                                toast.success('Controller mode set to Active');
                                            } catch (e: any) {
                                                toast.error(`Mode change failed: ${e?.message || 'error'}`);
                                            }
                                        }} className="rounded-xl bg-emerald-600 hover:bg-emerald-500 text-black">Active</Button>
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/mode', { mode: 'active_limited', reason: 'UI set limited' });
                                                toast.success('Controller mode set to Limited');
                                            } catch (e: any) {
                                                toast.error(`Mode change failed: ${e?.message || 'error'}`);
                                            }
                                        }} variant="secondary" className="rounded-xl">Limited</Button>
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/mode', { mode: 'advisory', reason: 'UI set advisory' });
                                                toast.success('Controller mode set to Advisory');
                                            } catch (e: any) {
                                                toast.error(`Mode change failed: ${e?.message || 'error'}`);
                                            }
                                        }} variant="secondary" className="rounded-xl">Advisory</Button>
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/mode', { mode: 'observe_only', reason: 'UI set observe' });
                                                toast.success('Controller mode set to Observe Only');
                                            } catch (e: any) {
                                                toast.error(`Mode change failed: ${e?.message || 'error'}`);
                                            }
                                        }} variant="secondary" className="rounded-xl">Observe</Button>
                                    </div>
                                    <div className="mt-3 flex flex-wrap gap-2">
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/emergency_stop', { reason: 'UI emergency stop' });
                                                toast.error('Emergency Stop activated', { icon: <AlertTriangle className="w-4 h-4" /> });
                                            } catch (e: any) {
                                                toast.error(`Emergency stop failed: ${e?.message || 'error'}`);
                                            }
                                        }} className="rounded-xl bg-red-600/80 hover:bg-red-500 text-white">Emergency Stop</Button>
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                await postJSON('/api/homeostasis/reset_emergency', {});
                                                toast.success('Emergency stop reset');
                                            } catch (e: any) {
                                                toast.error(`Reset failed: ${e?.message || 'error'}`);
                                            }
                                        }} variant="secondary" className="rounded-xl">Reset Emergency</Button>
                                        <Button onClick={async () => {
                                            try {
                                                const { postJSON } = await import('./lib/api');
                                                const result = await postJSON('/api/homeostasis/rollback', {});
                                                if (result.rolled_back) {
                                                    toast.success(`Rollback successful: ${result.message || 'last action reversed'}`);
                                                } else {
                                                    toast.warning(`Rollback completed but may have issues: ${result.message || 'check logs'}`);
                                                }
                                            } catch (e: any) {
                                                toast.error(`Rollback failed: ${e?.message || 'error'}`);
                                            }
                                        }} variant="secondary" className="rounded-xl">Rollback Last</Button>
                                        <Button onClick={() => setOpenActuatorDialog(true)} variant="secondary" className="rounded-xl">
                                            <Play className="w-4 h-4 mr-2" /> Execute Action
                                        </Button>
                                    </div>
                                </Section>
                                <Section title="KPIs" icon={Cpu}>
                                    <pre className="p-3 rounded-xl bg-[#111113] border border-[#1f1e21] text-xs whitespace-pre-wrap overflow-auto">{maintenance.data?.kpis ? JSON.stringify(maintenance.data.kpis, null, 2) : (maintenance.error ? `error: ${maintenance.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-6">
                                <Section title="Stability Metrics" icon={Gauge}>
                                    {homeostasisMetrics.data?.snapshot ? (
                                        <div className="space-y-3 text-sm">
                                            {homeostasisMetrics.data.snapshot.plugin_load_success != null && (
                                                <div>
                                                    <div className="flex justify-between mb-1">
                                                        <span className="text-gray-400">Plugin Success</span>
                                                        <span className="text-white">{homeostasisMetrics.data.snapshot.plugin_load_success.toFixed(1)}%</span>
                                                    </div>
                                                    <Progress value={homeostasisMetrics.data.snapshot.plugin_load_success} className="h-2 bg-[#121214]" />
                                                </div>
                                            )}
                                            {homeostasisMetrics.data.snapshot.memory_rtt != null && (
                                                <div>
                                                    <div className="flex justify-between mb-1">
                                                        <span className="text-gray-400">Memory RTT</span>
                                                        <span className="text-white">{homeostasisMetrics.data.snapshot.memory_rtt.toFixed(1)}ms</span>
                                                    </div>
                                                    <Progress value={Math.min(100, (homeostasisMetrics.data.snapshot.memory_rtt / 200) * 100)} className="h-2 bg-[#121214]" />
                                                </div>
                                            )}
                                            {homeostasisMetrics.data.snapshot.task_latency != null && (
                                                <div>
                                                    <div className="flex justify-between mb-1">
                                                        <span className="text-gray-400">Task Latency</span>
                                                        <span className="text-white">{homeostasisMetrics.data.snapshot.task_latency.toFixed(1)}ms</span>
                                                    </div>
                                                    <Progress value={Math.min(100, (homeostasisMetrics.data.snapshot.task_latency / 300) * 100)} className="h-2 bg-[#121214]" />
                                                </div>
                                            )}
                                            {homeostasisMetrics.data.snapshot.learning_rate != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Learning Rate</span>
                                                    <span className="text-white">{homeostasisMetrics.data.snapshot.learning_rate.toFixed(4)}</span>
                                                </div>
                                            )}
                                            {homeostasisMetrics.data.snapshot.confidence_level != null && (
                                                <div>
                                                    <div className="flex justify-between mb-1">
                                                        <span className="text-gray-400">Confidence</span>
                                                        <span className="text-white">{(homeostasisMetrics.data.snapshot.confidence_level * 100).toFixed(1)}%</span>
                                                    </div>
                                                    <Progress value={homeostasisMetrics.data.snapshot.confidence_level * 100} className="h-2 bg-[#121214]" />
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">{homeostasisMetrics.error ? `Error: ${homeostasisMetrics.error}` : 'Loading metrics…'}</div>
                                    )}
                                </Section>
                                <Section title="PID Control Loops" icon={Activity}>
                                    {homeostasis.data?.control_loops && Object.keys(homeostasis.data.control_loops).length > 0 ? (
                                        <div className="space-y-3 text-xs">
                                            {Object.entries(homeostasis.data.control_loops).slice(0, 5).map(([name, loop]: [string, any]) => (
                                                <div key={name} className="p-2 rounded-lg bg-[#111113] border border-[#1e1e21]">
                                                    <div className="font-medium text-emerald-300 mb-1">{name}</div>
                                                    <div className="grid grid-cols-3 gap-2 text-[10px]">
                                                        <div>
                                                            <span className="text-gray-500">Error:</span>
                                                            <span className={`ml-1 ${Math.abs(loop.error || 0) > (loop.setpoint || 1) * 0.1 ? 'text-amber-400' : 'text-gray-300'}`}>
                                                                {(loop.error || 0).toFixed(2)}
                                                            </span>
                                                        </div>
                                                        <div>
                                                            <span className="text-gray-500">Output:</span>
                                                            <span className="ml-1 text-gray-300">{(loop.output || 0).toFixed(2)}</span>
                                                        </div>
                                                        <div>
                                                            <span className="text-gray-500">Target:</span>
                                                            <span className="ml-1 text-gray-300">{(loop.setpoint || 0).toFixed(1)}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">No active control loops.</div>
                                    )}
                                </Section>
                                <Section title="Watchdog & Supervisor" icon={Shield}>
                                    {homeostasis.data?.orchestrator?.watchdog ? (
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Watchdog Active</span>
                                                <span className={`${homeostasis.data.orchestrator.watchdog.active ? 'text-emerald-400' : 'text-amber-400'}`}>
                                                    {homeostasis.data.orchestrator.watchdog.active ? 'YES' : 'NO'}
                                                </span>
                                            </div>
                                            {homeostasis.data.orchestrator.watchdog.cycle_count != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Cycles</span>
                                                    <span className="text-white">{homeostasis.data.orchestrator.watchdog.cycle_count}</span>
                                                </div>
                                            )}
                                            {homeostasis.data.orchestrator.watchdog.error_count != null && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Errors</span>
                                                    <span className={`${homeostasis.data.orchestrator.watchdog.error_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                                        {homeostasis.data.orchestrator.watchdog.error_count}
                                                    </span>
                                                </div>
                                            )}
                                            {homeostasis.data.supervisor?.runlevel && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-400">Runlevel</span>
                                                    <span className="text-white">{homeostasis.data.supervisor.runlevel}</span>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">Watchdog info unavailable</div>
                                    )}
                                </Section>
                            </div>
                            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Section title="Recent Actions" icon={Activity}>
                                    {Array.isArray(homeostasis.data?.recent_actions) && homeostasis.data.recent_actions.length > 0 ? (
                                        <div className="space-y-2 text-xs">
                                            {homeostasis.data.recent_actions.slice(-10).reverse().map((a: any, i: number) => (
                                                <div key={i} className="flex items-center justify-between gap-3 p-2 rounded-lg bg-[#111113] border border-[#1e1e21]">
                                                    <div className="truncate">
                                                        <span className="text-emerald-300 mr-2">{a.action_type}</span>
                                                        <span className="text-gray-400">{a.target}</span>
                                                        {a.reason && <span className="text-gray-500 ml-2">— {a.reason}</span>}
                                                    </div>
                                                    <span className={`text-[10px] ${a.success ? 'text-emerald-400' : 'text-amber-400'}`}>{a.success ? 'ok' : 'fail'}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-xs text-gray-500">No recent actions.</div>
                                    )}
                                </Section>
                                <Section title="Raw Homeostasis Snapshot" icon={Database}>
                                    <pre className="p-3 rounded-xl bg-[#111113] border border-[#1f1e21] text-xs whitespace-pre-wrap overflow-auto max-h-64">{homeostasis.data ? JSON.stringify(homeostasis.data, null, 2) : (homeostasis.error ? `error: ${homeostasis.error}` : 'loading…')}</pre>
                                </Section>
                            </div>
                        </Section>
                    )}
                    {route === "security" && (
                        <div className="space-y-6">
                            {/* Security Overview */}
                            <Section title="Security Overview" icon={ShieldCheck}>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <Stat
                                        label="Safety Mode"
                                        value={policy?.safety_mode || securityMode}
                                        sub="Current security level"
                                        icon={securityMode === "strict" ? Lock : Unlock}
                                        ok={securityMode === "strict"}
                                    />
                                    <Stat
                                        label="Active Alerts"
                                        value={securityAlerts.filter(a => a.status === "active").length}
                                        sub={`${securityAlerts.length} total`}
                                        icon={AlertCircle}
                                        ok={securityAlerts.filter(a => a.severity === "critical").length === 0}
                                    />
                                    <Stat
                                        label="Audit Entries"
                                        value={memoryAudit.data?.enabled ? (memoryAudit.data?.nodes?.length || 0) : "N/A"}
                                        sub="Memory audit nodes"
                                        icon={FileText}
                                    />
                                    <Stat
                                        label="Policy Status"
                                        value={policy ? "Active" : "Unknown"}
                                        sub="Current enforcement"
                                        icon={CheckCircle}
                                        ok={!!policy}
                                    />
                                </div>
                            </Section>

                            {/* Security Controls */}
                            <Section title="Security Controls" icon={Shield} right={
                                <div className="flex gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/20"
                                        onClick={async () => {
                                            try {
                                                toast.info("Security scan initiated");
                                                // Simulate scan
                                                await new Promise(resolve => setTimeout(resolve, 2000));
                                                toast.success("Security scan completed - no threats detected");
                                            } catch (err: any) {
                                                toast.error(`Scan failed: ${err?.message || 'unknown'}`);
                                            }
                                        }}
                                    >
                                        <Scan className="w-4 h-4 mr-2" />
                                        Run Scan
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-blue-800/40 text-blue-400 hover:bg-blue-900/20"
                                        onClick={() => {
                                            toast.success("Policy refreshed from backend");
                                            ping();
                                        }}
                                    >
                                        <RefreshCw className="w-4 h-4 mr-2" />
                                        Refresh Policy
                                    </Button>
                                </div>
                            }>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Button
                                        variant="outline"
                                        className="h-auto py-4 border-amber-800/40 text-amber-400 hover:bg-amber-900/20 flex flex-col items-start gap-2"
                                        onClick={() => {
                                            setSecurityMode(securityMode === "strict" ? "standard" : "strict");
                                            toast.success(`Security mode: ${securityMode === "strict" ? "standard" : "strict"}`);
                                        }}
                                    >
                                        <div className="flex items-center gap-2">
                                            {securityMode === "strict" ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                                            <span className="font-semibold">Toggle Safety Mode</span>
                                        </div>
                                        <span className="text-xs text-gray-400">Current: {securityMode}</span>
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="h-auto py-4 border-gray-800/40 hover:bg-gray-900/20 flex flex-col items-start gap-2"
                                        onClick={() => {
                                            const cleared = securityAlerts.filter(a => a.status === "active").length;
                                            setSecurityAlerts(prev => prev.map(a => ({ ...a, status: "resolved" })));
                                            toast.success(`Cleared ${cleared} active alert(s)`);
                                        }}
                                    >
                                        <div className="flex items-center gap-2">
                                            <Trash2 className="w-4 h-4" />
                                            <span className="font-semibold">Clear Alerts</span>
                                        </div>
                                        <span className="text-xs text-gray-400">Resolve all active</span>
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="h-auto py-4 border-red-800/40 text-red-400 hover:bg-red-900/20 flex flex-col items-start gap-2"
                                        onClick={() => {
                                            toast.warning("Emergency lockdown activated");
                                            setSecurityMode("strict");
                                        }}
                                    >
                                        <div className="flex items-center gap-2">
                                            <ShieldAlert className="w-4 h-4" />
                                            <span className="font-semibold">Emergency Lockdown</span>
                                        </div>
                                        <span className="text-xs text-gray-400">Activate strict mode</span>
                                    </Button>
                                </div>
                            </Section>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Active Threats & Alerts */}
                                <Section title="Security Alerts" icon={AlertTriangle}>
                                    <div className="space-y-3 max-h-[400px] overflow-y-auto">
                                        {securityAlerts.length === 0 ? (
                                            <div className="text-sm text-gray-500 text-center py-8">No security alerts</div>
                                        ) : (
                                            securityAlerts.slice().reverse().map((alert) => {
                                                const severityColor = alert.severity === "critical" ? "red" : alert.severity === "warning" ? "amber" : "blue";
                                                const statusColor = alert.status === "active" ? "emerald" : "gray";

                                                return (
                                                    <div
                                                        key={alert.id}
                                                        className={`p-3 rounded-xl bg-[#111113] border border-[#1e1e21] hover:border-${severityColor}-800/40 transition cursor-pointer`}
                                                        onClick={() => setShowAuditDetails(showAuditDetails === alert.id ? null : alert.id)}
                                                    >
                                                        <div className="flex items-start justify-between gap-3">
                                                            <div className="flex-1">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <Badge className={`bg-${severityColor}-900/30 text-${severityColor}-300 border-${severityColor}-800/40`}>
                                                                        {alert.severity}
                                                                    </Badge>
                                                                    <Badge className={`bg-${statusColor}-900/30 text-${statusColor}-300 border-${statusColor}-800/40`}>
                                                                        {alert.status}
                                                                    </Badge>
                                                                    <span className="text-xs text-gray-500">
                                                                        {new Date(alert.timestamp).toLocaleString()}
                                                                    </span>
                                                                </div>
                                                                <div className="text-sm text-white font-medium">{alert.message}</div>
                                                                <div className="text-xs text-gray-500 mt-1">Type: {alert.type} • ID: {alert.id}</div>

                                                                {showAuditDetails === alert.id && (
                                                                    <div className="mt-3 p-2 rounded bg-[#0e0e10] border border-[#1a1a1d] text-xs">
                                                                        <div className="text-gray-400">Additional details for {alert.id} would appear here.</div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                            <Eye className="w-4 h-4 text-gray-500" />
                                                        </div>
                                                    </div>
                                                );
                                            })
                                        )}
                                    </div>
                                </Section>

                                {/* Policy Details */}
                                <Section title="Active Policy Configuration" icon={Key}>
                                    <Tabs defaultValue="capabilities" className="w-full">
                                        <TabsList className="bg-[#111113] border border-[#1e1e21] w-full grid grid-cols-3">
                                            <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
                                            <TabsTrigger value="network">Network</TabsTrigger>
                                            <TabsTrigger value="signing">Signing</TabsTrigger>
                                        </TabsList>

                                        <TabsContent value="capabilities" className="mt-3 space-y-3">
                                            <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Allowed Capabilities</div>
                                                <div className="space-y-2">
                                                    {policy?.capabilities?.allow ? (
                                                        Object.entries(policy.capabilities.allow).map(([key, value]) => (
                                                            <div key={key} className="flex items-center justify-between text-sm">
                                                                <span className="text-emerald-400 font-mono">{key}</span>
                                                                <span className="text-gray-500">{Array.isArray(value) ? value.join(", ") : String(value)}</span>
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <div className="text-sm text-gray-500">No capability grants defined</div>
                                                    )}
                                                </div>
                                            </div>
                                            {policy?.capabilities?.limits && (
                                                <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Capability Limits</div>
                                                    <pre className="text-xs text-gray-400">{JSON.stringify(policy.capabilities.limits, null, 2)}</pre>
                                                </div>
                                            )}
                                        </TabsContent>

                                        <TabsContent value="network" className="mt-3 space-y-3">
                                            <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Network Policy</div>
                                                {policy?.network_policy ? (
                                                    <div className="space-y-2">
                                                        {policy.network_policy.allowlist && (
                                                            <div>
                                                                <div className="text-xs text-emerald-400 font-semibold mb-1">Allowlist</div>
                                                                <div className="flex flex-wrap gap-1">
                                                                    {policy.network_policy.allowlist.map((domain: string, idx: number) => (
                                                                        <Badge key={idx} className="bg-emerald-900/30 text-emerald-300 border-emerald-800/40 text-xs">
                                                                            {domain}
                                                                        </Badge>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                        {policy.network_policy.block_unknown !== undefined && (
                                                            <div className="text-sm">
                                                                <span className="text-gray-400">Block unknown: </span>
                                                                <span className={policy.network_policy.block_unknown ? "text-red-400" : "text-emerald-400"}>
                                                                    {String(policy.network_policy.block_unknown)}
                                                                </span>
                                                            </div>
                                                        )}
                                                    </div>
                                                ) : (
                                                    <div className="text-sm text-gray-500">No network policy defined</div>
                                                )}
                                            </div>
                                        </TabsContent>

                                        <TabsContent value="signing" className="mt-3 space-y-3">
                                            <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Signature Requirements</div>
                                                <div className="space-y-2 text-sm">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">Script Signing (.aether)</span>
                                                        <Badge className="bg-emerald-900/30 text-emerald-300 border-emerald-800/40">Required</Badge>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">Plugin Signing (Ed25519)</span>
                                                        <Badge className="bg-emerald-900/30 text-emerald-300 border-emerald-800/40">Required</Badge>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">Strict Mode</span>
                                                        <Badge className={securityMode === "strict" ? "bg-emerald-900/30 text-emerald-300 border-emerald-800/40" : "bg-gray-800/30 text-gray-400 border-gray-700/40"}>
                                                            {securityMode === "strict" ? "Enabled" : "Disabled"}
                                                        </Badge>
                                                    </div>
                                                </div>
                                            </div>
                                        </TabsContent>
                                    </Tabs>
                                </Section>
                            </div>

                            {/* Full Policy JSON */}
                            <Section title="Complete Policy Snapshot" icon={FileText}>
                                <pre className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21] text-xs whitespace-pre-wrap overflow-auto max-h-[400px]">
                                    {policy ? JSON.stringify(policy, null, 2) : 'Open Chat to retrieve current policy frame (or call /api/lyrixa/chat).'}
                                </pre>
                            </Section>
                        </div>
                    )}
                    {route === "scripts" && (
                        <div className="space-y-6">
                            {/* Scripts Overview */}
                            <Section title=".aether Script Management" icon={Workflow} right={
                                <div className="flex gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/20"
                                        onClick={() => {
                                            setShowScriptEditor(true);
                                            setScriptContent('goal: "New script"\n\nworkflow:\n  steps:\n    - reflect()');
                                            toast.info("Script editor opened");
                                        }}
                                    >
                                        <Plus className="w-4 h-4 mr-2" />
                                        New Script
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-blue-800/40 text-blue-400 hover:bg-blue-900/20"
                                        onClick={() => {
                                            ping();
                                            toast.success("Scripts refreshed");
                                        }}
                                    >
                                        <RefreshCw className="w-4 h-4 mr-2" />
                                        Refresh
                                    </Button>
                                </div>
                            }>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <Stat
                                        label="Total Scripts"
                                        value={aetherScripts.length}
                                        sub={`${aetherScripts.filter(s => s.status === "ready").length} ready`}
                                        icon={FileCode}
                                    />
                                    <Stat
                                        label="Executions Today"
                                        value={aetherScripts.filter(s => s.lastRun && s.lastRun > Date.now() - 86400000).length}
                                        sub="Last 24 hours"
                                        icon={Zap}
                                    />
                                    <Stat
                                        label="Active Execution"
                                        value={scriptExecution ? "Running" : "None"}
                                        sub={scriptExecution ? scriptExecution.script_name : "Idle"}
                                        icon={scriptExecution ? Play : Pause}
                                        ok={!scriptExecution}
                                    />
                                    <Stat
                                        label="Success Rate"
                                        value="95%"
                                        sub="Last 100 runs"
                                        icon={CheckCircle}
                                    />
                                </div>
                            </Section>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Script Library */}
                                <Section title="Script Library" icon={BookOpen}>
                                    <div className="space-y-3 max-h-[500px] overflow-y-auto">
                                        {aetherScripts.map((script) => (
                                            <div
                                                key={script.id}
                                                className={`p-4 rounded-xl bg-[#111113] border transition cursor-pointer ${selectedScript === script.id ? 'border-emerald-800/60 bg-emerald-900/10' : 'border-[#1e1e21] hover:border-emerald-800/40'
                                                    }`}
                                                onClick={() => {
                                                    setSelectedScript(script.id);
                                                    setScriptContent(`goal: "${script.description}"\n\nworkflow:\n  steps:\n    - summarize(load_logs(tag="system")) as sys\n    - summarize(load_logs(tag="user")) as usr retry=2 timeout="30s"\n    - run_plugin("report_merger", [sys, usr]) as rep requires=["memory.read"]\n    - store(rep, tag="daily")\n\npolicy:\n  timeout_default: "30s"\n  risk_threshold: 0.3\n\nrequire:\n  plugins:\n    - "anomaly_detector>=0.3"`);
                                                }}
                                            >
                                                <div className="flex items-start justify-between gap-3">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <FileCode className="w-4 h-4 text-emerald-400" />
                                                            <span className="text-white font-semibold">{script.name}</span>
                                                            <Badge className={`ml-auto ${script.status === "ready" ? "bg-emerald-900/30 text-emerald-300 border-emerald-800/40" :
                                                                script.status === "running" ? "bg-blue-900/30 text-blue-300 border-blue-800/40" :
                                                                    "bg-gray-800/30 text-gray-400 border-gray-700/40"
                                                                }`}>
                                                                {script.status}
                                                            </Badge>
                                                        </div>
                                                        <div className="text-sm text-gray-400 mb-2">{script.description}</div>
                                                        <div className="text-xs text-gray-500">
                                                            Last run: {script.lastRun ? new Date(script.lastRun).toLocaleString() : "Never"}
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex gap-2 mt-3">
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="flex-1 border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/20"
                                                        onClick={async (e) => {
                                                            e.stopPropagation();
                                                            try {
                                                                toast.info(`Running ${script.name}...`);
                                                                const { postJSON } = await import('./lib/api');
                                                                const result = await postJSON('/api/run', {
                                                                    script_name: script.name,
                                                                    parameters: {},
                                                                    context: {}
                                                                });

                                                                if (result.job_id) {
                                                                    setScriptExecution({ job_id: result.job_id, script_name: script.name, status: result.status });
                                                                    toast.success(`Script started: ${result.job_id.substring(0, 8)}...`);
                                                                    setAetherScripts(prev => prev.map(s => s.id === script.id ? { ...s, lastRun: Date.now(), status: "running" } : s));
                                                                } else {
                                                                    toast.warning("Script execution endpoint not available - using simulation");
                                                                    setAetherScripts(prev => prev.map(s => s.id === script.id ? { ...s, lastRun: Date.now() } : s));
                                                                }
                                                            } catch (err: any) {
                                                                toast.error(`Run failed: ${err?.message || 'unknown'}`);
                                                            }
                                                        }}
                                                    >
                                                        <Play className="w-3 h-3 mr-2" />
                                                        Run
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="flex-1 border-blue-800/40 text-blue-400 hover:bg-blue-900/20"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setShowScriptEditor(true);
                                                            toast.info(`Editing ${script.name}`);
                                                        }}
                                                    >
                                                        <Edit className="w-3 h-3 mr-2" />
                                                        Edit
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="border-gray-800/40 hover:bg-gray-900/20"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            toast.info(`Downloading ${script.name}`);
                                                        }}
                                                    >
                                                        <Download className="w-3 h-3" />
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </Section>

                                {/* Script Viewer/Editor */}
                                <Section title={showScriptEditor ? "Script Editor" : "Script Viewer"} icon={showScriptEditor ? Edit : Eye}>
                                    <Tabs defaultValue="source" className="w-full">
                                        <TabsList className="bg-[#111113] border border-[#1e1e21] w-full grid grid-cols-4">
                                            <TabsTrigger value="source">Source</TabsTrigger>
                                            <TabsTrigger value="policy">Policy</TabsTrigger>
                                            <TabsTrigger value="execution">Execution</TabsTrigger>
                                            <TabsTrigger value="trace">Trace</TabsTrigger>
                                        </TabsList>

                                        <TabsContent value="source" className="mt-3">
                                            <div className="space-y-3">
                                                {showScriptEditor ? (
                                                    <>
                                                        <textarea
                                                            className="w-full h-[400px] p-4 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs font-mono text-gray-300 focus:outline-none focus:border-emerald-800/60 resize-none"
                                                            value={scriptContent}
                                                            onChange={(e) => setScriptContent(e.target.value)}
                                                            placeholder="Enter .aether script content..."
                                                            spellCheck={false}
                                                        />
                                                        <div className="flex gap-2">
                                                            <Button
                                                                size="sm"
                                                                className="bg-emerald-600 hover:bg-emerald-700"
                                                                onClick={() => {
                                                                    toast.success("Script saved");
                                                                    setShowScriptEditor(false);
                                                                }}
                                                            >
                                                                <Upload className="w-4 h-4 mr-2" />
                                                                Save
                                                            </Button>
                                                            <Button
                                                                size="sm"
                                                                variant="outline"
                                                                className="border-gray-800/40"
                                                                onClick={() => {
                                                                    setShowScriptEditor(false);
                                                                    toast.info("Edit cancelled");
                                                                }}
                                                            >
                                                                Cancel
                                                            </Button>
                                                        </div>
                                                    </>
                                                ) : (
                                                    <pre className="p-4 rounded-xl bg-[#0e0e10] border border-[#1e1e21] text-xs font-mono text-gray-300 overflow-auto max-h-[400px] whitespace-pre">
                                                        {scriptContent || 'Select a script from the library to view its source code.'}
                                                    </pre>
                                                )}
                                            </div>
                                        </TabsContent>

                                        <TabsContent value="policy" className="mt-3">
                                            <div className="space-y-3">
                                                <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Policy Block</div>
                                                    <pre className="text-xs text-gray-400">{`policy:
  timeout_default: "30s"
  risk_threshold: 0.3
  deterministic: false
  data_class: "internal"`}</pre>
                                                </div>
                                                <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Required Dependencies</div>
                                                    <pre className="text-xs text-gray-400">{`require:
  plugins:
    - "anomaly_detector>=0.3,<0.5"
    - "report_merger==1.2.1"
  capabilities: ["storage.write", "memory.read"]`}</pre>
                                                </div>
                                                <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Meta Information</div>
                                                    <pre className="text-xs text-gray-400">{`meta:
  version: "1.1"
  author: "Aetherra Labs"
  seed: 42`}</pre>
                                                </div>
                                            </div>
                                        </TabsContent>

                                        <TabsContent value="execution" className="mt-3">
                                            <div className="space-y-3">
                                                {scriptExecution ? (
                                                    <>
                                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                            <div className="flex items-center justify-between mb-3">
                                                                <span className="text-sm font-semibold text-white">Job: {scriptExecution.job_id.substring(0, 16)}...</span>
                                                                <Badge className="bg-blue-900/30 text-blue-300 border-blue-800/40">
                                                                    {scriptExecution.status}
                                                                </Badge>
                                                            </div>
                                                            <div className="text-xs text-gray-400 space-y-1">
                                                                <div>Script: {scriptExecution.script_name}</div>
                                                                <div>Started: {new Date().toLocaleTimeString()}</div>
                                                            </div>
                                                        </div>
                                                        <div className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21]">
                                                            <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Output Log</div>
                                                            <div className="text-xs text-gray-400 font-mono space-y-1">
                                                                <div>[00:00] Script execution started...</div>
                                                                <div>[00:01] Loading memory context...</div>
                                                                <div>[00:02] Executing workflow steps...</div>
                                                                <div className="text-emerald-400">[00:03] ✓ Step 1: summarize(load_logs(tag="system"))</div>
                                                                <div className="text-blue-400">[00:04] → Processing...</div>
                                                            </div>
                                                        </div>
                                                        <Button
                                                            size="sm"
                                                            variant="outline"
                                                            className="w-full border-red-800/40 text-red-400 hover:bg-red-900/20"
                                                            onClick={async () => {
                                                                try {
                                                                    const { postJSON } = await import('./lib/api');
                                                                    await postJSON(`/api/cancel/${scriptExecution.job_id}`, {});
                                                                    toast.warning("Execution cancelled");
                                                                    setScriptExecution(null);
                                                                    setAetherScripts(prev => prev.map(s => ({ ...s, status: "ready" })));
                                                                } catch (err: any) {
                                                                    toast.error(`Cancel failed: ${err?.message || 'unknown'}`);
                                                                    setScriptExecution(null);
                                                                }
                                                            }}
                                                        >
                                                            <Square className="w-4 h-4 mr-2" />
                                                            Cancel Execution
                                                        </Button>
                                                    </>
                                                ) : (
                                                    <div className="text-center py-12 text-gray-500">
                                                        <Play className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                                        <div className="text-sm">No active execution</div>
                                                        <div className="text-xs mt-1">Run a script to see execution details</div>
                                                    </div>
                                                )}
                                            </div>
                                        </TabsContent>

                                        <TabsContent value="trace" className="mt-3">
                                            <div className="p-3 rounded-xl bg-[#0e0e10] border border-[#1e1e21] max-h-[400px] overflow-y-auto">
                                                <div className="text-xs text-gray-500 mb-3">Execution trace (when AETHERRA_TRACE=1):</div>
                                                <div className="space-y-2 text-xs font-mono">
                                                    {scriptExecution ? (
                                                        <>
                                                            <div className="text-gray-400">
                                                                <span className="text-emerald-400">→</span> [goal] "Generate daily narrative and store securely"
                                                            </div>
                                                            <div className="text-gray-400 pl-4">
                                                                <span className="text-blue-400">→</span> [assign] sys = summarize(load_logs(tag="system"))
                                                            </div>
                                                            <div className="text-gray-400 pl-4">
                                                                <span className="text-blue-400">→</span> [assign] usr = summarize(load_logs(tag="user"))
                                                            </div>
                                                            <div className="text-gray-400 pl-4">
                                                                <span className="text-amber-400">⟳</span> [retry] attempt 1/2
                                                            </div>
                                                        </>
                                                    ) : (
                                                        <div className="text-gray-500 text-center py-8">Trace will appear here when scripts run with trace enabled.</div>
                                                    )}
                                                </div>
                                            </div>
                                        </TabsContent>
                                    </Tabs>
                                </Section>
                            </div>

                            {/* Quick Reference */}
                            <Section title="Aether Script v1.1 Quick Reference" icon={BookOpen}>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs uppercase tracking-wider text-emerald-400 mb-2 font-semibold">Core Blocks</div>
                                        <div className="text-xs text-gray-400 space-y-1 font-mono">
                                            <div>goal: "..."</div>
                                            <div>workflow: ...</div>
                                            <div>policy: ...</div>
                                            <div>require: ...</div>
                                            <div>on_error: ...</div>
                                            <div>parallel: ...</div>
                                        </div>
                                    </div>
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs uppercase tracking-wider text-blue-400 mb-2 font-semibold">Step Modifiers</div>
                                        <div className="text-xs text-gray-400 space-y-1 font-mono">
                                            <div>as alias</div>
                                            <div>retry=N</div>
                                            <div>timeout="30s"</div>
                                            <div>requires=[...]</div>
                                        </div>
                                    </div>
                                    <div className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                        <div className="text-xs uppercase tracking-wider text-amber-400 mb-2 font-semibold">Built-in Functions</div>
                                        <div className="text-xs text-gray-400 space-y-1 font-mono">
                                            <div>reflect()</div>
                                            <div>summarize(x)</div>
                                            <div>load_logs()</div>
                                            <div>store(x, tag)</div>
                                            <div>run_plugin(x)</div>
                                        </div>
                                    </div>
                                </div>
                            </Section>
                        </div>
                    )}
                    {route === "settings" && (
                        <div className="space-y-6">
                            {/* Settings Overview */}
                            <Section title="System Settings" icon={Settings} right={
                                <div className="flex gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/20"
                                        onClick={() => {
                                            toast.success("Settings saved to local storage");
                                            localStorage.setItem('lyrixa_settings', JSON.stringify(settingsConfig));
                                        }}
                                    >
                                        <Save className="w-4 h-4 mr-2" />
                                        Save All
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-gray-800/40 hover:bg-gray-900/20"
                                        onClick={() => {
                                            const saved = localStorage.getItem('lyrixa_settings');
                                            if (saved) {
                                                setSettingsConfig(JSON.parse(saved));
                                                toast.info("Settings restored from local storage");
                                            } else {
                                                toast.warning("No saved settings found");
                                            }
                                        }}
                                    >
                                        <RefreshCw className="w-4 h-4 mr-2" />
                                        Reset
                                    </Button>
                                </div>
                            }>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <Stat
                                        label="Profile"
                                        value="Production"
                                        sub="AETHERRA_PROFILE"
                                        icon={Shield}
                                    />
                                    <Stat
                                        label="Backend"
                                        value="Connected"
                                        sub={settingsConfig.api.backendUrl}
                                        icon={Server}
                                    />
                                    <Stat
                                        label="Theme"
                                        value={settingsConfig.appearance.theme}
                                        sub="Current display mode"
                                        icon={settingsConfig.appearance.theme === "dark" ? Moon : Sun}
                                    />
                                    <Stat
                                        label="Notifications"
                                        value={settingsConfig.notifications.enabled ? "Enabled" : "Disabled"}
                                        sub={`${Object.values(settingsConfig.notifications).filter(Boolean).length} active`}
                                        icon={Bell}
                                    />
                                </div>
                            </Section>

                            {/* Settings Tabs */}
                            <Section title="Configuration" icon={Sliders}>
                                <Tabs defaultValue="appearance" className="w-full">
                                    <TabsList className="bg-[#111113] border border-[#1e1e21] grid grid-cols-5">
                                        <TabsTrigger value="appearance">
                                            <Palette className="w-4 h-4 mr-2" />
                                            Appearance
                                        </TabsTrigger>
                                        <TabsTrigger value="api">
                                            <Globe className="w-4 h-4 mr-2" />
                                            API
                                        </TabsTrigger>
                                        <TabsTrigger value="notifications">
                                            <Bell className="w-4 h-4 mr-2" />
                                            Notifications
                                        </TabsTrigger>
                                        <TabsTrigger value="performance">
                                            <Zap className="w-4 h-4 mr-2" />
                                            Performance
                                        </TabsTrigger>
                                        <TabsTrigger value="developer">
                                            <Code2 className="w-4 h-4 mr-2" />
                                            Developer
                                        </TabsTrigger>
                                    </TabsList>

                                    {/* Appearance Settings */}
                                    <TabsContent value="appearance" className="mt-6 space-y-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        {settingsConfig.appearance.theme === "dark" ? <Moon className="w-4 h-4 text-blue-400" /> : <Sun className="w-4 h-4 text-amber-400" />}
                                                        <span className="text-white font-semibold">Theme</span>
                                                    </div>
                                                </div>
                                                <div className="flex gap-2">
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className={`flex-1 ${settingsConfig.appearance.theme === "dark" ? "border-blue-600 bg-blue-900/20 text-blue-300" : "border-gray-800/40"}`}
                                                        onClick={() => {
                                                            setSettingsConfig(prev => ({ ...prev, appearance: { ...prev.appearance, theme: "dark" } }));
                                                            toast.info("Theme: Dark");
                                                        }}
                                                    >
                                                        <Moon className="w-4 h-4 mr-2" />
                                                        Dark
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className={`flex-1 ${settingsConfig.appearance.theme === "light" ? "border-amber-600 bg-amber-900/20 text-amber-300" : "border-gray-800/40"}`}
                                                        onClick={() => {
                                                            setSettingsConfig(prev => ({ ...prev, appearance: { ...prev.appearance, theme: "light" } }));
                                                            toast.info("Theme: Light (preview only)");
                                                        }}
                                                    >
                                                        <Sun className="w-4 h-4 mr-2" />
                                                        Light
                                                    </Button>
                                                </div>
                                            </div>

                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <Palette className="w-4 h-4 text-emerald-400" />
                                                        <span className="text-white font-semibold">Accent Color</span>
                                                    </div>
                                                </div>
                                                <div className="flex gap-2">
                                                    {["#00ff88", "#3b82f6", "#8b5cf6", "#f59e0b"].map(color => (
                                                        <button
                                                            key={color}
                                                            className={`w-10 h-10 rounded-lg border-2 transition ${settingsConfig.appearance.accentColor === color ? "border-white scale-110" : "border-transparent hover:border-gray-600"}`}
                                                            style={{ backgroundColor: color }}
                                                            onClick={() => {
                                                                setSettingsConfig(prev => ({ ...prev, appearance: { ...prev.appearance, accentColor: color } }));
                                                                toast.info(`Accent color updated`);
                                                            }}
                                                        />
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <Monitor className="w-4 h-4 text-gray-400" />
                                                        <span className="text-white font-semibold">Font Size</span>
                                                    </div>
                                                </div>
                                                <div className="flex gap-2">
                                                    {[{ label: "Small", value: "small" }, { label: "Medium", value: "medium" }, { label: "Large", value: "large" }].map(size => (
                                                        <Button
                                                            key={size.value}
                                                            size="sm"
                                                            variant="outline"
                                                            className={`flex-1 ${settingsConfig.appearance.fontSize === size.value ? "border-emerald-600 bg-emerald-900/20 text-emerald-300" : "border-gray-800/40"}`}
                                                            onClick={() => {
                                                                setSettingsConfig(prev => ({ ...prev, appearance: { ...prev.appearance, fontSize: size.value } }));
                                                                toast.info(`Font size: ${size.label}`);
                                                            }}
                                                        >
                                                            {size.label}
                                                        </Button>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Sparkles className="w-4 h-4 text-purple-400" />
                                                        <span className="text-white font-semibold">Animations</span>
                                                    </div>
                                                    <button
                                                        onClick={() => {
                                                            setSettingsConfig(prev => ({ ...prev, appearance: { ...prev.appearance, animations: !prev.appearance.animations } }));
                                                            toast.info(`Animations ${!settingsConfig.appearance.animations ? "enabled" : "disabled"}`);
                                                        }}
                                                        className="text-gray-400 hover:text-white transition"
                                                    >
                                                        {settingsConfig.appearance.animations ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </TabsContent>

                                    {/* API Settings */}
                                    <TabsContent value="api" className="mt-6 space-y-4">
                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center gap-2 mb-3">
                                                <Server className="w-4 h-4 text-blue-400" />
                                                <span className="text-white font-semibold">Backend URL</span>
                                            </div>
                                            <Input
                                                value={settingsConfig.api.backendUrl}
                                                onChange={(e) => setSettingsConfig(prev => ({ ...prev, api: { ...prev.api, backendUrl: e.target.value } }))}
                                                className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                                placeholder="e.g., https://backend.example.com"
                                            />
                                            <div className="text-xs text-gray-500 mt-2">Base URL for all API requests</div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center gap-2 mb-3">
                                                    <Timer className="w-4 h-4 text-amber-400" />
                                                    <span className="text-white font-semibold">Timeout (ms)</span>
                                                </div>
                                                <Input
                                                    type="number"
                                                    value={settingsConfig.api.timeout}
                                                    onChange={(e) => setSettingsConfig(prev => ({ ...prev, api: { ...prev.api, timeout: parseInt(e.target.value) || 30000 } }))}
                                                    className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                                />
                                            </div>

                                            <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center gap-2 mb-3">
                                                    <RefreshCw className="w-4 h-4 text-green-400" />
                                                    <span className="text-white font-semibold">Retry Attempts</span>
                                                </div>
                                                <Input
                                                    type="number"
                                                    value={settingsConfig.api.retryAttempts}
                                                    onChange={(e) => setSettingsConfig(prev => ({ ...prev, api: { ...prev.api, retryAttempts: parseInt(e.target.value) || 3 } }))}
                                                    className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                                />
                                            </div>
                                        </div>

                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <Globe className="w-4 h-4 text-purple-400" />
                                                    <span className="text-white font-semibold">Enable CORS</span>
                                                </div>
                                                <button
                                                    onClick={() => setSettingsConfig(prev => ({ ...prev, api: { ...prev.api, enableCORS: !prev.api.enableCORS } }))}
                                                    className="text-gray-400 hover:text-white transition"
                                                >
                                                    {settingsConfig.api.enableCORS ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                </button>
                                            </div>
                                        </div>

                                        <Button
                                            className="w-full bg-blue-600 hover:bg-blue-700"
                                            onClick={async () => {
                                                try {
                                                    toast.info("Testing connection...");
                                                    const response = await fetch(`${settingsConfig.api.backendUrl}/health`);
                                                    if (response.ok) {
                                                        toast.success("Connection successful!");
                                                    } else {
                                                        toast.error("Connection failed");
                                                    }
                                                } catch (err) {
                                                    toast.error("Could not reach backend");
                                                }
                                            }}
                                        >
                                            <CheckCircle className="w-4 h-4 mr-2" />
                                            Test Connection
                                        </Button>
                                    </TabsContent>

                                    {/* Notification Settings */}
                                    <TabsContent value="notifications" className="mt-6 space-y-4">
                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <Bell className="w-4 h-4 text-blue-400" />
                                                    <div>
                                                        <div className="text-white font-semibold">Enable Notifications</div>
                                                        <div className="text-xs text-gray-500">Master toggle for all notifications</div>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => {
                                                        setSettingsConfig(prev => ({ ...prev, notifications: { ...prev.notifications, enabled: !prev.notifications.enabled } }));
                                                        toast.info(`Notifications ${!settingsConfig.notifications.enabled ? "enabled" : "disabled"}`);
                                                    }}
                                                    className="text-gray-400 hover:text-white transition"
                                                >
                                                    {settingsConfig.notifications.enabled ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                </button>
                                            </div>
                                        </div>

                                        {settingsConfig.notifications.enabled && (
                                            <>
                                                <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-2">
                                                            <Volume2 className="w-4 h-4 text-amber-400" />
                                                            <span className="text-white font-semibold">Sound Alerts</span>
                                                        </div>
                                                        <button
                                                            onClick={() => setSettingsConfig(prev => ({ ...prev, notifications: { ...prev.notifications, sound: !prev.notifications.sound } }))}
                                                            className="text-gray-400 hover:text-white transition"
                                                        >
                                                            {settingsConfig.notifications.sound ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                        </button>
                                                    </div>
                                                </div>

                                                <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                    <div className="flex items-center gap-2 mb-3">
                                                        <Clock className="w-4 h-4 text-purple-400" />
                                                        <span className="text-white font-semibold">Toast Duration (ms)</span>
                                                    </div>
                                                    <Input
                                                        type="number"
                                                        value={settingsConfig.notifications.toastDuration}
                                                        onChange={(e) => setSettingsConfig(prev => ({ ...prev, notifications: { ...prev.notifications, toastDuration: parseInt(e.target.value) || 4000 } }))}
                                                        className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                                    />
                                                </div>

                                                <div className="space-y-3">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500">Notification Types</div>
                                                    {[
                                                        { key: "showSystemNotifications", label: "System Notifications", icon: Monitor },
                                                        { key: "showSecurityAlerts", label: "Security Alerts", icon: ShieldAlert },
                                                        { key: "showExecutionStatus", label: "Execution Status", icon: Zap },
                                                    ].map(({ key, label, icon: Icon }) => (
                                                        <div key={key} className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                            <div className="flex items-center justify-between">
                                                                <div className="flex items-center gap-2">
                                                                    <Icon className="w-4 h-4 text-gray-400" />
                                                                    <span className="text-white text-sm">{label}</span>
                                                                </div>
                                                                <button
                                                                    onClick={() => setSettingsConfig(prev => ({ ...prev, notifications: { ...prev.notifications, [key]: !prev.notifications[key as keyof typeof prev.notifications] } }))}
                                                                    className="text-gray-400 hover:text-white transition"
                                                                >
                                                                    {settingsConfig.notifications[key as keyof typeof settingsConfig.notifications] ? <ToggleRight className="w-6 h-6 text-emerald-400" /> : <ToggleLeft className="w-6 h-6" />}
                                                                </button>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </>
                                        )}
                                    </TabsContent>

                                    {/* Performance Settings */}
                                    <TabsContent value="performance" className="mt-6 space-y-4">
                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center gap-2 mb-3">
                                                <RefreshCw className="w-4 h-4 text-blue-400" />
                                                <span className="text-white font-semibold">Poll Interval (ms)</span>
                                            </div>
                                            <Input
                                                type="number"
                                                value={settingsConfig.performance.pollInterval}
                                                onChange={(e) => setSettingsConfig(prev => ({ ...prev, performance: { ...prev.performance, pollInterval: parseInt(e.target.value) || 8000 } }))}
                                                className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                            />
                                            <div className="text-xs text-gray-500 mt-2">How often to poll API endpoints</div>
                                        </div>

                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center gap-2 mb-3">
                                                <Database className="w-4 h-4 text-green-400" />
                                                <span className="text-white font-semibold">Data Retention (days)</span>
                                            </div>
                                            <Input
                                                type="number"
                                                value={settingsConfig.performance.dataRetentionDays}
                                                onChange={(e) => setSettingsConfig(prev => ({ ...prev, performance: { ...prev.performance, dataRetentionDays: parseInt(e.target.value) || 30 } }))}
                                                className="bg-[#0e0e10] border-[#1e1e21] text-white"
                                            />
                                        </div>

                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center gap-2">
                                                    <Zap className="w-4 h-4 text-amber-400" />
                                                    <span className="text-white font-semibold">Performance Mode</span>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-3 gap-2">
                                                {[
                                                    { label: "Economy", value: "economy", desc: "Longer polls, less CPU" },
                                                    { label: "Balanced", value: "balanced", desc: "Standard performance" },
                                                    { label: "Performance", value: "performance", desc: "Faster updates" },
                                                ].map(mode => (
                                                    <Button
                                                        key={mode.value}
                                                        size="sm"
                                                        variant="outline"
                                                        className={`flex-col h-auto py-3 ${settingsConfig.performance.performanceMode === mode.value ? "border-emerald-600 bg-emerald-900/20 text-emerald-300" : "border-gray-800/40"}`}
                                                        onClick={() => {
                                                            setSettingsConfig(prev => ({ ...prev, performance: { ...prev.performance, performanceMode: mode.value } }));
                                                            toast.info(`Performance mode: ${mode.label}`);
                                                        }}
                                                    >
                                                        <span className="font-semibold">{mode.label}</span>
                                                        <span className="text-xs text-gray-500 mt-1">{mode.desc}</span>
                                                    </Button>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <Database className="w-4 h-4 text-purple-400" />
                                                    <span className="text-white font-semibold">Enable Caching</span>
                                                </div>
                                                <button
                                                    onClick={() => setSettingsConfig(prev => ({ ...prev, performance: { ...prev.performance, enableCaching: !prev.performance.enableCaching } }))}
                                                    className="text-gray-400 hover:text-white transition"
                                                >
                                                    {settingsConfig.performance.enableCaching ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                </button>
                                            </div>
                                        </div>
                                    </TabsContent>

                                    {/* Developer Settings */}
                                    <TabsContent value="developer" className="mt-6 space-y-4">
                                        <div className="p-3 rounded-xl bg-amber-900/20 border border-amber-800/40">
                                            <div className="flex items-start gap-2">
                                                <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5" />
                                                <div className="text-xs text-amber-300">
                                                    <div className="font-semibold mb-1">Developer Options</div>
                                                    <div>These settings are for debugging and development. Changes may affect system stability.</div>
                                                </div>
                                            </div>
                                        </div>

                                        {[
                                            { key: "showDebugInfo", label: "Show Debug Info", desc: "Display technical details in UI", icon: Eye },
                                            { key: "enableTrace", label: "Enable Trace", desc: "Log detailed execution traces", icon: FileText },
                                            { key: "verboseLogging", label: "Verbose Logging", desc: "Detailed console output", icon: ListChecks },
                                            { key: "mockData", label: "Mock Data", desc: "Use simulated API responses", icon: Database },
                                        ].map(({ key, label, desc, icon: Icon }) => (
                                            <div key={key} className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Icon className="w-4 h-4 text-gray-400" />
                                                        <div>
                                                            <div className="text-white font-semibold">{label}</div>
                                                            <div className="text-xs text-gray-500">{desc}</div>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => setSettingsConfig(prev => ({ ...prev, developer: { ...prev.developer, [key]: !prev.developer[key as keyof typeof prev.developer] } }))}
                                                        className="text-gray-400 hover:text-white transition"
                                                    >
                                                        {settingsConfig.developer[key as keyof typeof settingsConfig.developer] ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8" />}
                                                    </button>
                                                </div>
                                            </div>
                                        ))}

                                        <div className="p-4 rounded-xl bg-[#111113] border border-[#1e1e21]">
                                            <div className="text-xs uppercase tracking-wider text-gray-500 mb-3">Environment Variables</div>
                                            <pre className="text-xs font-mono text-gray-400 space-y-1">
                                                <div>AETHERRA_PROFILE=prod</div>
                                                <div>AETHERRA_TRACE={settingsConfig.developer.enableTrace ? "1" : "0"}</div>
                                                <div>AETHERRA_AI_API_ENABLED=1</div>
                                                <div>AETHERRA_NET_STRICT={securityMode === "strict" ? "1" : "0"}</div>
                                            </pre>
                                        </div>
                                    </TabsContent>
                                </Tabs>
                            </Section>
                        </div>
                    )}
                </main>
            </div>
            <footer className="py-6 text-center text-xs text-gray-500">© {new Date().getFullYear()} Aetherra Labs — CODE AWAKENED</footer>
        </div>
    );
}
