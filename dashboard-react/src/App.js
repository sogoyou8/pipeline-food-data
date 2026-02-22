import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import StatsPage from './pages/StatsPage';
import ProductsPage from './pages/ProductsPage';
import Footer from './components/Footer';
import { checkHealth } from './api/client';
import { useStats } from './hooks/useStats';

export default function App() {
  const [tab, setTab] = useState('stats');
  const [apiUp, setApiUp] = useState(null);
  const { stats } = useStats();
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light');

  useEffect(() => {
    checkHealth().then(() => setApiUp(true)).catch(() => setApiUp(false));
  }, []);

  useEffect(() => {
    const h = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setTab('products');
        setTimeout(() => document.getElementById('search-input')?.focus(), 80);
      }
    };
    document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, []);

  return (
    <>
      <Navbar tab={tab} setTab={setTab} apiUp={apiUp} theme={theme} toggleTheme={toggleTheme} />
      <main className="content">
        {tab === 'stats' && <StatsPage stats={stats} />}
        {tab === 'products' && <ProductsPage />}
      </main>
      <Footer />
    </>
  );
}
