import { Canvas, useFrame } from "@react-three/fiber";
import {
    Activity,
    Brain,
    CircleDot,
    GitBranch,
    Network,
    RefreshCw,
    Shield,
    ShieldCheck,
    Sparkles,
    Stethoscope,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

type NodeStatus = "active" | "stable" | "degraded" | "contained" | "offline" | "unknown";

interface ObservatoryNode {
    name: string;
    label: string;
    group: string;
    x: number;
    y: number;
    z: number;
    radius: number;
    emphasis: number;
    status: NodeStatus;
    accessibility_label: string;
}

interface ObservatoryConnection {
    source: string;
    target: string;
    label: string;
    status: NodeStatus;
    pulse: number;
    thickness: number;
}

interface ObservatoryEvent {
    id?: string;
    source: string;
    title?: string;
    event_type?: string;
    occurred_at?: string;
    summary: string;
    severity: string;
    visual_channel: string;
}

interface BootstrapPayload {
    ok: boolean;
    read_only: boolean;
    manifest: {
        controls_enabled: boolean;
        legacy_ui_enabled: boolean;
        contract_version: string;
    };
    observatory: {
        core_label: string;
        mode: string;
        greeting: string | null;
        generated_at?: string;
        read_only: boolean;
        subsystems: Array<{
            name: string;
            label: string;
            status: NodeStatus;
            activity: number;
            summary?: string;
            metrics: Record<string, string | number | boolean | null>;
        }>;
        events: ObservatoryEvent[];
    };
    scene: {
        core_label: string;
        read_only: boolean;
        nodes: ObservatoryNode[];
        connections: ObservatoryConnection[];
    };
    activity: {
        events: ObservatoryEvent[];
        total: number;
        limit: number;
    };
}

const NODE_COLORS: Record<NodeStatus, string> = {
    active: "#64d8ff",
    stable: "#7cffbd",
    degraded: "#ffd166",
    contained: "#ff5a6f",
    offline: "#7d8796",
    unknown: "#b8c0cc",
};

const FALLBACK_BOOTSTRAP: BootstrapPayload = {
    ok: false,
    read_only: true,
    manifest: {
        controls_enabled: false,
        legacy_ui_enabled: false,
        contract_version: "1.0",
    },
    observatory: {
        core_label: "AETHERRA",
        mode: "first_launch",
        greeting: "I can't see Aetherra's runtime right now.",
        read_only: true,
        subsystems: [
            { name: "guardian", label: "Guardian", status: "unknown", activity: 0, metrics: { authority: "decide" } },
            { name: "security", label: "Security", status: "unknown", activity: 0, metrics: { authority: "enforce" } },
            { name: "homeostasis", label: "Homeostasis", status: "unknown", activity: 0, metrics: { authority: "verify" } },
            { name: "engine", label: "Engine", status: "unknown", activity: 0, metrics: { authority: "reason" } },
            { name: "memory", label: "Memory", status: "unknown", activity: 0, metrics: { authority: "remember" } },
            { name: "consciousness", label: "Consciousness", status: "unknown", activity: 0, metrics: { authority: "observe" } },
            { name: "agents", label: "Agents", status: "unknown", activity: 0, metrics: { authority: "coordinate" } },
            { name: "self_improvement", label: "Self-Improvement", status: "unknown", activity: 0, metrics: { authority: "propose" } },
            { name: "self_incorporation", label: "Self-Incorporation", status: "unknown", activity: 0, metrics: { authority: "execute_approved" } },
            { name: "maintenance", label: "Maintenance", status: "unknown", activity: 0, metrics: { authority: "coordinate" } },
            { name: "aether_script", label: "Aether Script", status: "unknown", activity: 0, metrics: { authority: "workflow" } },
            { name: "kernel", label: "Kernel", status: "unknown", activity: 0, metrics: { authority: "schedule" } },
            { name: "integration_validation", label: "Integration Validation", status: "unknown", activity: 0, metrics: { authority: "validate" } },
        ],
        events: [],
    },
    scene: {
        core_label: "AETHERRA",
        read_only: true,
        nodes: [],
        connections: [],
    },
    activity: {
        events: [],
        total: 0,
        limit: 8,
    },
};

async function loadBootstrap(): Promise<{ payload: BootstrapPayload; source: "api" | "fallback" }> {
    try {
        const response = await fetch("/api/runtime-ui/bootstrap?mode=first_launch&user=Tim&limit=8", {
            headers: { Accept: "application/json" },
            signal: AbortSignal.timeout(8000),
        });
        if (!response.ok) {
            throw new Error(`runtime-ui:${response.status}`);
        }
        const nextPayload = (await response.json()) as BootstrapPayload;
        const validStatus = (status: NodeStatus) => ["active", "stable", "degraded", "contained", "offline", "unknown"].includes(status);
        const validEvent = (event: ObservatoryEvent) => event && typeof event.source === "string" &&
            typeof event.summary === "string" &&
            (event.event_type === undefined || typeof event.event_type === "string") &&
            (event.occurred_at === undefined || typeof event.occurred_at === "string");
        const age = Date.now() - Date.parse(nextPayload.observatory?.generated_at ?? "");
        if (nextPayload.ok !== true || nextPayload.read_only !== true ||
            nextPayload.manifest?.controls_enabled !== false ||
            typeof nextPayload.manifest.contract_version !== "string" ||
            !Array.isArray(nextPayload.observatory?.subsystems) ||
            !nextPayload.observatory.subsystems.every((node) => node &&
                typeof node.name === "string" && typeof node.label === "string" &&
                Number.isFinite(node.activity) &&
                (node.summary === undefined || typeof node.summary === "string") &&
                node.metrics && typeof node.metrics === "object" && !Array.isArray(node.metrics) &&
                validStatus(node.status)) ||
            !Array.isArray(nextPayload.scene?.nodes) || !Array.isArray(nextPayload.scene?.connections) ||
            !nextPayload.scene.nodes.every((node) => node && typeof node.name === "string" &&
                [node.x, node.y, node.z, node.radius, node.emphasis].every(Number.isFinite) &&
                node.radius > 0 && validStatus(node.status)) ||
            !nextPayload.scene.connections.every((connection) => connection &&
                typeof connection.source === "string" && typeof connection.target === "string" &&
                typeof connection.label === "string" && Number.isFinite(connection.pulse) && validStatus(connection.status)) ||
            !Array.isArray(nextPayload.activity?.events) || !nextPayload.activity.events.every(validEvent) ||
            !Array.isArray(nextPayload.observatory.events) || !nextPayload.observatory.events.every(validEvent) ||
            !Number.isFinite(age) || age < -5000 || age > 60000) {
            throw new Error("runtime-ui:invalid-or-stale");
        }
        return { payload: normalizeBootstrap(nextPayload), source: "api" };
    } catch {
        return { payload: normalizeBootstrap(FALLBACK_BOOTSTRAP), source: "fallback" };
    }
}

function App() {
    const [payload, setPayload] = useState<BootstrapPayload>(FALLBACK_BOOTSTRAP);
    const [selectedNode, setSelectedNode] = useState("guardian");
    const [loading, setLoading] = useState(true);
    const [source, setSource] = useState<"api" | "fallback">("fallback");
    const inFlight = useRef(false);

    const refresh = async () => {
        // One bounded request at a time: an older response cannot revive stale state.
        if (inFlight.current) return;
        inFlight.current = true;
        const next = await loadBootstrap();
        setPayload(next.payload);
        setSource(next.source);
        setLoading(false);
        inFlight.current = false;
    };

    useEffect(() => {
        void refresh();
        const timer = window.setInterval(() => void refresh(), 15000);
        return () => window.clearInterval(timer);
    }, []);

    const selected = useMemo(() => {
        return payload.observatory.subsystems.find((item) => item.name === selectedNode) ?? payload.observatory.subsystems[0];
    }, [payload.observatory.subsystems, selectedNode]);

    const coreState = summarizeCoreState(payload);

    return (
        <main className="observatory-shell">
            <section className="space-stage" aria-label="Aetherra Cognitive Observatory">
                <div className="stellar-field" />
                <Canvas camera={{ position: [0, 0, 3.25], fov: 48 }} dpr={[1, 1.7]}>
                    <ambientLight intensity={0.28} />
                    <pointLight position={[0, 0.2, 2]} intensity={5} color="#c8fff0" />
                    <ObservatoryScene payload={payload} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
                </Canvas>
            </section>

            <section className="top-status" aria-label="Runtime status">
                <div className="identity-lockup">
                    <span className="presence-mark" style={coreState === "System Online" ? undefined : { background: NODE_COLORS.unknown, boxShadow: "none" }} />
                    <div>
                        <h1>AETHERRA</h1>
                        <p>{coreState}</p>
                    </div>
                </div>
                <div className="system-line">
                    <StatusPill icon={ShieldCheck} label="Guardian" status={statusFor(payload, "guardian")} />
                    <StatusPill icon={Shield} label="Security" status={statusFor(payload, "security")} />
                    <StatusPill icon={Stethoscope} label="Homeostasis" status={statusFor(payload, "homeostasis")} />
                    <StatusPill icon={Brain} label="Memory" status={statusFor(payload, "memory")} />
                </div>
            </section>

            <section className="center-presence" aria-label="Core prompt">
                <p className="greeting">{source === "api" ? "I'm here to help you observe Aetherra." : payload.observatory.greeting}</p>
                <p className="prompt">{source === "api" ? "Select a system to inspect its evidence." : "Runtime status is unavailable. Check the connection and try again."}</p>
            </section>

            <aside className="system-dock" aria-label="Subsystems">
                <div className="dock-head">
                    <div>
                        <p className="eyebrow">Architect Mode</p>
                        <h2>Living Systems</h2>
                    </div>
                    <button className="icon-button" type="button" onClick={() => {
                        setLoading(true);
                        void refresh();
                    }} aria-label="Refresh runtime state">
                        <RefreshCw className={loading ? "spin" : ""} size={18} />
                    </button>
                </div>
                <div className="node-list">
                    {payload.observatory.subsystems.map((node) => (
                        <button
                            className={`node-row ${selected?.name === node.name ? "selected" : ""}`}
                            key={node.name}
                            type="button"
                            onClick={() => setSelectedNode(node.name)}
                        >
                            <span className={`node-signal ${node.status}`} />
                            <span>{node.label}</span>
                            <small>{node.status}</small>
                        </button>
                    ))}
                </div>
            </aside>

            <aside className="inspector-panel" aria-label="Selected subsystem">
                <div className="inspector-head">
                    <p className="eyebrow">Subsystem</p>
                    <h2>{selected?.label ?? "Aetherra"}</h2>
                    <span className={`state-badge ${selected?.status ?? "unknown"}`}>{selected?.status ?? "unknown"}</span>
                </div>
                <div className="metric-grid">
                    <Metric icon={Activity} label="Activity" value={selected?.metrics?.activity_measured === true ? `${Math.round(selected.activity * 100)}%` : "Not measured"} />
                    <Metric icon={Network} label="Source" value={source === "api" ? "Runtime API" : "Unavailable"} />
                    <Metric icon={CircleDot} label="Contract" value={payload.manifest.contract_version} />
                    <Metric icon={GitBranch} label="Controls" value={payload.manifest.controls_enabled ? "Enabled" : "Read only"} />
                </div>
                <p>{source === "api" ? selected?.summary : "No current evidence is available for this system."}</p>
                <div className="authority-strip">
                    <Sparkles size={16} />
                    <span>{authorityLabel(selected?.metrics)}</span>
                </div>
                <div className="event-feed">
                    <p className="eyebrow">Recent Activity</p>
                    {(payload.activity.events.length ? payload.activity.events : payload.observatory.events).slice(0, 5).map((event) => (
                        <article className="event-row" key={event.id}>
                            <span className={`node-signal ${event.severity}`} />
                            <div>
                                <strong>{event.title}</strong>
                                <p>{event.summary}</p>
                            </div>
                        </article>
                    ))}
                </div>
            </aside>

            <footer className="alpha-footer">
                <span>Runtime UI Alpha Shell</span>
                <span>{payload.read_only ? "Read-only observatory" : "Controls available"}</span>
                <span>{payload.manifest.legacy_ui_enabled ? "Legacy UI linked" : "Legacy UI disabled"}</span>
            </footer>
        </main>
    );
}

function ObservatoryScene({
    payload,
    selectedNode,
    onSelectNode,
}: {
    payload: BootstrapPayload;
    selectedNode: string;
    onSelectNode: (node: string) => void;
}) {
    const groupRef = useRef<THREE.Group>(null);
    const nodes = payload.scene.nodes.length ? payload.scene.nodes : fallbackSceneNodes(payload);
    const connections = payload.scene.connections.length ? payload.scene.connections : fallbackConnections(nodes);

    useFrame(({ clock }) => {
        if (!groupRef.current) {
            return;
        }
        groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.18) * 0.08;
        groupRef.current.rotation.x = Math.sin(clock.elapsedTime * 0.12) * 0.035;
    });

    return (
        <group ref={groupRef}>
            <CorePresence />
            {connections.map((connection) => (
                <ConnectionLine connection={connection} key={`${connection.source}-${connection.target}-${connection.label}`} nodes={nodes} />
            ))}
            {nodes.map((node) => (
                <NodeOrb key={node.name} node={node} selected={node.name === selectedNode} onSelectNode={onSelectNode} />
            ))}
            <ParticleHalo />
        </group>
    );
}

