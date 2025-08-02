// Aetherra Holographic UI Shell
// Technologies: React + Tailwind + Three.js + Zustand + WebSocket

import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { create } from "zustand";

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
        <motion.div
            className="absolute top-4 right-4 text-aetherra-cyan font-mono text-sm bg-black/80 backdrop-blur-sm p-4 rounded-xl shadow-2xl border border-aetherra-green/30 z-50"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
        >
            <div className="text-aetherra-green text-lg mb-2">◉ NEURAL METRICS</div>
            <div className="space-y-1">
                <div>Memory Load: <span className="text-aetherra-green">{(memoryLoad * 100).toFixed(1)}%</span></div>
                <div>Confidence: <span className="text-aetherra-cyan">{(confidence * 100).toFixed(1)}%</span></div>
                <div>Curiosity: <span className="text-purple-400">{(curiosity * 100).toFixed(1)}%</span></div>
            </div>
        </motion.div>
    );
}// 3D AURA with advanced animated shader and glow
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

    // Connect to Socket.IO events
    useEffect(() => {
        const socket = window.aetherraSocket;
        if (!socket) return;

        const handleChatMessage = (data) => {
            addMessage({ from: "lyrixa", text: data.text });
        };

        socket.on("chat_message", handleChatMessage);

        return () => {
            socket.off("chat_message", handleChatMessage);
        };
    }, [addMessage]);

    const sendMessage = () => {
        if (!input.trim()) return;
        addMessage({ from: "user", text: input });

        // Send via Socket.IO
        const socket = window.aetherraSocket;
        if (socket && socket.connected) {
            socket.emit("chat", { text: input });
        }
        setInput("");
    };

    return (
        <motion.div
            className="absolute left-6 bottom-6 w-[32rem] h-[28rem] bg-black/90 backdrop-blur-sm text-aetherra-cyan rounded-2xl p-4 font-mono shadow-2xl border border-aetherra-green/30 z-50"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
        >
            <div className="text-xl font-bold mb-2 text-aetherra-green">◉ NEURAL INTERFACE</div>
            <div className="h-[20rem] overflow-y-auto space-y-2 bg-black/20 p-2 rounded border border-aetherra-green/20">
                {messages.map((m, i) => (
                    <div key={i} className={`text-${m.from === "user" ? "aetherra-cyan" : "white"}`}>
                        <span className="text-aetherra-green">▶</span> {m.text}
                    </div>
                ))}
                {messages.length === 0 && (
                    <div className="text-gray-400 text-center py-8">
                        Neural interface ready...
                    </div>
                )}
            </div>
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Enter neural command..."
                className="w-full mt-3 bg-black/50 text-aetherra-cyan p-3 rounded-lg border border-aetherra-green/30 outline-none focus:border-aetherra-green focus:shadow-lg focus:shadow-aetherra-green/20 placeholder-gray-500"
            />
        </motion.div>
    );
}

// GLASSMORPHIC MEMORY GRAPH PANEL (enhanced)
function MemoryGraphPanel() {
    const { memoryLoad } = useAetherraStore();

    return (
        <motion.div
            className="absolute right-6 bottom-6 w-[25rem] h-[15rem] bg-black/80 backdrop-blur-sm border border-aetherra-green/30 rounded-3xl shadow-2xl flex flex-col p-4 z-50"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
        >
            <div className="text-lg font-bold text-aetherra-green mb-3">◉ MEMORY CORE</div>
            <div className="flex-1 flex items-center justify-center">
                <div className="relative">
                    <div className="w-24 h-24 rounded-full border-2 border-aetherra-green/30 flex items-center justify-center">
                        <div
                            className="w-20 h-20 rounded-full bg-gradient-to-r from-aetherra-green to-aetherra-cyan flex items-center justify-center text-black font-bold"
                            style={{
                                background: `conic-gradient(from 0deg, #00ff88 0%, #00ff88 ${memoryLoad * 360}deg, transparent ${memoryLoad * 360}deg)`
                            }}
                        >
                            <div className="w-16 h-16 rounded-full bg-black flex items-center justify-center">
                                <span className="text-aetherra-cyan text-sm">{(memoryLoad * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>
                    <div className="absolute -inset-1 bg-aetherra-green/20 rounded-full blur animate-pulse"></div>
                </div>
            </div>
        </motion.div>
    );
}// MAIN APP
export default function AetherraGUI() {
    // Robust Socket.IO connection with reconnect and error handling
    useEffect(() => {
        let socket;
        let reconnectTimeout;
        let connectionAttempts = 0;
        const maxAttempts = 5;

        function connect() {
            if (connectionAttempts >= maxAttempts) {
                console.log("❌ Max connection attempts reached. Stopping reconnection.");
                return;
            }

            connectionAttempts++;
            console.log(`🔄 Socket.IO connection attempt ${connectionAttempts}/${maxAttempts}`);

            socket = io("http://localhost:8686", {
                transports: ["polling", "websocket"],
                timeout: 10000,
                autoConnect: true,
                reconnection: false, // We handle reconnection manually
                forceNew: true // Force a new connection each time
            });
            window.aetherraSocket = socket;

            socket.on("connect", () => {
                console.log("🔗 Connected to Aetherra API server");
                connectionAttempts = 0; // Reset on successful connection
            });

            socket.on("disconnect", (reason) => {
                console.log("🔌 Disconnected from Aetherra API server:", reason);
                if (reason === "io server disconnect") {
                    // Server initiated disconnect, don't reconnect
                    return;
                }
                reconnectTimeout = setTimeout(connect, 3000);
            });

            socket.on("metrics", (data) => {
                console.log("📊 Received metrics:", data);
                useAetherraStore.getState().updateMetrics(data);
            });

            socket.on("chat_message", (data) => {
                console.log("💬 Received chat message:", data);
                useAetherraStore.getState().addMessage({ from: "lyrixa", text: data.text });
            });

            socket.on("connect_error", (error) => {
                console.log("❌ Socket.IO connection error:", error.message || error);
                reconnectTimeout = setTimeout(connect, 2000);
            });

            socket.on("error", (error) => {
                console.log("❌ Socket.IO error:", error);
            });
        }

        // Wait a bit for the server to be ready before connecting
        const initialDelay = setTimeout(connect, 1000);

        return () => {
            if (socket) socket.disconnect();
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
            if (initialDelay) clearTimeout(initialDelay);
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
            <div className="relative z-10">
                <MetricsOverlay />
                <NeuralChat />
                <MemoryGraphPanel />

                {/* Title with glassmorphism and glow */}
                <motion.div
                    className="absolute top-4 left-4 text-4xl font-extrabold text-aetherra-green font-mono bg-black/80 backdrop-blur-sm px-8 py-4 rounded-2xl border border-aetherra-green/30 shadow-2xl shadow-aetherra-green/20 z-50"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 1, delay: 0.2 }}
                >
                    AETHERRA <span className="text-aetherra-cyan">LYRIXA</span>
                </motion.div>
            </div>

            {/* Subtle animated background glow */}
            <div className="pointer-events-none absolute inset-0 z-0">
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[60vw] h-[60vw] rounded-full bg-aetherra-green/5 blur-3xl animate-pulse" />
            </div>
        </div>
    );
}
