import Hero from '../components/Hero'
import PluginCarousel from '../components/PluginCarousel'
import RoadmapTimeline from '../components/RoadmapTimeline'
import TelemetryStrip from '../components/TelemetryStrip'
import useHubPlugins from '../hooks/useHubPlugins'

export default function Home() {
  const { plugins, loading } = useHubPlugins('/api/plugins', 12000)
  return (
    <div>
      <Hero />
      <TelemetryStrip />
      <div className="mx-auto max-w-7xl px-4">
        <div className="mt-2 rounded-xl border border-white/10 bg-surface/60 p-3 text-sm">
          <div className="flex items-center justify-between">
            <div className="text-neutral-300">Hub status</div>
            <div className="text-neutral-500">{new Date().toLocaleTimeString()}</div>
          </div>
          <div className="mt-1 text-neutral-400">Registered plugins: <span className="text-aether">{loading ? '—' : (plugins?.length ?? 0)}</span></div>
          {!!plugins?.length && (
            <div className="mt-1 text-neutral-400">Latest: {plugins.slice(-3).map(p => p.name || p.id || 'plugin').join(', ')}</div>
          )}
        </div>
      </div>
      <PluginCarousel />
      <RoadmapTimeline />
    </div>
  )
}
