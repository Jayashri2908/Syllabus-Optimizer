import React, { useState, useEffect, useCallback } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { FileScan, PenTool, Lightbulb, Map, Activity, Sun, Moon, Monitor, Menu, X } from 'lucide-react';
import './Navbar.css';

type Theme = 'light' | 'dark' | 'system';

const getStoredTheme = (): Theme => {
  return (localStorage.getItem('scdo_theme') as Theme) || 'system';
};

const applyTheme = (theme: Theme): void => {
  const root = document.documentElement;
  if (theme === 'system') {
    root.removeAttribute('data-theme');
  } else {
    root.setAttribute('data-theme', theme);
  }
};

const themeIcon = (theme: Theme) => {
  switch (theme) {
    case 'light': return <Sun size={18} />;
    case 'dark': return <Moon size={18} />;
    case 'system': return <Monitor size={18} />;
  }
};

const themeLabel = (theme: Theme) => {
  switch (theme) {
    case 'light': return 'Light';
    case 'dark': return 'Dark';
    case 'system': return 'System';
  }
};

const Navbar: React.FC = () => {
  const [theme, setTheme] = useState<Theme>(getStoredTheme);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem('scdo_theme', theme);
  }, [theme]);

  // Listen for system preference changes when in 'system' mode
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      if (theme === 'system') {
        setTheme('system');
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  // Close mobile menu on route change (resize)
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cycleTheme = (): void => {
    const next: Theme = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light';
    setTheme(next);
  };

  const closeMobileMenu = useCallback(() => {
    setMenuOpen(false);
  }, []);

  const navLinks = (
    <>
      <NavLink to="/analyze" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"} onClick={closeMobileMenu}>
        <FileScan size={18} /> Analyze
      </NavLink>
      <NavLink to="/generate" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"} onClick={closeMobileMenu}>
        <PenTool size={18} /> Generate
      </NavLink>
      <NavLink to="/optimize" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"} onClick={closeMobileMenu}>
        <Lightbulb size={18} /> Optimize
      </NavLink>
      <NavLink to="/map-outcomes" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"} onClick={closeMobileMenu}>
        <Map size={18} /> Map CO-PO
      </NavLink>
      <NavLink to="/specs" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"} onClick={closeMobileMenu}>
        <Activity size={18} /> Specs
      </NavLink>
      <button
        className="theme-toggle"
        onClick={cycleTheme}
        aria-label={`Theme: ${themeLabel(theme)}. Click to switch.`}
        title={`Current: ${themeLabel(theme)}. Click to switch.`}
      >
        {themeIcon(theme)}
        <span className="theme-label">{themeLabel(theme)}</span>
      </button>
    </>
  );

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMobileMenu}>
          <svg className="logo-icon" width="28" height="28" viewBox="0 0 48 48" fill="none">
            <path d="M10 2h20l12 12v26c0 2.2-1.8 4-4 4H10c-2.2 0-4-1.8-4-4V6c0-2.2 1.8-4 4-4z" fill="currentColor"/>
            <path d="M30 2v8c0 2.2 1.8 4 4 4h8L30 2z" fill="rgba(0,0,0,0.12)"/>
            <line x1="14" y1="19" x2="27" y2="19" stroke="rgba(255,255,255,0.35)" strokeWidth="1.5" strokeLinecap="round"/>
            <line x1="14" y1="25" x2="24" y2="25" stroke="rgba(255,255,255,0.35)" strokeWidth="1.5" strokeLinecap="round"/>
            <path d="M14 36L22 27L31 17" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="14" cy="36" r="2.5" fill="white"/>
            <circle cx="22" cy="27" r="2.5" fill="white"/>
            <circle cx="31" cy="17" r="3" fill="white"/>
          </svg>
          <span className="logo-text">SCDO</span>
        </Link>

        {/* Desktop links */}
        <div className="navbar-links">
          {navLinks}
        </div>

        {/* Mobile hamburger */}
        <button
          className="hamburger-button"
          onClick={() => setMenuOpen(prev => !prev)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile drawer */}
      <div className={`mobile-drawer ${menuOpen ? 'mobile-drawer--open' : ''}`}>
        <div className="mobile-drawer-inner">
          {navLinks}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
