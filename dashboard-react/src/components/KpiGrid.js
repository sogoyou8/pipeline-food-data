import React from 'react';
import { Package, Tag, Folder, Star } from 'lucide-react';
import AnimatedCounter from './AnimatedCounter';

const kpis = [
  { key: 'total_products', label: 'Produits analysés', icon: Package, color: 'green' },
  { key: 'total_brands', label: 'Marques distinctes', icon: Tag, color: 'blue' },
  { key: 'total_categories', label: 'Catégories', icon: Folder, color: 'orange' },
  { key: 'avg_quality_score', label: 'Score qualité moyen', icon: Star, color: 'pink', suffix: '/100', decimal: true },
];

export default function KpiGrid({ stats }) {
  if (!stats) return null;

  return (
    <div className="kpi-grid">
      {kpis.map((kpi, i) => {
        const Icon = kpi.icon;
        const val = stats[kpi.key];
        return (
          <div className="kpi-card" key={kpi.key} style={{ animationDelay: `${i * 100}ms` }}>
            <div className={`kpi-icon ${kpi.color}`}>
              <Icon size={24} />
            </div>
            <div className="kpi-body">
              <span className="kpi-value">
                {kpi.decimal ? val?.toFixed(1) : <AnimatedCounter target={val} />}
              </span>
              <span className="kpi-label">{kpi.label}</span>
              {kpi.suffix && <span className="kpi-sub">{kpi.suffix}</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}