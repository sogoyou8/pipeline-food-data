import React from 'react';
import AnimatedCounter from './AnimatedCounter';

export default function Hero({ totalProducts }) {
  return (
    <header className="hero">
      <div className="hero-bg">
        <div className="hero-shape hero-shape-1" />
        <div className="hero-shape hero-shape-2" />
        <div className="hero-shape hero-shape-3" />
      </div>
      <div className="hero-content">
        <div className="hero-eyebrow">Pipeline Data Full-Stack</div>
        <h1 className="hero-title">Analyse <span className="hero-highlight">Nutritionnelle</span></h1>
        <p className="hero-subtitle">
          Explorez la qualité de{' '}
          <span className="hero-counter"><AnimatedCounter target={totalProducts} /></span>{' '}
          produits alimentaires collectés depuis OpenFoodFacts
        </p>
        <div className="hero-chips">
          <span className="hero-chip">🔬 4 enrichissements</span>
          <span className="hero-chip">📊 Score qualité 0-100</span>
          <span className="hero-chip">⚠️ Détection allergènes</span>
        </div>
      </div>
    </header>
  );
}