function CorePresence() {
    const meshRef = useRef<THREE.Mesh>(null);

    useFrame(({ clock }) => {
        if (meshRef.current) {
            const scale = 1 + Math.sin(clock.elapsedTime * 1.2) * 0.035;
            meshRef.current.scale.setScalar(scale);
            meshRef.current.rotation.y = clock.elapsedTime * 0.2;
        }
    });

    return (
        <mesh ref={meshRef}>
            <sphereGeometry args={[0.22, 48, 48]} />
            <meshStandardMaterial color="#f5fff9" emissive="#7cffbd" emissiveIntensity={1.2} roughness={0.35} metalness={0.2} />
        </mesh>
    );
}

function NodeOrb({
    node,
    selected,
    onSelectNode,
}: {
    node: ObservatoryNode;
    selected: boolean;
    onSelectNode: (node: string) => void;
}) {
    const meshRef = useRef<THREE.Mesh>(null);
    const color = NODE_COLORS[node.status];

    useFrame(({ clock }) => {
        if (!meshRef.current) {
            return;
        }
        const pulse = 1 + Math.sin(clock.elapsedTime * 1.5 + node.emphasis * 5) * 0.06;
        meshRef.current.scale.setScalar(selected ? pulse * 1.25 : pulse);
    });

    return (
        <mesh
            ref={meshRef}
            position={[node.x, node.y, node.z]}
            onClick={(event) => {
                event.stopPropagation();
                onSelectNode(node.name);
            }}
        >
            <sphereGeometry args={[node.radius, 32, 32]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={selected ? 1.8 : 0.9} transparent opacity={0.86} />
        </mesh>
    );
}

function ConnectionLine({ connection, nodes }: { connection: ObservatoryConnection; nodes: ObservatoryNode[] }) {
    const source = nodes.find((node) => node.name === connection.source);
    const target = nodes.find((node) => node.name === connection.target);
    const positions = useMemo(() => {
        if (!source || !target) {
            return new Float32Array();
        }
        return new Float32Array([source.x, source.y, source.z, target.x, target.y, target.z]);
    }, [source, target]);

    if (!source || !target) {
        return null;
    }

    return (
        <line>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" args={[positions, 3]} />
            </bufferGeometry>
            <lineBasicMaterial color={NODE_COLORS[connection.status]} transparent opacity={0.2 + connection.pulse * 0.45} />
        </line>
    );
}

function ParticleHalo() {
    const points = useMemo(() => {
        const vertices: number[] = [];
        for (let index = 0; index < 140; index += 1) {
            const radius = 1.15 + (index % 17) * 0.045;
            const angle = index * 2.399963;
            const y = Math.sin(index * 0.73) * 0.78;
            vertices.push(Math.cos(angle) * radius, y, Math.sin(angle) * radius * 0.22);
        }
        return new Float32Array(vertices);
    }, []);

    return (
        <points>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" args={[points, 3]} />
            </bufferGeometry>
            <pointsMaterial color="#b6ffee" size={0.012} transparent opacity={0.45} sizeAttenuation />
        </points>
    );
}

function StatusPill({ icon: Icon, label, status }: { icon: typeof Shield; label: string; status: NodeStatus }) {
    return (
        <div className={`status-pill ${status}`}>
            <Icon size={16} />
            <span>{label}</span>
            <strong>{status}</strong>
        </div>
    );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Activity; label: string; value: string }) {
    return (
        <div className="metric">
            <Icon size={17} />
            <span>{label}</span>
            <strong>{value}</strong>
        </div>
    );
}

