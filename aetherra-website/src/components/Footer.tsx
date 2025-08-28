export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-bg/80">
      <div className="mx-auto max-w-7xl px-4 py-10 grid gap-6 md:grid-cols-3 text-sm text-neutral-300">
        <div>
          <div className="font-mono font-bold text-white">Aetherra Labs</div>
          <p className="mt-2">An AI‑native operating system and research lab exploring memory, cognition, and autonomous evolution.</p>
        </div>
        <div>
          <div className="text-white font-medium">Resources</div>
          <ul className="mt-2 space-y-2">
            <li><a href="/docs" className="hover:text-aether">Docs</a></li>
            <li><a href="/roadmap" className="hover:text-aether">Roadmap</a></li>
            <li><a href="/plugins" className="hover:text-aether">Plugins</a></li>
          </ul>
        </div>
        <div>
          <div className="text-white font-medium">Community</div>
          <ul className="mt-2 space-y-2">
            <li><a href="https://github.com/AetherraLabs" className="hover:text-aether">GitHub</a></li>
            <li><a href="https://x.com/AetherraProject" className="hover:text-aether">X / Twitter</a></li>
            <li><a href="/community" className="hover:text-aether">Discord</a></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-white/5 py-4 text-center text-xs text-neutral-400">© {new Date().getFullYear()} Aetherra Labs</div>
    </footer>
  )
}
