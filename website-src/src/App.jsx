import { motion } from 'framer-motion'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'

// Import your actual components
import Home from './pages/Home'
import LyrixaDemo from './src2/pages/LyrixaDemo'
import AetherScriptPlayground from './src5/pages/AetherScriptPlayground'
import LiveIntrospection from './src6/pages/LiveIntrospection'

// Import backup simple pages for sections not yet built
import Navbar from './components/Navbar'
import About from './pages/About'
import Community from './pages/Community'
import Features from './pages/Features'

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-black text-white">
                <Navbar />
                <motion.main
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/lyrixa" element={<LyrixaDemo />} />
                        <Route path="/playground" element={<AetherScriptPlayground />} />
                        <Route path="/introspection" element={<LiveIntrospection />} />
                        <Route path="/about" element={<About />} />
                        <Route path="/features" element={<Features />} />
                        <Route path="/community" element={<Community />} />
                        <Route path="*" element={<Home />} />
                    </Routes>
                </motion.main>
            </div>
        </Router>
    )
}

export default App
