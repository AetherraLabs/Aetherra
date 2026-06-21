
import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { AetherraAvatar } from "./AetherraAvatar";

// Minimal Zustand-like store for metrics
const metricsInitial = { cpu: 0, mem: 0, net: 0 };
const listeners = [];
let metrics = { ...metricsInitial };
function updateMetrics(data) {
    let changed = false;
    if (data.metrics) {
        for (const k of Object.keys(metricsInitial)) {
            if (typeof data.metrics[k] === "number") {
                metrics[k] = data.metrics[k];
                changed = true;
            }
        }
    }
    if (changed) listeners.forEach(fn => fn(metrics));
}
export const useAetherraStore = {
    getState: () => ({ ...metrics, updateMetrics }),
    subscribe: (fn) => {
        listeners.push(fn);
        return () => {
            const idx = listeners.indexOf(fn);
            if (idx > -1) listeners.splice(idx, 1);
        };
    }
};

// Minimal MetricsOverlay component
function MetricsOverlay() {
    const [metricsState, setMetricsState] = useState({ cpu: 0, mem: 0, net: 0 });
    useEffect(() => {
        setMetricsState(useAetherraStore.getState());
        const unsub = useAetherraStore.subscribe(setMetricsState);
        return unsub;
    }, []);
    return (
        <div className="absolute top-24 left-4 bg-black/70 rounded-lg px-4 py-2 text-green-200 font-mono text-xs border border-green-700/40 shadow">
            <div>CPU: <span className="text-green-400">{metricsState.cpu}%</span></div>
            <div>MEM: <span className="text-green-400">{metricsState.mem} MB</span></div>
            <div>NET: <span className="text-green-400">{metricsState.net} KB/s</span></div>
        </div>
    );
}

function MemoryGraphPanel({ ws }) {
    const [graph, setGraph] = useState({ nodes: [], edges: [] });
    const panelRef = useRef(null);
    useEffect(() => {
        if (!ws) return;
        const handleMsg = (msg) => {
            try {
                const data = JSON.parse(msg.data);
                if (data.type === "memory_graph" && data.nodes && data.edges) {
                    setGraph({ nodes: data.nodes, edges: data.edges });
                }
            } catch (e) { }
        };
        ws.addEventListener("message", handleMsg);
        return () => ws.removeEventListener("message", handleMsg);
    }, [ws]);
    return (
        <motion.div
            ref={panelRef}
            className="absolute right-6 bottom-6 w-[24rem] h-[20rem] bg-[#101c1a]/80 text-green-200 rounded-2xl p-3 shadow-xl border border-green-500/30 backdrop-blur cursor-move select-none"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            drag
            dragMomentum={false}
        >
            <div className="text-lg font-bold mb-2 text-green-300">Memory Graph</div>
            <Canvas camera={{ position: [0, 0, 8], fov: 60 }} style={{ width: '100%', height: '80%' }}>
                <ambientLight intensity={0.7} />
                <pointLight position={[10, 10, 10]} intensity={0.7} />
                {/* Render nodes */}
                {graph.nodes.map((node) => (
                    <mesh key={node.id} position={node.pos}>
                        <sphereGeometry args={[0.22, 24, 24]} />
                        <meshStandardMaterial color={node.color || "#00ff88"} emissive={node.color || "#00ff88"} emissiveIntensity={0.7} />
                    </mesh>
                ))}
                {/* Render edges */}
                {graph.edges.map(([a, b], i) => {
                    const from = graph.nodes.find(n => n.id === a)?.pos;
                    const to = graph.nodes.find(n => n.id === b)?.pos;
                    if (!from || !to) return null;
                    return (
                        <line key={i}>
                            <bufferGeometry>
                                <bufferAttribute
                                    attach="attributes-position"
                                    count={2}
                                    array={new Float32Array([...from, ...to])}
                                    itemSize={3}
                                />
                            </bufferGeometry>
                            <lineBasicMaterial color="#00ff88" linewidth={2} />
                        </line>
                    );
                })}
                <OrbitControls enableZoom={false} enablePan={false} />
            </Canvas>
        </motion.div>
    );
}

