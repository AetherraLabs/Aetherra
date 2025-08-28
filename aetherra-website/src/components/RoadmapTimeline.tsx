type Milestone = { title: string; status: 'done' | 'next' | 'planned'; note?: string }
const milestones: Milestone[] = [
  { title: 'Stage 1–5: UI + Theme + Animations', status: 'done' },
  { title: 'Stage 6: Live Introspection', status: 'done' },
  { title: 'Stage 7: .aether Playground', status: 'done' },
  { title: 'Stage 8: Professional Console', status: 'done' },
  { title: 'Stage 9: Community Hub', status: 'done' },
  { title: 'Stage 10: Live Terminal', status: 'done' },
  { title: 'Stage 11: Docs & Assistant', status: 'done' },
  { title: 'Stage 12: Deployment', status: 'done' },
  { title: 'Phase: Unified Cognitive Stack', status: 'done' },
  { title: 'Next: Mobile/Voice Interfaces', status: 'next' },
  { title: 'Planned: Quantum Hardware Bridge', status: 'planned' }
]

export default function RoadmapTimeline() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10">
      <h2 className="text-2xl md:text-3xl font-bold">Roadmap</h2>
      <div className="mt-6 overflow-x-auto">
        <ol className="flex gap-6">
          {milestones.map((m, i) => (
            <li key={i} className="min-w-[240px] rounded-2xl border border-white/10 bg-surface/60 p-4">
              <div className="text-sm">{m.title}</div>
              <div className="mt-2 text-xs">
                <span className={
                  m.status === 'done' ? 'text-aether' :
                  m.status === 'next' ? 'text-white' : 'text-neutral-400'
                }>
                  {m.status.toUpperCase()}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
