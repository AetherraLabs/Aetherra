import { Link, useLocation } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home' },
  { to: '/os', label: 'OS' },
  { to: '/why', label: 'Why Aetherra' },
  { to: '/lyrixa', label: 'Lyrixa' },
  { to: '/labs', label: 'Labs' },
  { to: '/plugins', label: 'Plugins' },
  { to: '/docs', label: 'Docs' },
  { to: '/community', label: 'Community' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-bg/70 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
        <Link to="/" className="font-mono font-bold tracking-wider text-aether">AETHERRA LABS</Link>
        <nav className="hidden md:flex items-center gap-6 text-sm">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={"hover:text-aether " + (pathname === l.to ? "text-aether" : "text-neutral-300")}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <Link to="/manifesto" className="px-3 py-1.5 rounded-lg bg-aether text-black font-medium shadow-glow">Manifesto</Link>
      </div>
    </header>
  )
}