function normalizeBootstrap(payload: BootstrapPayload): BootstrapPayload {
    const normalizeEvents = (events: ObservatoryEvent[] = []) => events.map((event, index) => ({
        ...event,
        // The API's event_type/timestamp contract has no renderer id or title.
        id: `${event.source}:${event.event_type ?? "status"}:${event.occurred_at ?? ""}:${index}`,
        title: (event.event_type ?? "status").replace(/_/g, " "),
        severity: ["error", "critical"].includes(event.severity) ? "contained" :
            event.severity === "warning" ? "degraded" : "unknown",
    }));
    return {
        ...payload,
        activity: {
            ...payload.activity,
            events: normalizeEvents(payload.activity?.events),
        },
        observatory: {
            ...payload.observatory,
            subsystems: payload.observatory?.subsystems ?? [],
            events: normalizeEvents(payload.observatory?.events),
        },
        scene: {
            ...payload.scene,
            nodes: payload.scene?.nodes ?? [],
            connections: payload.scene?.connections ?? [],
        },
    };
}

function summarizeCoreState(payload: BootstrapPayload): string {
    if (!payload.ok) return "Runtime unavailable";
    const contained = payload.observatory.subsystems.filter((item) => item.status === "contained").length;
    const degraded = payload.observatory.subsystems.filter((item) => item.status === "degraded").length;
    if (contained > 0) {
        return "Containment active";
    }
    if (degraded > 0) {
        return "Degraded systems visible";
    }
    if (!payload.observatory.subsystems.length || payload.observatory.subsystems.some((item) => ["unknown", "offline"].includes(item.status))) {
        return "Runtime status incomplete";
    }
    return "System Online";
}

