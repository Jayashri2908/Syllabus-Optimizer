import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Menu, X, BookOpen, BarChart2, FileText, Zap } from 'lucide-react';
import Logo3D from './components/Logo3D';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import GeneratePage from './pages/GeneratePage';
import OptimizePage from './pages/OptimizePage';
import './index.css';

// NavLink Helper Component
const NavLink = ({ to, icon: Icon, label, onClick }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`nav-link ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <Icon size={18} />
      <span>{label}</span>
    </Link>
  );
};

function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu when route changes
  const closeMobileMenu = () => setMobileMenuOpen(false);

  return (
    <Router>
      <div className="app">
        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#ffffff',
              color: '#0f172a',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontFamily: 'Inter, sans-serif',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            },
            success: {
              iconTheme: {
                primary: '#15803d',
                secondary: 'white',
              },
            },
            error: {
              iconTheme: {
                primary: '#b91c1c',
                secondary: 'white',
              },
            },
          }}
        />

        {/* Navigation */}
        <nav className="navbar">
          <div className="navbar-content px-6">
            <Link to="/" className="navbar-brand" onClick={closeMobileMenu}>
              <div className="brand-logo-container">
                <Logo3D />
              </div>
              <div className="flex flex-col">
                <span className="brand-text">Syllabus Optimizer</span>
                <span className="brand-subtitle">Enterprise Edition</span>
              </div>
            </Link>

            {/* Desktop Nav */}
            <div className="navbar-links hidden-mobile">
              <NavLink to="/" icon={BookOpen} label="Home" />
              <NavLink to="/analyze" icon={BarChart2} label="Analyze" />
              <NavLink to="/generate" icon={FileText} label="Generate" />
              <NavLink to="/optimize" icon={Zap} label="Optimize" />
            </div>

            <div className="navbar-actions">
              <button
                className="mobile-menu-toggle"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>

          {/* Mobile Nav */}
          <div className={`mobile-nav ${mobileMenuOpen ? 'open' : ''}`}>
            <div className="mobile-nav-content">
              <NavLink to="/" icon={BookOpen} label="Home" onClick={closeMobileMenu} />
              <NavLink to="/analyze" icon={BarChart2} label="Analyze" onClick={closeMobileMenu} />
              <NavLink to="/generate" icon={FileText} label="Generate" onClick={closeMobileMenu} />
              <NavLink to="/optimize" icon={Zap} label="Optimize" onClick={closeMobileMenu} />
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/optimize" element={<OptimizePage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="footer">
          <div className="container">
            <div className="flex flex-col items-center justify-center gap-2">
              <p className="footer-text">
                © 2025 SCDO Inc. All rights reserved.
              </p>
              <p className="text-xs text-subtle">
                Enterprise Grade Syllabus Management System
              </p>
            </div>
          </div>
        </footer>
      </div>

      <style>{`
        .navbar {
          background: white;
          border-bottom: 1px solid var(--border);
          position: sticky;
          top: 0;
          z-index: 100;
          height: 70px;
          display: flex;
          align-items: center;
          box-shadow: var(--shadow-sm);
        }

        .navbar-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
        }

        .navbar-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          text-decoration: none;
        }
        
        .brand-logo-container {
            background: linear-gradient(135deg, var(--primary), #334155);
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-sm);
        }
        
        .text-white { color: white; }

        .brand-text {
          font-weight: 700;
          font-size: 1.125rem;
          color: var(--text-primary);
          line-height: 1.1;
        }
        
        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .navbar-links {
          display: flex;
          gap: 4px;
          background: var(--bg-surface);
          padding: 4px;
          border-radius: 10px;
        }

        .nav-link {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: var(--text-secondary);
          font-weight: 500;
          font-size: 0.9rem;
          padding: 8px 16px;
          border-radius: 6px;
          transition: all 0.2s ease;
        }

        .nav-link:hover {
          color: var(--text-primary);
          background: rgba(0,0,0,0.03);
        }
        
        .nav-link.active {
            background: white;
            color: var(--brand);
            box-shadow: var(--shadow-sm);
            font-weight: 600;
        }

        .mobile-menu-toggle {
          display: none;
          background: transparent;
          border: none;
          color: var(--text-primary);
          cursor: pointer;
        }
        
        .mobile-nav {
            position: fixed;
            top: 70px;
            left: 0;
            width: 100%;
            background: white;
            border-bottom: 1px solid var(--border);
            padding: 1rem;
            transform: translateY(-150%);
            transition: transform 0.3s ease;
            z-index: 99;
        }
        
        .mobile-nav.open {
            transform: translateY(0);
        }
        
        .mobile-nav-content {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .footer {
          background: white;
          border-top: 1px solid var(--border);
          padding: 2rem 0;
          margin-top: auto;
        }

        .footer-text {
          color: var(--text-secondary);
          font-size: 0.875rem;
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .hidden-mobile {
            display: none;
          }

          .mobile-menu-toggle {
            display: block;
          }
        }
      `}</style>
    </Router >
  );
}

export default App;
