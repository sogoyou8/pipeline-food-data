import React from 'react';

const GRADES = ['a', 'b', 'c', 'd', 'e'];
const LABELS = { a: 'Excellent', b: 'Bon', c: 'Moyen', d: 'Médiocre', e: 'Mauvais' };
const COLORS = { a: '#038141', b: '#85BB2F', c: '#FECB02', d: '#EE8100', e: '#E63E11' };

export default function NutriscoreChart({ distribution }) {
  if (!distribution) return null;

  const total = GRADES.reduce((s, g) => s + (distribution[g] || 0), 0) || 1;
  const max = Math.max(...GRADES.map(g => distribution[g] || 0), 1);

  return (
    <div className="chart-card chart-card-wide">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">Distribution Nutriscore</h3>
          <p className="chart-desc">Répartition des produits par grade nutritionnel officiel</p>
        </div>
      </div>

      <div className="ns-bars">
        {GRADES.map(g => {
          const count = distribution[g] || 0;
          const pct = ((count / total) * 100).toFixed(1);
          const height = Math.max((count / max) * 100, 3);
          return (
            <div className="ns-bar-wrapper" key={g}>
              <span className="ns-count">{count}</span>
              <div className={`ns-bar ${g}`} style={{ height: `${height}%` }} />
              <span className={`ns-label ${g}`}>{g.toUpperCase()}</span>
              <span className="ns-pct">{pct}%</span>
            </div>
          );
        })}
      </div>

      <div className="ns-legend">
        {GRADES.map(g => (
          <span className="ns-legend-item" key={g}>
            <span className="ns-legend-dot" style={{ background: COLORS[g] }} />
            {LABELS[g]}
          </span>
        ))}
      </div>
    </div>
  );
}