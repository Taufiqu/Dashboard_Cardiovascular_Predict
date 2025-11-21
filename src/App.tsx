import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Analytics from './pages/Analytics'
import Predict from './pages/Predict'
import About from './pages/About'
import Logging from './pages/Logging'

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/" element={<Analytics />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/about" element={<About />} />
          <Route path="/logging" element={<Logging />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

