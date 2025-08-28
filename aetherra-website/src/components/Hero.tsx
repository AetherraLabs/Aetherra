import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import usePRM from '../hooks/usePrefersReducedMotion'

export default function Hero() {
  const reduced = usePRM()
  // Only show the background video if explicitly enabled via env.
  // This avoids 404s on GitHub Pages where the media isn't published yet.
  const enableVideo = Boolean((import.meta as any)?.env?.VITE_ENABLE_HERO_VIDEO)
  return (
    <section className="relative h-[78vh] min-h-[560px] overflow-hidden">
      {enableVideo ? (
        <video
          className="absolute inset-0 h-full w-full object-cover opacity-40"
          src="/hero-preview.mp4"
          autoPlay
          muted
          loop
          playsInline
          // Optional poster if present in the deployment; not required.
          // poster="/hero-poster.png"
          preload="metadata"
        />
      ) : (
        // Fallback visual when video is disabled or unavailable.
        <div className="absolute inset-0 bg-[radial-gradient(60%_60%_at_50%_40%,rgba(68,255,209,0.20)_0%,rgba(68,255,209,0.05)_35%,transparent_70%)]" />
      )}
      <div className="absolute inset-0 bg-gradient-to-b from-bg/10 via-bg/40 to-bg/80" />
      {/* Nebula accent */}
      <div className="pointer-events-none absolute -top-24 -left-16 h-72 w-72 rounded-full bg-aether/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -right-16 h-72 w-72 rounded-full bg-soft/20 blur-3xl" />
      {/* Parallax layers */}
      {!reduced && (
        <>
          <div className="pointer-events-none absolute top-16 left-12 h-24 w-24 rounded-full bg-aether/25 blur-2xl" style={{ transform: 'translateZ(0)' }} />
          <div className="pointer-events-none absolute bottom-20 right-24 h-28 w-28 rounded-full bg-soft/25 blur-2xl" style={{ transform: 'translateZ(0)' }} />
        </>
      )}
      <div className="relative z-10 mx-auto flex h-full max-w-7xl items-center justify-center px-6 text-center">
        <div>
          <p className="font-mono tracking-widest text-soft">AETHERRA LABS</p>
          <motion.h1
            initial={reduced ? false : { opacity: 0, y: 20 }}
            animate={reduced ? {} : { opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="mt-3 text-5xl md:text-7xl font-bold"
          >
            CODE AWAKENED
          </motion.h1>
          <p className="mx-auto mt-4 max-w-2xl text-neutral-300">
            The AI‑native operating system. Thoughts, goals, and intelligent evolution—built in.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link to="/lyrixa" className="px-5 py-3 rounded-lg bg-aether text-black font-medium shadow-glow">Try Lyrixa</Link>
            <Link to="/manifesto" className="px-5 py-3 rounded-lg border border-white/10 hover:border-aether/40">Read the Manifesto</Link>
          </div>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-sm text-neutral-300">
            <div className="rounded-lg border border-white/10 bg-black/30 px-3 py-1.5">🧠 Memory</div>
            <div className="rounded-lg border border-white/10 bg-black/30 px-3 py-1.5">🎯 Goals</div>
            <div className="rounded-lg border border-white/10 bg-black/30 px-3 py-1.5">🧭 Ethics</div>
            <div className="rounded-lg border border-white/10 bg-black/30 px-3 py-1.5">🔌 Plugins</div>
          </div>
        </div>
      </div>
      <div className="pointer-events-none absolute inset-0 ring-1 ring-white/5" />
    </section>
  )
}
