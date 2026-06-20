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
    id: string;
    source: string;
    title: string;
    summary: string;
    severity: NodeStatus;
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
        read_only: boolean;
        subsystems: Array<{
            name: string;
            label: string;
            status: NodeStatus;
            activity: number;
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
    ok: true,
    read_only: true,
    manifest: {
        controls_enabled: false,
        legacy_ui_enabled: false,
        contract_version: "1.0",
    },
    observatory: {
        core_label: "AETHERRA",
        mode: "first_launch",
        greeting: "Good morning, Tim.",
        read_only: true,
        subsystems: [
            { name: "guardian", label: "Guardian", status: "active", activity: 0.88, metrics: { authority: "decide" } },
            { name: "security", label: "Security", status: "active", activity: 0.82, metrics: { authority: "enforce" } },
            { name: "homeostasis", label: "Homeostasis", status: "stable", activity: 0.64, metrics: { authority: "verify" } },
            { name: "memory", label: "Memory", status: "stable", activity: 0.58, metrics: { authority: "remember" } },
            { name: "consciousness", label: "Consciousness", status: "stable", activity: 0.52, metrics: { authority: "observe" } },
            { name: "agents", label: "Agents", status: "stable", activity: 0.46, metrics: { authority: "coordinate" } },
            { name: "self_improvement", label: "Self-Improvement", status: "stable", activity: 0.5, metrics: { authority: "propose" } },
            { name: "self_incorporation", label: "Self-Incorporation", status: "stable", activity: 0.43, metrics: { authority: "execute_approved" } },
            { name: "maintenance", label: "Maintenance", status: "stable", activity: 0.48, metrics: { authority: "coordinate" } },
            { name: "aether_script", label: "Aether Script", status: "stable", activity: 0.42, metrics: { authority: "workflow" } },
            { name: "kernel", label: "Kernel", status: "stable", activity: 0.6, metrics: { authority: "schedule" } },
            { name: "integration_validation", label: "Integration Validation", status: "stable", activity: 0.36, metrics: { authority: "validate" } },
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
        events: [
            {
                id: "fallback-guardian",
                source: "guardian",
                title: "Guardian active",
                summary: "Governance layer is visible to the alpha shell.",
                severity: "active",
                visual_channel: "governance",
            },
            {
                id: "fallback-security",
                source: "security",
                title: "Security active",
                summary: "Capability and audit systems remain authoritative.",
                severity: "active",
                visual_channel: "governance",
            },
        ],
        total: 2,
        limit: 8,
    },
};

function App() {
    const [payload, setPayload] = useState<BootstrapPayload>(FALLBACK_BOOTSTRAP);
    const [selectedNode, setSelectedNode] = useState("guardian");
    const [loading, setLoading] = useState(false);
    const [source, setSource] = useState<"api" | "fallback">("fallback");

    const refresh = async () => {
        setLoading(true);
        try {
            const response = await fetch("/api/runtime-ui/bootstrap?mode=first_launch&user=Tim&limit=8", {
                headers: { Accept: "application/json" },
            });
            if (!response.ok) {
                throw new Error(`runtime-ui:${response.status}`);
            }
            const nextPayload = (await response.json()) as BootstrapPayload;
            setPayload(normalizeBootstrap(nextPayload));
            setSource("api");
        } catch {
            setPayload(normalizeBootstrap(FALLBACK_BOOTSTRAP));
            setSource("fallback");
        } finally {
            setLoading(false);
        }
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
                    <span className="presence-mark" />
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
                <p className="greeting">{payload.observatory.greeting ?? "System Online"}</p>
                <p className="prompt">What would you like to do today?</p>
            </section>

            <aside className="system-dock" aria-label="Subsystems">
                <div className="dock-head">
                    <div>
                        <p className="eyebrow">Architect Mode</p>
                        <h2>Living Systems</h2>
                    </div>
                    <button className="icon-button" type="button" onClick={() => void refresh()} aria-label="Refresh runtime state">
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
                    <Metric icon={Activity} label="Activity" value={`${Math.round((selected?.activity ?? 0) * 100)}%`} />
                    <Metric icon={Network} label="Source" value={source === "api" ? "Runtime API" : "Fallback"} />
                    <Metric icon={CircleDot} label="Contract" value={payload.manifest.contract_version} />
                    <Metric icon={GitBranch} label="Controls" value={payload.manifest.controls_enabled ? "Enabled" : "Read only"} />
                </div>
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
    return {
        ...payload,
        activity: {
            ...payload.activity,
            events: payload.activity?.events ?? [],
        },
        observatory: {
            ...payload.observatory,
            subsystems: payload.observatory?.subsystems ?? [],
            events: payload.observatory?.events ?? [],
        },
        scene: {
            ...payload.scene,
            nodes: payload.scene?.nodes ?? [],
            connections: payload.scene?.connections ?? [],
        },
    };
}

function summarizeCoreState(payload: BootstrapPayload): string {
    const contained = payload.observatory.subsystems.filter((item) => item.status === "contained").length;
    const degraded = payload.observatory.subsystems.filter((item) => item.status === "degraded").length;
    if (contained > 0) {
        return "Containment active";
    }
    if (degraded > 0) {
        return "Degraded systems visible";
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
        status: nodes.find((node) => node.name === source)?.status ?? "stable",
        pulse: nodes.find((node) => node.name === source)?.emphasis ?? 0.4,
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