function statusFor(payload: BootstrapPayload, name: string): NodeStatus {
    return payload.observatory.subsystems.find((item) => item.name === name)?.status ?? "unknown";
}

function authorityLabel(metrics: Record<string, string | number | boolean | null> | undefined): string {
    const authority = metrics?.authority;
    if (typeof authority === "string") {
        return `Authority: ${authority.replace(/_/g, " ")}`;
    }
    return "Authority: observe only";
}

function fallbackSceneNodes(payload: BootstrapPayload): ObservatoryNode[] {
    const layout = [
        [-0.22, 0.62, 0],
        [0.62, 0.34, 0],
        [0.88, 0.04, 0],
        [0.58, -0.42, 0],
        [0, -0.72, 0],
        [-0.42, -0.46, 0],
        [0.02, -0.24, 0.08],
        [-0.7, 0.16, 0],
        [-0.78, -0.32, 0],
        [-0.34, -0.08, 0],
        [0.24, 0.66, 0],
        [0, 0.92, -0.02],
        [-0.65, 0.68, -0.05],
    ];
    return payload.observatory.subsystems.map((node, index) => {
        const [x, y, z] = layout[index % layout.length];
        return {
            name: node.name,
            label: node.label,
            group: groupFor(node.name),
            x,
            y,
            z,
            radius: 0.11 + node.activity * 0.05,
            emphasis: node.activity,
            status: node.status,
            accessibility_label: `${node.label}: ${node.status}`,
        };
    });
}

function fallbackConnections(nodes: ObservatoryNode[]): ObservatoryConnection[] {
    const important = ["guardian", "security", "homeostasis", "maintenance", "self_improvement", "self_incorporation", "memory", "consciousness"];
    return important.slice(0, -1).map((source, index) => ({
        source,
        target: important[index + 1],
        label: "runtime",
        status: nodes.find((node) => node.name === source)?.status ?? "unknown",
        pulse: nodes.find((node) => node.name === source)?.emphasis ?? 0,
        thickness: 0.4,
    }));
}

function groupFor(name: string): string {
    if (["guardian", "security"].includes(name)) {
        return "governance";
    }
    if (["homeostasis", "maintenance"].includes(name)) {
        return "regulation";
    }
    if (["self_improvement", "self_incorporation"].includes(name)) {
        return "evolution";
    }
    if (["memory", "consciousness"].includes(name)) {
        return "cognition";
    }
    if (name === "integration_validation") {
        return "readiness";
    }
    return "runtime";
}

export default App;
