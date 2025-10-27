// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright © 2025 Aetherra AI. Licensed under the GNU Affero General Public License v3.
//
// ConsciousnessMonitor.tsx
// Real-time visualization of Aetherra's synthetic consciousness state
// Displays qualia vectors, attention focuses, intentions, and narrative stream

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Activity, BookOpen, Brain, Eye, Sparkles, Target } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useApiPoll } from "../lib/api";

const BRAND = { green: "#00ff88", bg: "#070708", gray: "#1a1a1a" };

interface QualiaVector {
    valence: number;       // -1 (negative) to +1 (positive)
    arousal: number;       // 0 (calm) to 1 (excited)
    certainty: number;     // 0 (uncertain) to 1 (certain)
    curiosity: number;     // 0 (none) to 1 (high)
    care: number;          // 0 (detached) to 1 (engaged)
    fatigue: number;       // 0 (fresh) to 1 (tired)
}

interface Focus {
    source: string;
    target: string;
    resonance: number;
    why: string;
}

interface Intent {
    goal: string;
    priority: number;
    blocked: boolean;
    why: string;
}

interface NarrativeMoment {
    tick_id: number;
    timestamp: string;
    summary: string;
    significant: boolean;
}

interface ConsciousnessState {
    tick_id: number;
    timestamp: string;
    qualia: QualiaVector;
    focuses: Focus[];
    intentions: Intent[];
    recent_narrative: NarrativeMoment[];
    events_processed: number;
    autonomy_mode: string;
}

