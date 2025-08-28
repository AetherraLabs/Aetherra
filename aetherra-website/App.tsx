import { Route, Routes } from 'react-router-dom'
import Footer from './src/components/Footer'
import NavBar from './src/components/NavBar'
import Community from './src/pages/Community'
import Docs from './src/pages/Docs'
import Home from './src/pages/Home'
import Labs from './src/pages/Labs'
import Lyrixa from './src/pages/Lyrixa'
import Manifesto from './src/pages/Manifesto'
import OSPage from './src/pages/OS'
import Plugins from './src/pages/Plugins'
import Roadmap from './src/pages/Roadmap'
import WhyAetherra from './src/pages/WhyAetherra'

export default function App() {
  return (
    <div className="body-grid bg-bg text-white">
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/os" element={<OSPage />} />
          <Route path="/lyrixa" element={<Lyrixa />} />
          <Route path="/labs" element={<Labs />} />
          <Route path="/plugins" element={<Plugins />} />
          <Route path="/docs/*" element={<Docs />} />
          <Route path="/why" element={<WhyAetherra />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/community" element={<Community />} />
          <Route path="/manifesto" element={<Manifesto />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
