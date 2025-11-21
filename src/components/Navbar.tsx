import { Link, useLocation } from 'react-router-dom'
import './Navbar.css'

const Navbar = () => {
  const location = useLocation()

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>Cardiovascular Dashboard</h1>
        </div>
        <div className="navbar-links">
          <Link 
            to="/" 
            className={location.pathname === '/' ? 'active' : ''}
          >
            Analytics
          </Link>
          <Link 
            to="/predict" 
            className={location.pathname === '/predict' ? 'active' : ''}
          >
            Predict
          </Link>
          <Link 
            to="/about" 
            className={location.pathname === '/about' ? 'active' : ''}
          >
            About
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

