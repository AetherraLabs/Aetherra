export default function SystemDiagram() {
    return (
        <svg viewBox="0 0 760 300" className="w-full h-auto" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Aetherra System Flow">
            <defs>
                <linearGradient id="g" x1="0" x2="1">
                    <stop offset="0" stopColor="#7c3aed" stopOpacity="0.22" />
                    <stop offset="1" stopColor="#7c3aed" stopOpacity="0.08" />
                </linearGradient>
                <marker id="arrow" markerWidth="12" markerHeight="10" refX="10" refY="5" orient="auto">
                    <polygon points="0 0, 12 5, 0 10" fill="#7c3aed" />
                </marker>
                {/* Label pill background */}
                <filter id="labelGlow" x="-50%" y="-50%" width="200%" height="200%">
                    <feDropShadow dx="0" dy="0" stdDeviation="1.5" floodColor="#7c3aed" floodOpacity="0.35" />
                </filter>
            </defs>

            <rect x="10" y="10" width="740" height="280" rx="14" fill="url(#g)" stroke="#ffffff22" />

            {/* Nodes */}
            <g fill="#00000055" stroke="#ffffff22">
                <rect x="40" y="60" width="160" height="68" rx="10" />
                <rect x="240" y="60" width="180" height="68" rx="10" />
                <rect x="460" y="60" width="180" height="68" rx="10" />

                <rect x="40" y="168" width="180" height="68" rx="10" />
                <rect x="260" y="168" width="160" height="68" rx="10" />
                <rect x="460" y="168" width="180" height="68" rx="10" />
            </g>

            {/* Node labels */}
            <g fill="#c7c7ff" fontFamily="monospace" fontSize="13">
                <text x="60" y="100">Goal Kernel</text>
                <text x="260" y="100">Agent Orchestrator</text>
                <text x="480" y="100">Plugins + Chaining</text>

                <text x="60" y="208">Memory / QFAC</text>
                <text x="280" y="208">Unified Context</text>
                <text x="480" y="208">Safety / Ethics</text>
            </g>

            {/* Flows with clearer labels */}
            <g stroke="#7c3aed" strokeWidth="2.5" fill="none" markerEnd="url(#arrow)">
                {/* plan */}
                <path className="flow" d="M200 94 H240" />
                <g filter="url(#labelGlow)">
                    <rect x="214" y="76" rx="4" ry="4" width="36" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="218" y="88" fill="#bda4ff" fontSize="10">plan</text>
                </g>
                {/* exec */}
                <path className="flow" d="M420 94 H460" />
                <g filter="url(#labelGlow)">
                    <rect x="432" y="76" rx="4" ry="4" width="34" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="436" y="88" fill="#bda4ff" fontSize="10">exec</text>
                </g>
                {/* context */}
                <path className="flow" d="M330 128 V168" />
                <g filter="url(#labelGlow)">
                    <rect x="310" y="144" rx="4" ry="4" width="52" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="314" y="156" fill="#bda4ff" fontSize="10">context</text>
                </g>
                {/* memory */}
                <path className="flow" d="M220 202 H260" />
                <g filter="url(#labelGlow)">
                    <rect x="232" y="184" rx="4" ry="4" width="56" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="236" y="196" fill="#bda4ff" fontSize="10">memory</text>
                </g>
                {/* trace */}
                <path className="flow" d="M420 202 H460" />
                <g filter="url(#labelGlow)">
                    <rect x="432" y="184" rx="4" ry="4" width="44" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="436" y="196" fill="#bda4ff" fontSize="10">trace</text>
                </g>
                {/* guard */}
                <path className="flow" d="M550 128 V168" />
                <g filter="url(#labelGlow)">
                    <rect x="534" y="144" rx="4" ry="4" width="44" height="16" fill="#1a1129" stroke="#7c3aed" strokeOpacity="0.6" />
                    <text x="538" y="156" fill="#bda4ff" fontSize="10">guard</text>
                </g>
            </g>
        </svg>
    );
}
