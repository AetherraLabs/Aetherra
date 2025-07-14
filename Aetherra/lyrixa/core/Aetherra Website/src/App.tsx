import { Routes, Route, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Home from './pages/Home'
import LyrixaDemo from './pages/LyrixaDemo'
import LyrixaSandbox from './pages/LyrixaSandbox'
import LyrixaTechnical from './pages/LyrixaTechnical'
import AetherHub from './pages/AetherHub'
import Contribute from './pages/Contribute'
import AetherScriptPlayground from './pages/AetherScriptPlayground'
import AetherScriptPlaygroundV7 from './pages/AetherScriptPlaygroundV7'
import LiveIntrospection from './pages/LiveIntrospection'
import AetherScriptConsole from './pages/AetherScriptConsole'
import CommunityHub from './pages/CommunityHub'

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
              Community Hub
            </Link>
            <Link 
              to="/playground" 
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Playground
            </Link>
            <Link 
              to="/playground-v7" 
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Playground V7
            </Link>
            <Link 
              to="/introspection" 
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Introspection
            </Link>
            <Link 
              to="/console" 
              className="text-zinc-300 hover:text-aetherra-green transition-colors"
            >
              Console
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="pt-20">
        <Routes>
          <Route path="/" element={<Home />} />
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