function QuantumPanel({ ws }) {
    const [quantum, setQuantum] = useState(null);
    useEffect(() => {
        if (!ws) return;
        const handleMsg = (msg) => {
            try {
                const data = JSON.parse(msg.data);
                if (data.type === "quantum_state") {
                    setQuantum(data);
                }
            } catch (e) { }
        };
        ws.addEventListener("message", handleMsg);
        return () => ws.removeEventListener("message", handleMsg);
    }, [ws]);
    return (
        <motion.div
            className="absolute right-6 top-28 w-[20rem] h-[16rem] bg-[#181a2a]/80 text-purple-200 rounded-2xl p-3 shadow-xl border border-purple-500/30 backdrop-blur cursor-move select-none"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            drag
            dragMomentum={false}
        >
            <div className="text-lg font-bold mb-2 text-purple-300">Quantum State</div>
            <div className="flex flex-col items-center justify-center h-full">
                {quantum ? (
                    <>
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 via-blue-400 to-pink-400 opacity-80 animate-pulse mb-3 flex items-center justify-center text-2xl font-bold text-white">
                            {quantum.label || "Q"}
                        </div>
                        <div className="text-center text-purple-200/80 text-sm">
                            {quantum.description || "Live quantum state received."}
                        </div>
                        {quantum.state && (
                            <div className="mt-2 text-xs text-purple-100/80 break-all max-w-[16rem]">
                                {JSON.stringify(quantum.state)}
                            </div>
                        )}
                    </>
                ) : (
                    <div className="text-purple-400/60">Waiting for quantum state data...</div>
                )}
            </div>
        </motion.div>
    );
}

function BootReadinessPanel({ readinessState }) {
    const readiness = readinessState?.readiness || {};
    const status = (readiness.status || "unknown").toUpperCase();
    const phase = (readiness.phase || "presence").toLowerCase();
    const progress = Number.isFinite(readiness.progress) ? readiness.progress : 0;
    const registry = readiness.system_scan?.registry || {};
    const kernel = readiness.system_scan?.kernel || {};
    const hub = readiness.system_scan?.hub || {};
    const issues = Array.isArray(readiness.issues) ? readiness.issues : [];
    const phases = ["presence", "diagnostics", "ready"];

    const activePhaseIndex =
        phase === "stabilizing"
            ? phases.indexOf("ready")
            : Math.max(0, phases.indexOf(phase));

    const statusClasses =
        status === "READY"
            ? "border-green-500/40 text-green-200"
            : status === "DEGRADED"
                ? "border-yellow-500/40 text-yellow-200"
                : "border-red-500/40 text-red-200";

    return (
        <div className={`absolute top-20 left-4 w-[26rem] bg-black/75 rounded-xl px-4 py-3 text-xs font-mono shadow border backdrop-blur ${statusClasses}`}>
            <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-bold">Aetherra Boot Readiness</div>
                <div className="font-semibold">{status}</div>
            </div>
            <div className="mb-2">
                <div className="flex items-center justify-between text-[10px] opacity-90 mb-1">
                    <span>Phase: {phase.toUpperCase()}</span>
                    <span>{Math.max(0, Math.min(100, progress))}%</span>
                </div>
                <div className="h-1.5 bg-black/60 rounded overflow-hidden">
                    <motion.div
                        className="h-full bg-green-400"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
                        transition={{ duration: 0.4 }}
                    />
                </div>
            </div>
            <div className="flex items-center gap-2 mb-2 text-[10px]">
                {phases.map((p, idx) => {
                    const isReached = idx <= activePhaseIndex;
                    const isActive = idx === activePhaseIndex;
                    return (
                        <div key={p} className={`px-2 py-1 rounded border ${isReached ? "border-green-500/40 text-green-300" : "border-gray-600/40 text-gray-400"} ${isActive ? "animate-pulse" : ""}`}>
                            {p}
                        </div>
                    );
                })}
            </div>
            <div className="opacity-90 mb-2">{readiness.message || "Preparing diagnostics..."}</div>
            <div className="grid grid-cols-2 gap-2 opacity-90">
                <div>Services: {registry.total_services ?? 0}</div>
                <div>Healthy: {registry.healthy_services ?? 0}</div>
                <div>Kernel: {kernel.running ? "Running" : "Stopped"}</div>
                <div>Cycles: {kernel.cycle_count ?? 0}</div>
                <div>Hub: {hub.ok ? "Online" : "Offline"}</div>
                <div>Mode: {readiness.interface_mode || "hybrid"}</div>
            </div>
            {issues.length > 0 && (
                <div className="mt-2 opacity-90">Issues: {issues.slice(0, 2).join("; ")}</div>
            )}
        </div>
    );
}

