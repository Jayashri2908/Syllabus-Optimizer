import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import GeneratePage from './pages/GeneratePage';
import OptimizePage from './pages/OptimizePage';
import './index.css';

function App() {
    const [theme, setTheme] = useState('light');

    // Load theme from localStorage
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
        document.documentElement.setAttribute('data-theme', savedTheme);
    }, []);

    // Toggle theme
    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    return (
        <Router>
            <div className="app">
                {/* Navigation */}
                <nav className="navbar">
                    <div className="container">
                        <div className="navbar-content">
                            <Link to="/" className="navbar-brand">
                                <span className="brand-icon">📚</span>
                                <span className="brand-text">SCDO</span>
                            </Link>

                            <div className="navbar-links">
                                <Link to="/" className="nav-link">Home</Link>
                                <Link to="/analyze" className="nav-link">Analyze</Link>
                                <Link to="/generate" className="nav-link">Generate</Link>
                                <Link to="/optimize" className="nav-link">Optimize</Link>
                            </div>

                            <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle theme">
                                {theme === 'light' ? '🌙' : '☀️'}
                            </button>
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
                        <p className="footer-text">
                            © 2025 SCDO - Powered by IBM Granite AI (Free Tier)
                        </p>
                    </div>
                </footer>
            </div>

            <style>{`
        .navbar {
          background: var(--bg-primary);
          border-bottom: 1px solid var(--border);
          padding: var(--spacing-md) 0;
          position: sticky;
          top: 0;
          z-index: 100;
          backdrop-filter: blur(10px);
          background: rgba(255, 255, 255, 0.9);
        }

        [data-theme="dark"] .navbar {
          background: rgba(20, 20, 30, 0.9);
        }

        .navbar-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .navbar-brand {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          text-decoration: none;
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .brand-icon {
          font-size: 2rem;
        }

        .brand-text {
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .navbar-links {
          display: flex;
          gap: var(--spacing-lg);
        }

        .nav-link {
          text-decoration: none;
          color: var(--text-secondary);
          font-weight: 600;
          transition: color var(--transition-fast);
          position: relative;
        }

        .nav-link:hover {
          color: var(--primary);
        }

        .nav-link::after {
          content: '';
          position: absolute;
          bottom: -4px;
          left: 0;
          width: 0;
          height: 2px;
          background: var(--primary);
          transition: width var(--transition-fast);
        }

        .nav-link:hover::after {
          width: 100%;
        }

        .theme-toggle {
          background: var(--bg-tertiary);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          padding: var(--spacing-sm);
          font-size: 1.25rem;
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .theme-toggle:hover {
          transform: scale(1.1);
          box-shadow: var(--shadow-md);
        }

        .main-content {
          min-height: calc(100vh - 200px);
          padding: var(--spacing-2xl) 0;
        }

        .footer {
          background: var(--bg-secondary);
          border-top: 1px solid var(--border);
          padding: var(--spacing-lg) 0;
          text-align: center;
        }

        .footer-text {
          color: var(--text-secondary);
          font-size: 0.875rem;
          margin: 0;
        }

        @media (max-width: 768px) {
          .navbar-links {
            display: none;
          }
        }
      `}</style>
        </Router>
    );
}

export default App;
