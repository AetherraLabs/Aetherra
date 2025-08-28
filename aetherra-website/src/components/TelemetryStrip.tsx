import { useEffect, useState } from 'react'
import { generateMetrics, Metric } from '../utils/metrics'

export default function TelemetryStrip() {
    const [metrics, setMetrics] = useState<Metric[]>(generateMetrics())
    useEffect(() => {
        const id = setInterval(() => setMetrics(generateMetrics()), 2000)
        return () => clearInterval(id)
    }, [])
    return (
        <div className="mx-auto max-w-7xl px-4 py-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {metrics.map((m) => (
                <div key={m.label} className="rounded-xl border border-white/10 bg-surface/60 p-4">
                    <div className="text-xs uppercase tracking-wider text-neutral-400">{m.label}</div>
                    <div className="mt-1 text-2xl font-semibold">{m.value}</div>
                    <div className="mt-1 text-xs text-neutral-400">{m.trend === 'up' ? '↑ improving' : m.trend === 'down' ? '↓ fluctuating' : '→ stable'}</div>
                </div>
            ))}
        </div>
    )
}
