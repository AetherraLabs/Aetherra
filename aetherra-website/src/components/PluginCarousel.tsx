import { motion } from 'framer-motion'

type Card = {
  name: string
  desc: string
  risk: 'low' | 'med' | 'high'
  confidence: number
  io: string[]
}

const cards: Card[] = [
  { name: 'Workflow Builder', desc: 'Compose multi‑agent flows with semantic chaining.', risk: 'low', confidence: 96, io: ['plan','task[]','result'] },
  { name: 'Assistant Trainer', desc: 'Iterative fine‑tuning & eval loops.', risk: 'med', confidence: 93, io: ['dataset','prompt','model'] },
  { name: 'Plugin Generator', desc: 'Scaffold, validate, version & publish.', risk: 'low', confidence: 97, io: ['spec','code','bundle'] },
  { name: 'Memory Cleanser', desc: 'Curates, decays, and rewrites memory traces.', risk: 'med', confidence: 92, io: ['trace[]','policy','summary'] },
]

export default function PluginCarousel() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-6 flex items-end justify-between">
        <h2 className="text-2xl md:text-3xl font-bold">Featured Plugins</h2>
        <div className="text-sm text-neutral-400">Confidence · Risk · I/O</div>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((c, i) => (
          <motion.div
            key={c.name}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
            className="rounded-2xl border border-white/10 bg-surface/60 p-4 hover:shadow-glow"
          >
            <div className="flex items-center justify-between">
              <div className="font-mono text-aether">{c.name}</div>
              <div className="text-xs text-neutral-400">{c.risk.toUpperCase()}</div>
            </div>
            <p className="mt-2 text-sm text-neutral-300">{c.desc}</p>
            <div className="mt-3 text-xs text-neutral-400">I/O: {c.io.join(' · ')}</div>
            <div className="mt-4">
              <div className="h-2 w-full rounded bg-white/10">
                <div className="h-2 rounded bg-aether" style={{ width: `${c.confidence}%` }} />
              </div>
              <div className="mt-1 text-xs">{c.confidence}% confidence</div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