function NeuralChat({ ws }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    useEffect(() => {
        if (!ws) return;
        const handleMsg = (msg) => {
            try {
                const data = JSON.parse(msg.data);
                if (data.type === "chat_reply" && data.text) {
                    setMessages((prev) => [...prev, { from: "ai", text: data.text }]);
                }
            } catch (e) { }
        };
        ws.addEventListener("message", handleMsg);
        return () => ws.removeEventListener("message", handleMsg);
    }, [ws]);
    const sendMessage = () => {
        if (!input.trim() || !ws || ws.readyState !== 1) return;
        setMessages((prev) => [...prev, { from: "user", text: input }]);
        ws.send(JSON.stringify({ type: "chat", text: input }));
        setInput("");
    };
    return (
        <motion.div
            className="absolute left-6 bottom-6 w-[32rem] h-[28rem] bg-[#1a1a1a]/80 text-green-300 rounded-2xl p-4 overflow-y-auto font-mono shadow-xl backdrop-blur"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
        >
            <div className="text-lg font-bold mb-2">Aetherra</div>
            <div className="h-[20rem] overflow-y-auto space-y-2">
                {messages.map((m, i) => (
                    <div key={i} className={m.from === "user" ? "text-white text-right" : "text-green-300 text-left"}>{m.text}</div>
                ))}
            </div>
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask Aetherra anything..."
                className="w-full mt-3 bg-black/40 p-2 rounded-lg text-green-200 border border-green-500 outline-none"
            />
        </motion.div>
    );
}

export default function AetherraGUI() {
    const [ws, setWs] = useState(null);
    const [wsStatus, setWsStatus] = useState("Connecting...");
    const [readinessState, setReadinessState] = useState({
        available: false,
        readiness: {
            status: "booting",
            phase: "presence",
            progress: 5,
            message: "Connecting to readiness diagnostics...",
            system_scan: {},
            issues: [],
        },
    });
    useEffect(() => {
        let socket;
        try {
            socket = new WebSocket(`ws://${window.location.hostname}:8888/ws`);
            setWs(socket);
            socket.onopen = () => {
                setWsStatus("Connected");
                console.log("WebSocket connected to Aetherra");
            };
            socket.onmessage = (msg) => {
                try {
                    const data = JSON.parse(msg.data);
                    useAetherraStore.getState().updateMetrics(data);
                } catch (e) {
                    console.error("Error parsing WebSocket message:", e);
                }
            };
            socket.onclose = () => {
                setWsStatus("Disconnected");
                console.log("WebSocket disconnected");
            };
            socket.onerror = (error) => {
                setWsStatus("Error");
                console.error("WebSocket error:", error);
            };
        } catch (error) {
            setWsStatus("Failed");
            console.error("Failed to create WebSocket:", error);
        }
        return () => {
            if (socket) socket.close();
        };
    }, []);

    useEffect(() => {
        let cancelled = false;

        const loadReadiness = async () => {
            try {
                const res = await fetch("/api/boot/readiness", { cache: "no-store" });
                if (!res.ok) return;
                const data = await res.json();
                if (!cancelled) {
                    setReadinessState(data);
                }
            } catch (error) {
                if (!cancelled) {
                    setReadinessState((prev) => ({
                        ...prev,
                        readiness: {
                            ...(prev.readiness || {}),
                            status: "degraded",
                            message: "Readiness endpoint unavailable.",
                            issues: ["Could not reach /api/boot/readiness"],
                        },
                    }));
                }
            }
        };

        loadReadiness();
        const timer = setInterval(loadReadiness, 1500);
        return () => {
            cancelled = true;
            clearInterval(timer);
        };
    }, []);

    return (
        <div className="w-screen h-screen bg-[#0a0a0a] overflow-hidden relative">
            <Canvas
                camera={{ position: [0, 0.65, 4.2], fov: 65 }}
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
                gl={{ antialias: true }}
            >
                <AetherraAvatar />
                <OrbitControls
                    enableZoom={false}
                    autoRotate
                    autoRotateSpeed={0.28}
                    enablePan={false}
                    target={[0, 0.5, 0]}
                    maxPolarAngle={Math.PI * 0.62}
                    minPolarAngle={Math.PI * 0.38}
                />
            </Canvas>
            <BootReadinessPanel readinessState={readinessState} />
            <MetricsOverlay />
            <NeuralChat ws={ws} />
            <MemoryGraphPanel ws={ws} />
            <QuantumPanel ws={ws} />
            <div className="absolute top-4 left-4 text-2xl font-bold text-[#00ff88] font-mono">
                AETHERRA OS
            </div>
            <div className="absolute top-4 right-4 text-sm font-mono">
                <div className={`px-2 py-1 rounded ${wsStatus === "Connected" ? "bg-green-900 text-green-300" :
                    wsStatus === "Connecting..." ? "bg-yellow-900 text-yellow-300" :
                        "bg-red-900 text-red-300"
                    }`}>
                    WS: {wsStatus}
                </div>
            </div>
        </div>
    );
}