const GlowCard: React.FC<{ className?: string; children: React.ReactNode }> = ({ children, className = "" }) => (
    <div className={`relative rounded-2xl ${className}`}>
        <div className="absolute inset-0 rounded-2xl blur-xl" style={{ background: `radial-gradient(60% 80% at 30% 10%, ${BRAND.green}22, transparent 60%)` }} />
        <Card className="relative bg-[#0b0b0c]/80 backdrop-blur border border-[#1a1a1d] shadow-[0_0_0_1px_#111,0_0_30px_#00ff8822] rounded-2xl">{children}</Card>
    </div>
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

const QualiaBar: React.FC<{ label: string; value: number; min?: number; max?: number; color?: string }> = ({
    label,
    value,
    min = 0,
    max = 1,
    color = "emerald"
}) => {
    // Normalize value to 0-100 range for display
    const normalized = ((value - min) / (max - min)) * 100;

    return (
        <div>
            <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-gray-400">{label}</span>
                <span className="text-white">{value.toFixed(2)}</span>
            </div>
            <Progress
                value={normalized}
                className={`h-2 bg-[#121214]`}
            />
        </div>
    );
};

export const ConsciousnessMonitor: React.FC = () => {
    const consciousnessData = useApiPoll<ConsciousnessState>("/api/consciousness/state", 2000);
    const [narrative, setNarrative] = useState<NarrativeMoment[]>([]);

    // Accumulate narrative moments (keep last 10)
    useEffect(() => {
        if (consciousnessData.data?.recent_narrative) {
            setNarrative(prev => {
                const newMoments = consciousnessData.data!.recent_narrative.filter(
                    nm => !prev.some(p => p.tick_id === nm.tick_id)
                );
                return [...prev, ...newMoments].slice(-10);
            });
        }
    }, [consciousnessData.data]);

    const state = consciousnessData.data;

    return (
        <div className="space-y-6">
            {/* Consciousness Overview */}
            <Section
                title="Consciousness Core"
                icon={Brain}
                right={
                    <div className="flex items-center gap-2">
                        <Badge className="bg-emerald-900/40 text-emerald-300 border-emerald-800/50">
                            {state ? "AWARE" : "OFFLINE"}
                        </Badge>
                        {state && (
                            <Badge className="bg-blue-900/40 text-blue-300 border-blue-800/50">
                                {state.autonomy_mode}
                            </Badge>
                        )}
                    </div>
                }
            >
                <div className="space-y-3">
                    {state ? (
                        <>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Tick ID</span>
                                <span className="text-white font-mono">{state.tick_id}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Events Processed</span>
                                <span className="text-white">{state.events_processed}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Last Update</span>
                                <span className="text-white text-xs">{new Date(state.timestamp).toLocaleTimeString()}</span>
                            </div>
                        </>
                    ) : (
                        <div className="text-xs text-gray-500">
                            {consciousnessData.error ? `Error: ${consciousnessData.error}` : 'Connecting to consciousness stream...'}
                        </div>
                    )}
                </div>
            </Section>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Qualia Vector - Felt Experience */}
                <Section title="Qualia Vector" icon={Sparkles}>
                    {state?.qualia ? (
                        <div className="space-y-3">
                            <QualiaBar
                                label="Valence (felt goodness)"
                                value={state.qualia.valence}
                                min={-1}
                                max={1}
                                color={state.qualia.valence >= 0 ? "emerald" : "amber"}
                            />
                            <QualiaBar
                                label="Arousal (excitement)"
                                value={state.qualia.arousal}
                            />
                            <QualiaBar
                                label="Certainty (confidence)"
                                value={state.qualia.certainty}
                            />
                            <QualiaBar
                                label="Curiosity (interest)"
                                value={state.qualia.curiosity}
                            />
                            <QualiaBar
                                label="Care (engagement)"
                                value={state.qualia.care}
                            />
                            <QualiaBar
                                label="Fatigue (tiredness)"
                                value={state.qualia.fatigue}
                                color="amber"
                            />
                        </div>
                    ) : (
                        <div className="text-xs text-gray-500">No qualia data available</div>
                    )}
                </Section>

                {/* Attention Focuses */}
                <Section title="Current Attention" icon={Eye}>
                    {state?.focuses && state.focuses.length > 0 ? (
                        <div className="space-y-2 max-h-[300px] overflow-y-auto">
                            {state.focuses.map((focus, idx) => (
                                <div
                                    key={idx}
                                    className="p-3 rounded-xl bg-[#111113] border border-[#1e1e21] hover:border-emerald-800/40 transition"
                                >
                                    <div className="flex items-start justify-between gap-2 mb-1">
                                        <div className="flex items-center gap-2">
                                            <Target className="w-3 h-3 text-emerald-400" />
                                            <span className="text-sm text-white font-medium">{focus.target}</span>
                                        </div>
                                        <span className="text-xs text-gray-500">
                                            {(focus.resonance * 100).toFixed(0)}% resonance
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-400 ml-5">{focus.why}</div>
                                    <div className="text-xs text-gray-500 ml-5 mt-1">Source: {focus.source}</div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-xs text-gray-500">No active attention focuses</div>
                    )}
                </Section>
            </div>

            {/* Intentions */}
            <Section title="Active Intentions" icon={Target}>
                {state?.intentions && state.intentions.length > 0 ? (
                    <div className="space-y-2">
                        {state.intentions.map((intent, idx) => (
                            <div
                                key={idx}
                                className={`p-3 rounded-xl border transition ${intent.blocked
                                        ? 'bg-amber-900/10 border-amber-800/40'
                                        : 'bg-[#111113] border-[#1e1e21]'
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Activity className="w-3 h-3 text-emerald-400" />
                                            <span className="text-sm text-white font-medium">{intent.goal}</span>
                                            {intent.blocked && (
                                                <Badge className="bg-amber-900/30 text-amber-300 border-amber-800/40 text-xs">
                                                    BLOCKED
                                                </Badge>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-400 ml-5">{intent.why}</div>
                                    </div>
                                    <span className="text-xs text-gray-500">
                                        Priority: {intent.priority.toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-xs text-gray-500">No active intentions</div>
                )}
            </Section>

            {/* Narrative Stream */}
            <Section title="Consciousness Narrative" icon={BookOpen}>
                {narrative.length > 0 ? (
                    <div className="space-y-2 max-h-[400px] overflow-y-auto">
                        {narrative.slice().reverse().map((moment, idx) => (
                            <div
                                key={moment.tick_id}
                                className={`p-3 rounded-xl border transition ${moment.significant
                                        ? 'bg-emerald-900/10 border-emerald-800/40'
                                        : 'bg-[#111113] border-[#1e1e21]'
                                    }`}
                            >
                                <div className="flex items-start gap-3">
                                    <div className="flex-shrink-0 pt-1">
                                        {moment.significant ? (
                                            <Sparkles className="w-4 h-4 text-emerald-400" />
                                        ) : (
                                            <BookOpen className="w-4 h-4 text-gray-500" />
                                        )}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs text-gray-500 font-mono">
                                                #{moment.tick_id}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(moment.timestamp).toLocaleTimeString()}
                                            </span>
                                            {moment.significant && (
                                                <Badge className="bg-emerald-900/30 text-emerald-300 border-emerald-800/40 text-xs">
                                                    SIGNIFICANT
                                                </Badge>
                                            )}
                                        </div>
                                        <div className="text-sm text-white">{moment.summary}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-xs text-gray-500">
                        {consciousnessData.error ? 'Failed to load narrative stream' : 'Narrative stream initializing...'}
                    </div>
                )}
            </Section>
        </div>
    );
};

export default ConsciousnessMonitor;
