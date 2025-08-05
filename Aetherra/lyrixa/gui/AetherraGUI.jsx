// Aetherra Holographic UI Shell
// Technologies: React + Tailwind + Three.js + Zustand + WebSocket

import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import create from "zustand";

// STATE MANAGEMENT
const useAetherraStore = create((set) => ({
    memoryLoad: 0.45,
    confidence: 0.9,
    curiosity: 0.63,
    updateMetrics: (data) => set(data),
    addMessage: (msg) => set((state) => ({ messages: [...(state.messages || []), msg] })),
    messages: [],
}));

// LIVE METRICS OVERLAY
function MetricsOverlay() {
    const { memoryLoad, confidence, curiosity } = useAetherraStore();
    return (
        <div className="absolute top-2 right-4 text-green-400 font-mono text-sm bg-black/40 backdrop-blur p-2 rounded-xl shadow-md">
            <div>Memory Load: {(memoryLoad * 100).toFixed(1)}%</div>
            <div>Confidence: {(confidence * 100).toFixed(1)}%</div>
            <div>Curiosity: {(curiosity * 100).toFixed(1)}%</div>
        </div>
    );
}

// 3D AURA with advanced animated shader and glow
function HoloAura() {
    const meshRef = useRef();
    useFrame(({ clock }) => {
        if (meshRef.current) {
            meshRef.current.material.opacity = 0.09 + 0.05 * Math.sin(clock.getElapsedTime() * 2);
            meshRef.current.material.emissiveIntensity = 0.7 + 0.3 * Math.sin(clock.getElapsedTime() * 1.5);
            meshRef.current.rotation.y += 0.003;
        }
    });
    return (
        <mesh ref={meshRef}>
            <sphereGeometry args={[2.1, 96, 96]} />
            <meshStandardMaterial color="#00ff88" transparent opacity={0.13} emissive="#00ff88" emissiveIntensity={0.8} />
            {/* Glow effect using another sphere */}
            <mesh>
                <sphereGeometry args={[2.25, 96, 96]} />
                <meshBasicMaterial color="#00ff88" transparent opacity={0.07} />
            </mesh>
        </mesh>
    );
}

// CHAT PANEL (wired to backend)
function NeuralChat() {
    const [input, setInput] = useState("");
    const messages = useAetherraStore((s) => s.messages || []);
    const addMessage = useAetherraStore((s) => s.addMessage);
    const wsRef = useRef();

    // Attach to global WebSocket
    useEffect(() => {
        wsRef.current = window.aetherraSocket;
        if (!wsRef.current) return;
        const handler = (msg) => {
            try {
                const data = JSON.parse(msg.data);
                if (data.type === "chat") {
                    addMessage({ from: "lyrixa", text: data.text });
                }
            } catch { }
        };
        wsRef.current.addEventListener("message", handler);
        return () => wsRef.current?.removeEventListener("message", handler);
    }, [addMessage]);

    const sendMessage = () => {
        if (!input.trim()) return;
        addMessage({ from: "user", text: input });
        if (wsRef.current && wsRef.current.readyState === 1) {
            wsRef.current.send(JSON.stringify({ type: "chat", text: input }));
        }
        setInput("");
    };

    return (
        <motion.div
            className="absolute left-6 bottom-6 w-[32rem] h-[28rem] bg-[#1a1a1a]/80 text-green-300 rounded-2xl p-4 overflow-y-auto font-mono shadow-xl backdrop-blur"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
        >
            <div className="text-lg font-bold mb-2">Lyrixa Neural Chat</div>
            <div className="h-[20rem] overflow-y-auto space-y-2">
                {messages.map((m, i) => (
                    <div key={i} className={`text-${m.from === "user" ? "white" : "green-300"}`}>{m.text}</div>
                ))}
            </div>
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask Lyrixa anything..."
                className="w-full mt-3 bg-black/40 p-2 rounded-lg text-green-200 border border-green-500 outline-none"
            />
        </motion.div>
    );
}

// GLASSMORPHIC MEMORY GRAPH PANEL (enhanced)
function MemoryGraphPanel() {
    return (
        <motion.div
            className="absolute right-12 bottom-12 w-[30rem] h-[20rem] bg-white/10 backdrop-blur-2xl border border-cyan-300/20 rounded-3xl shadow-2xl flex flex-col items-center justify-center"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
        >
            <div className="text-xl font-bold text-cyan-200 mb-2 tracking-wider drop-shadow">Fractal Memory Graph</div>
            <div className="w-full h-full flex items-center justify-center">
                {/* Animated fractal/halo effect */}
                <div className="w-48 h-48 rounded-full bg-gradient-to-tr from-green-400/30 to-cyan-400/10 blur-3xl animate-pulse shadow-2xl border border-cyan-400/20" />
            </div>
        </motion.div>
    );
}

// MAIN APP
export default function AetherraGUI() {
    // Robust WebSocket connection with reconnect and error handling
    useEffect(() => {
        let socket;
        let reconnectTimeout;
        function connect() {
            socket = new window.WebSocket("ws://localhost:8080/ws");
            window.aetherraSocket = socket;
            socket.onopen = () => {
                // Optionally send handshake
            };
            socket.onmessage = (msg) => {
                try {
                    const data = JSON.parse(msg.data);
                    if (data.type === "metrics") {
                        useAetherraStore.getState().updateMetrics(data);
                    } else if (data.type === "chat") {
                        useAetherraStore.getState().addMessage({ from: "lyrixa", text: data.text });
                    }
                } catch { }
            };
            socket.onerror = (e) => {
                // Optionally show error UI
            };
            socket.onclose = () => {
                reconnectTimeout = setTimeout(connect, 2000);
            };
        }
        connect();
        return () => {
            if (socket) socket.close();
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
        };
    }, []);

    return (
        <div className="w-screen h-screen bg-gradient-to-br from-[#0a0a0a] via-[#0e1a16] to-[#0a0a0a] overflow-hidden relative">
            {/* 3D Canvas with animated aura */}
            <Canvas camera={{ position: [0, 0, 5] }} className="absolute inset-0 z-0">
                <ambientLight intensity={0.6} />
                <pointLight position={[10, 10, 10]} intensity={1.2} />
                <HoloAura />
                <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.18} />
            </Canvas>

            {/* Overlays and panels */}
            <MetricsOverlay />
            <NeuralChat />
            <MemoryGraphPanel />

            {/* Title with glassmorphism and glow */}
            <div className="absolute top-6 left-8 text-3xl font-extrabold text-[#00ff88] font-mono drop-shadow-lg bg-black/30 px-6 py-2 rounded-2xl border border-green-400/20 backdrop-blur-lg shadow-xl">
                LYRIXA <span className="text-cyan-300">- Aetherra OS</span>
            </div>

            {/* Subtle animated background glow */}
            <div className="pointer-events-none absolute inset-0 z-0">
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[60vw] h-[60vw] rounded-full bg-cyan-400/5 blur-3xl animate-pulse" />
            </div>
        </div>
    );
}
