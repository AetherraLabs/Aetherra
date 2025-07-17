import { motion } from 'framer-motion'
import { Link, Route, Routes } from 'react-router-dom'
import AetherHub from './pages/AetherHub'
import AetherScriptConsole from './pages/AetherScriptConsole'
import AetherScriptPlayground from './pages/AetherScriptPlayground'
import AetherScriptPlaygroundV7 from './pages/AetherScriptPlaygroundV7'
import CommunityHub from './pages/CommunityHub'
import Contribute from './pages/Contribute'
import Home from './pages/Home'
import LiveIntrospection from './pages/LiveIntrospection'
import LyrixaDemo from './pages/LyrixaDemo'
import LyrixaSandbox from './pages/LyrixaSandbox'
import LyrixaTechnical from './pages/LyrixaTechnical'
import Manifesto from './pages/Manifesto'
import PluginGuidelines from './pages/PluginGuidelines'
import Roadmap from './pages/Roadmap'
import Terms from './pages/Terms'

function App() {
  return (
    <div className="App min-h-screen bg-aetherra-dark">
      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 bg-aetherra-dark/80 backdrop-blur-custom border-b border-aetherra-green/20"
      >
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold gradient-text">
            Aetherra
          </Link>
          <div className="flex space-x-6">
            <Link
              to="/"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Home
            </Link>
            <Link
              to="/manifesto"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Manifesto
            </Link>
            <Link
              to="/roadmap"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Roadmap
            </Link>
            <Link
              to="/demo"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Live Demo
            </Link>
            <Link
              to="/sandbox"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Sandbox
            </Link>
            <Link
              to="/technical"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Technical
            </Link>
            <Link
              to="/hub"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              AetherHub
            </Link>
            <Link
              to="/contribute"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Contribute
            </Link>
            <Link
              to="/community"
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Community
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="pt-20">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/manifesto" element={<Manifesto />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/plugin-guidelines" element={<PluginGuidelines />} />
          <Route path="/demo" element={<LyrixaDemo />} />
          <Route path="/sandbox" element={<LyrixaSandbox />} />
          <Route path="/technical" element={<LyrixaTechnical />} />
          <Route path="/hub" element={<AetherHub />} />
          <Route path="/contribute" element={<Contribute />} />
          <Route path="/community" element={<CommunityHub />} />
          <Route path="/playground" element={<AetherScriptPlayground />} />
          <Route path="/playground-v7" element={<AetherScriptPlaygroundV7 />} />
          <Route path="/introspection" element={<LiveIntrospection />} />
          <Route path="/console" element={<AetherScriptConsole />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
