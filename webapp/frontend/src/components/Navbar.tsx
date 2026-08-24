import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { BookOpen, FileScan, PenTool, Lightbulb, Map, Activity, Sun, Moon } from 'lucide-react';
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

const resolveEffectiveTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme !== 'system') return theme;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const Navbar: React.FC = () => {
  const [theme, setTheme] = useState<Theme>(getStoredTheme);

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem('scdo_theme', theme);
  }, [theme]);

  // Listen for system preference changes when in 'system' mode
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      if (theme === 'system') {
        // Force re-render to update icon
        setTheme('system');
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  const toggleTheme = (): void => {
    const effective = resolveEffectiveTheme(theme);
    const next: Theme = effective === 'dark' ? 'light' : 'dark';
    setTheme(next);
  };

  const isDark = resolveEffectiveTheme(theme) === 'dark';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <BookOpen className="logo-icon" />
          <span className="logo-text">SCDO</span>
        </Link>
        <div className="navbar-links">
          <NavLink to="/analyze" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <FileScan size={18} /> Analyze
          </NavLink>
          <NavLink to="/generate" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <PenTool size={18} /> Generate
          </NavLink>
          <NavLink to="/optimize" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Lightbulb size={18} /> Optimize
          </NavLink>
          <NavLink to="/map-outcomes" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Map size={18} /> Map CO-PO
          </NavLink>
          <NavLink to="/specs" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Activity size={18} /> Specs
          </NavLink>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
