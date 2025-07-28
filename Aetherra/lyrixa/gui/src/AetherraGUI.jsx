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
        <div className="absolute top-2 right-4 text-green-400 font-mono text-sm bg-black/40 backdrop-blur p-2 rounded-xl shadow-md">
            <div>Memory Load: {(memoryLoad * 100).toFixed(1)}%</div>
            <div>Confidence: {(confidence * 100).toFixed(1)}%</div>
            <div>Curiosity: {(curiosity * 100).toFixed(1)}%</div>
        </div>
    );
}

// 3D AURA
function HoloAura() {
    return (
        <mesh>
            <sphereGeometry args={[1.8, 64, 64]} />
            <meshBasicMaterial color="#00ff88" transparent opacity={0.04} />
        </mesh>
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
    useEffect(() => {
        const socket = new WebSocket("ws://localhost:7070/ws");
        socket.onmessage = (msg) => {
            const data = JSON.parse(msg.data);
            useAetherraStore.getState().updateMetrics(data);
        };
    }, []);

    return (
        <div className="w-screen h-screen bg-[#0a0a0a] overflow-hidden relative">
            <Canvas camera={{ position: [0, 0, 5] }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} />
                <HoloAura />
                <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.2} />
            </Canvas>

            <MetricsOverlay />
            <NeuralChat />

            <div className="absolute top-4 left-4 text-2xl font-bold text-[#00ff88] font-mono">
                LYRIXA - Aetherra OS
            </div>
        </div>
    );
}
