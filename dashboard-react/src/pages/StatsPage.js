import React from 'react';
import AnimatedCounter from '../components/AnimatedCounter';
import DonutChart from '../components/DonutChart';
import RankingList from '../components/RankingList';
import QualityDist from '../components/QualityDist';

export default function StatsPage({ stats }) {
  const total = stats?.total_products || 0;
  const brands = stats?.total_brands || 0;
  const cats = stats?.total_categories || 0;
  const avg = stats?.avg_quality_score || 0;
  const dist = stats?.nutriscore_distribution || {};

  // Total des produits AVEC nutriscore seulement
  const grades = ['a', 'b', 'c', 'd', 'e'];
  const graded = grades.reduce((s, g) => s + (dist[g] || 0), 0);
  const ungraded = total - graded;

  // Calculs basés sur les produits NOTÉS uniquement
  const dominant = grades.reduce((best, g) => (dist[g] || 0) > (dist[best] || 0) ? g : best, 'a');
  const dominantPct = graded ? Math.round(((dist[dominant] || 0) / graded) * 100) : 0;

  const good = (dist.a || 0) + (dist.b || 0);
  const goodPct = graded ? Math.round((good / graded) * 100) : 0;

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Vue d'ensemble</h1>
        <p className="page-subtitle">Analyse en temps réel de la base de données alimentaire</p>
        <div className="page-meta">
          <span className="meta-item">OpenFoodFacts</span>
          <span className="meta-dot" />
          <span className="meta-item">{total} produits</span>
          <span className="meta-dot" />
          <span className="meta-item">{graded} notés</span>
          <span className="meta-dot" />
          <span className="meta-item">4 enrichissements</span>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem' }}>
        <div className="bento">
          {/* KPI row */}
          <div className="cell cell-span-3" style={{ animationDelay: '0ms' }}>
            <div className="cell-label">Produits</div>
            <div className="cell-value"><AnimatedCounter target={total} /></div>
            <div className="cell-sub">entrées analysées</div>
          </div>
          <div className="cell cell-span-3" style={{ animationDelay: '60ms' }}>
            <div className="cell-label">Marques</div>
            <div className="cell-value"><AnimatedCounter target={brands} /></div>
            <div className="cell-sub">distinctes</div>
          </div>
          <div className="cell cell-span-3" style={{ animationDelay: '120ms' }}>
            <div className="cell-label">Catégories</div>
            <div className="cell-value"><AnimatedCounter target={cats} /></div>
            <div className="cell-sub">alimentaires</div>
          </div>
          <div className="cell cell-span-3" style={{ animationDelay: '180ms' }}>
            <div className="cell-label">Score moyen</div>
            <div className="cell-value">{avg.toFixed(1)}</div>
            <div className="cell-sub">sur 100</div>
          </div>

          {/* Nutriscore donut + insights */}
          <div className="cell cell-span-7" style={{ animationDelay: '240ms' }}>
            <div className="cell-title">Distribution Nutriscore</div>
            <DonutChart distribution={dist} totalProducts={total} />
            <div className="insight">
              <div className={`insight-icon ${goodPct >= 50 ? 'green' : 'amber'}`}>
                {goodPct >= 50 ? '✅' : '⚠️'}
              </div>
              <div className="insight-text">
                <strong>{goodPct}%</strong> des produits notés ont un Nutriscore A ou B.
                Le grade dominant est <strong>{dominant.toUpperCase()}</strong> ({dominantPct}%).
                {ungraded > 0 && <> <strong>{ungraded}</strong> produit{ungraded > 1 ? 's' : ''} sans nutriscore.</>}
              </div>
            </div>
          </div>

          {/* Quality distribution */}
          <div className="cell cell-span-5" style={{ animationDelay: '300ms' }}>
            <div className="cell-title">Score qualité</div>
            <QualityDist stats={stats} />
            <div className="insight" style={{ marginTop: '0.75rem' }}>
              <div className={`insight-icon ${avg >= 60 ? 'green' : avg >= 40 ? 'amber' : 'red'}`}>
                {avg >= 60 ? '📊' : avg >= 40 ? '📉' : '🔻'}
              </div>
              <div className="insight-text">
                Score moyen de <strong>{avg.toFixed(1)}/100</strong>.
                {avg >= 60 ? ' Satisfaisant.' : ' Marge d\'amélioration.'}
                <br />
                <em style={{ fontSize: '0.7rem' }}>Le score combine Nutriscore (40pts) + complétude des données (30pts) + nutrition (30pts).</em>
              </div>
            </div>
          </div>

          {/* Rankings */}
          <div className="cell cell-span-6" style={{ animationDelay: '360ms' }}>
            <div className="cell-title">Top marques</div>
            <RankingList items={stats?.top_brands} color="green" />
          </div>
          <div className="cell cell-span-6" style={{ animationDelay: '420ms' }}>
            <div className="cell-title">Top catégories</div>
            <RankingList items={stats?.top_categories} color="blue" />
          </div>
        </div>
      </div>
    </>
  );
}