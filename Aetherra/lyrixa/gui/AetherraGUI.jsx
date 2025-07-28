// Aetherra Holographic UI Shell
// Technologies: React + Tailwind + Three.js + Zustand + WebSocket

import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { create } from "zustand";

// STATE MANAGEMENT
const useAetherraStore = create((set) => ({
    memoryLoad: 0.45,
    confidence: 0.9,
    curiosity: 0.63,
    updateMetrics: (data) => set(data),
}));

// LIVE METRICS OVERLAY
function MetricsOverlay() {
    const { memoryLoad, confidence, curiosity } = useAetherraStore();
    return (
        <div className="absolute top-16 right-4 text-green-400 font-mono text-sm bg-black/60 backdrop-blur p-3 rounded-xl shadow-lg border border-green-500/30">
            <div className="text-center text-green-300 font-bold mb-2">NEURAL METRICS</div>
            <div className="space-y-1">
                <div>Memory Load: {(memoryLoad * 100).toFixed(1)}%</div>
                <div>Confidence: {(confidence * 100).toFixed(1)}%</div>
                <div>Curiosity: {(curiosity * 100).toFixed(1)}%</div>
            </div>
        </div>
    );
}

// 3D AURA
function HoloAura() {
    return (
        <group>
            {/* Main holographic sphere */}
            <mesh>
                <sphereGeometry args={[1.8, 64, 64]} />
                <meshBasicMaterial
                    color="#00ff88"
                    transparent
                    opacity={0.15}
                    wireframe={false}
                />
            </mesh>

            {/* Wireframe overlay */}
            <mesh>
                <sphereGeometry args={[1.85, 32, 32]} />
                <meshBasicMaterial
                    color="#00ff88"
                    transparent
                    opacity={0.3}
                    wireframe={true}
                />
            </mesh>

            {/* Inner core */}
            <mesh>
                <sphereGeometry args={[0.3, 16, 16]} />
                <meshBasicMaterial
                    color="#ffffff"
                    transparent
                    opacity={0.8}
                />
            </mesh>
        </group>
    );
}

// CHAT PANEL
function NeuralChat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = () => {
        if (!input.trim()) return;
        setMessages([...messages, { from: "user", text: input }]);
        setInput("");
        // TODO: Send to backend and handle reply
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

// MAIN APP
export default function AetherraGUI() {
    const [wsStatus, setWsStatus] = useState("Connecting...");

    useEffect(() => {
        try {
            const socket = new WebSocket("ws://localhost:7070/ws");

            socket.onopen = () => {
                setWsStatus("Connected");
                console.log("WebSocket connected to Lyrixa");
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

            return () => {
                socket.close();
            };
        } catch (error) {
            setWsStatus("Failed");
            console.error("Failed to create WebSocket:", error);
        }
    }, []);

    return (
        <div className="w-screen h-screen bg-[#0a0a0a] overflow-hidden relative">
            {/* 3D Canvas */}
            <Canvas
                camera={{ position: [0, 0, 5], fov: 75 }}
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
            >
                <ambientLight intensity={0.6} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <directionalLight position={[-5, 5, 5]} intensity={0.5} />
                <HoloAura />
                <OrbitControls
                    enableZoom={false}
                    autoRotate
                    autoRotateSpeed={0.5}
                    enablePan={false}
                />
            </Canvas>

            {/* UI Overlays */}
            <MetricsOverlay />
            <NeuralChat />

            {/* Title */}
            <div className="absolute top-4 left-4 text-2xl font-bold text-[#00ff88] font-mono">
                LYRIXA - Aetherra OS
            </div>

            {/* WebSocket Status */}
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
