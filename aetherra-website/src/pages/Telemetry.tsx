import { useEffect, useRef, useState } from "react";
import PromSparkline from "../components/PromSparkline";
import TelemetryStrip from "../components/TelemetryStrip";
import usePrometheus from "../hooks/usePrometheus";
import useSSE from "../hooks/useSSE";

export default function Telemetry() {
    const { data: prom, error: promErr, loading: promLoading } = usePrometheus("/metrics", 7000);
    const { connected, lastEvent, error: sseErr } = useSSE("/api/ai/stream");
    // Build a tiny timeseries for one metric we care about, e.g., aetherra_requests_total
    const [hist, setHist] = useState<number[]>([]);
    const lastSampleRef = useRef<number | null>(null);
    useEffect(() => {
        if (!prom) return;
        const target = prom.find(s => s.name.includes("aetherra") || s.name.includes("request") || s.name.includes("cpu"));
        if (target) {
            lastSampleRef.current = target.value;
            setHist((h) => {
                const next = [...h, target.value];
                return next.slice(-40);
            });
        }
    }, [prom]);
    return (
        <div className="max-w-4xl mx-auto px-6 py-16">
            <div className="text-center mb-12">
                <h1 className="text-display font-display text-aetherra-text-primary mb-4">
                    System Telemetry
                </h1>
                <p className="text-lg text-aetherra-text-secondary">
                    Real-time system performance and cognitive metrics
                </p>
            </div>

            {/* Compact Telemetry Dashboard */}
            <div className="card-lab p-6">
                <TelemetryStrip />
            </div>

            {/* Additional System Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <div className="card-lab p-6">
                    <h2 className="text-headline font-display text-aetherra-text-primary mb-4">
                        Performance Metrics
                    </h2>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">CPU Usage</span>
                            <span className="text-aetherra-accent">12.4%</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">Memory Usage</span>
                            <span className="text-aetherra-accent">2.1GB / 16GB</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">Network I/O</span>
                            <span className="text-aetherra-accent">156 MB/s</span>
                        </div>
                    </div>
                </div>

                <div className="card-lab p-6">
                    <h2 className="text-headline font-display text-aetherra-text-primary mb-4">
                        Cognitive Status
                    </h2>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">Active Goals</span>
                            <span className="text-aetherra-accent">7</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">Plugin Load</span>
                            <span className="text-aetherra-accent">4 / 12</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-aetherra-text-secondary">Memory Depth</span>
                            <span className="text-aetherra-accent">3.2k entries</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Endpoints and Streaming */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <div className="card-lab p-6">
                    <h2 className="text-headline font-display text-aetherra-text-primary mb-3">
                        Prometheus Metrics
                    </h2>
                    <p className="text-aetherra-text-secondary mb-3">
                        Scrape OS and Hub metrics via the standard Prometheus plaintext endpoint.
                    </p>
                    <div className="rounded-lg bg-black/40 border border-white/10 p-3 text-sm">
                        <div><span className="text-aetherra-text-tertiary">GET</span> <code className="text-aether">/metrics</code></div>
                        <div className="text-caption text-aetherra-text-tertiary mt-2">Hints: rolling histogram fallback; zero-bucket first scrape guarded.</div>
                    </div>
                </div>
                <div className="card-lab p-6">
                    <h2 className="text-headline font-display text-aetherra-text-primary mb-3">
                        AI Streaming (SSE)
                    </h2>
                    <p className="text-aetherra-text-secondary mb-3">Subscribe to AI output tokens and events via SSE.</p>
                    <div className="rounded-lg bg-black/40 border border-white/10 p-3 text-sm space-y-2">
                        <div>Connection: <span className={connected ? 'text-emerald-400' : 'text-rose-400'}>{connected ? 'connected' : 'disconnected'}</span></div>
                        {sseErr && <div className="text-rose-400">{sseErr}</div>}
                        <div className="h-28 overflow-auto rounded border border-white/10 p-2 bg-black/30">
                            <pre className="text-xs whitespace-pre-wrap break-words">{lastEvent?.data || '—'}</pre>
                        </div>
                        <div className="text-caption text-aetherra-text-tertiary">Endpoint: <code className="text-aether">GET /api/ai/stream</code></div>
                    </div>
                </div>
            </div>

            {/* Live Prometheus Snapshot */}
            <div className="card-lab p-6 mt-8">
                <h2 className="text-headline font-display text-aetherra-text-primary mb-3">Prometheus Snapshot</h2>
                {promLoading && <div className="text-aetherra-text-tertiary text-sm">Loading…</div>}
                {promErr && <div className="text-rose-400 text-sm">{promErr}</div>}
                {prom && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        {prom.slice(0, 8).map((s) => (
                            <div key={s.name} className="flex justify-between rounded border border-white/10 bg-black/30 px-3 py-2">
                                <span className="text-aetherra-text-secondary">{s.name}</span>
                                <span className="text-aether">{s.value}</span>
                            </div>
                        ))}
                    </div>
                )}
                <div className="mt-4">
                    <div className="text-caption text-aetherra-text-tertiary mb-1">Selected metric (live)</div>
                    <PromSparkline values={hist} />
                </div>
            </div>
        </div>
    );
}
