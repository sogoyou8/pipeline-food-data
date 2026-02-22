import React, { useState, useEffect } from 'react';
import { BarChart3, Search, Sun, Moon } from 'lucide-react';

export default function Navbar({ tab, setTab, apiUp, theme, toggleTheme }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  const statusClass = apiUp === true ? 'online' : apiUp === false ? 'offline' : '';
  const statusText = apiUp === true ? 'API connectée' : apiUp === false ? 'API hors ligne' : 'Connexion...';

  return (
    <nav className="nav">
      <div className="nav-inner">
        <div className="nav-left">
          <a href="#top" className="nav-brand" onClick={e => e.preventDefault()}>
            <div className="nav-logo">FD</div>
            <span className="nav-name">Food Data</span>
          </a>
          <div className="nav-tabs">
            <button className={`nav-tab ${tab === 'stats' ? 'active' : ''}`} onClick={() => setTab('stats')}>
              <BarChart3 size={14} /> Vue d'ensemble
            </button>
            <button className={`nav-tab ${tab === 'products' ? 'active' : ''}`} onClick={() => setTab('products')}>
              <Search size={14} /> Explorer
            </button>
          </div>
        </div>
        <div className="nav-right">
          <button className="theme-toggle" onClick={toggleTheme} title={theme === 'light' ? 'Mode sombre' : 'Mode clair'}>
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>
          <div className={`api-pill ${statusClass}`}>
            <span className="api-dot" />
            {statusText}
          </div>
        </div>
      </div>
    </nav>
  );
}