import React from 'react';

const NS_COLORS = { a: '#038141', b: '#85BB2F', c: '#FECB02', d: '#EE8100', e: '#E63E11' };
const NS_LABELS = { a: 'Excellent', b: 'Bon', c: 'Correct', d: 'Médiocre', e: 'Mauvais' };

export default function ProductCard({ product, index, onClick }) {
  const g = product.nutriscore_grade || 'unknown';
  const q = product.quality_score || 0;
  const qc = q >= 70 ? 'high' : q >= 40 ? 'mid' : 'low';
  const hasImg = product.has_image && product.image_url;
  const nsColor = NS_COLORS[g] || '#a8a29e';
  const nsLabel = NS_LABELS[g] || 'Non noté';
  const nsPoints = g === 'unknown' ? 0 : { a: 40, b: 32, c: 24, d: 16, e: 8 }[g] || 0;

  // Completeness estimate
  const fields = [
    product.product_name,
    product.brand_name,
    product.categories?.length > 0,
    product.nutriscore_grade,
    product.nutrient_count > 0
  ];
  const completeness = Math.round((fields.filter(Boolean).length / fields.length) * 100);

  // Rarity based on quality
  const rarity = q >= 90 ? 'legendary' : q >= 70 ? 'epic' : q >= 50 ? 'rare' : q >= 30 ? 'common' : 'basic';

  return (
    <div
      className={`card-collect card-${rarity}`}
      style={{ animationDelay: `${index * 30}ms`, '--ns-glow': nsColor }}
      onClick={() => onClick(product.id)}
    >
      {/* Top ribbon */}
      <div className="card-ribbon" style={{ background: nsColor }}>
        <span className="card-ribbon-grade">{g === 'unknown' ? 'N/A' : g.toUpperCase()}</span>
        <span className="card-ribbon-label">{nsLabel}</span>
      </div>

      {/* Image area */}
      <div className="card-visual">
        {hasImg ? (
          <img src={product.image_url} alt="" className="card-img" loading="lazy"
            onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
        ) : null}
        <div className="card-img-fallback" style={{ display: hasImg ? 'none' : 'flex' }}>
          🍽️
        </div>
        {/* Quality badge overlay */}
        <div className={`card-score-badge ${qc}`}>
          <span className="card-score-num">{q}</span>
          <span className="card-score-label">/ 100</span>
        </div>
        {/* Rarity indicator */}
        <div className={`card-rarity-gem ${rarity}`} title={`${rarity.charAt(0).toUpperCase() + rarity.slice(1)}`}>
          {rarity === 'legendary' ? '💎' : rarity === 'epic' ? '⭐' : rarity === 'rare' ? '🔷' : '●'}
        </div>
      </div>

      {/* Info block */}
      <div className="card-body">
        <h3 className="card-title">{product.product_name || 'Produit sans nom'}</h3>
        <p className="card-brand">{product.brand_name ? `par ${product.brand_name}` : 'Marque inconnue'}</p>

        {/* Stats row */}
        <div className="card-stats">
          <div className="card-stat" title="Score Nutriscore">
            <span className="card-stat-icon" style={{ color: nsColor }}>🏷️</span>
            <div className="card-stat-data">
              <span className="card-stat-val">{nsPoints}</span>
              <span className="card-stat-max">/40</span>
            </div>
          </div>
          <div className="card-stat" title="Nutriments renseignés">
            <span className="card-stat-icon">🧪</span>
            <div className="card-stat-data">
              <span className="card-stat-val">{product.nutrient_count || 0}</span>
              <span className="card-stat-max">/7</span>
            </div>
          </div>
          <div className="card-stat" title="Allergènes détectés">
            <span className="card-stat-icon">{(product.allergen_count || 0) > 0 ? '⚠️' : '✅'}</span>
            <div className="card-stat-data">
              <span className="card-stat-val">{product.allergen_count || 0}</span>
            </div>
          </div>
          <div className="card-stat" title="Complétude des données">
            <span className="card-stat-icon">📋</span>
            <div className="card-stat-data">
              <span className="card-stat-val">{completeness}%</span>
            </div>
          </div>
        </div>

        {/* Quality bar */}
        <div className="card-quality-row">
          <span className="card-quality-label">Qualité globale</span>
          <div className="card-quality-track">
            <div className={`card-quality-fill ${qc}`} style={{ width: `${q}%` }} />
          </div>
        </div>

        {/* Tags */}
        <div className="card-tags">
          {(product.categories || []).slice(0, 2).map(c => (
            <span key={c} className="card-tag cat">{c}</span>
          ))}
          {(product.allergens || []).slice(0, 2).map(a => (
            <span key={a} className="card-tag danger">{a}</span>
          ))}
        </div>

        {/* Barcode */}
        {product.barcode && (
          <div className="card-barcode">
            <span className="card-barcode-icon">║║│║║│║</span>
            <span className="card-barcode-text">{product.barcode}</span>
          </div>
        )}
      </div>
    </div>
  );
}