import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { fetchProduct } from '../api/client';

const NS_COLORS = { a: '#038141', b: '#85BB2F', c: '#FECB02', d: '#EE8100', e: '#E63E11' };
const NS_LABELS = { a: 'Excellent', b: 'Bon', c: 'Correct', d: 'Médiocre', e: 'Mauvais' };

const NUTRIENT_INFO = {
  energy_kcal: { label: 'Énergie', emoji: '🔥', ref: 2000, unit: 'kcal' },
  fat: { label: 'Matières grasses', emoji: '🧈', ref: 70, unit: 'g' },
  saturated_fat: { label: 'Acides gras saturés', emoji: '⚡', ref: 20, unit: 'g' },
  sugars: { label: 'Sucres', emoji: '🍬', ref: 50, unit: 'g' },
  salt: { label: 'Sel', emoji: '🧂', ref: 6, unit: 'g' },
  proteins: { label: 'Protéines', emoji: '💪', ref: 50, unit: 'g' },
  fiber: { label: 'Fibres', emoji: '🌾', ref: 25, unit: 'g' },
};

export default function ProductModal({ productId, onClose }) {
  const [p, setP] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    fetchProduct(productId).then(setP).catch(console.error).finally(() => setLoading(false));
  }, [productId]);

  useEffect(() => {
    const h = e => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', h);
    document.body.style.overflow = 'hidden';
    return () => { document.removeEventListener('keydown', h); document.body.style.overflow = ''; };
  }, [onClose]);

  if (!productId) return null;

  const g = p?.nutriscore_grade || 'unknown';
  const q = p?.quality_score || 0;
  const qc = q >= 70 ? 'high' : q >= 40 ? 'mid' : 'low';
  const nsColor = NS_COLORS[g] || '#a8a29e';
  const hasImg = p?.has_image && p?.image_url;
  const nsPoints = g === 'unknown' ? 0 : { a: 40, b: 32, c: 24, d: 16, e: 8 }[g] || 0;
  const compPoints = Math.min(30, Math.max(0, Math.round((q - nsPoints) * 0.5)));
  const nutPoints = Math.max(0, q - nsPoints - compPoints);

  return (
    <>
      <div className="pm-overlay" onClick={onClose} />
      <div className="pm-panel">
        {/* Header */}
        <div className="pm-header">
          <span className="pm-header-title">Fiche produit</span>
          <button className="pm-close" onClick={onClose}><X size={16} /></button>
        </div>

        <div className="pm-scroll">
          {loading ? (
            <div className="loading"><div className="spinner" /><p>Chargement...</p></div>
          ) : !p ? (
            <div className="no-data">Produit introuvable</div>
          ) : (
            <>
              {/* ═══ HERO ═══ */}
              <div className="pm-hero" style={{ '--pm-accent': nsColor }}>
                <div className="pm-hero-glow" />
                <div className="pm-hero-top">
                  <div className="pm-hero-img-wrap">
                    {hasImg ? (
                      <img src={p.image_url} alt={p.product_name} className="pm-hero-img"
                        onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
                    ) : null}
                    <div className="pm-hero-img-fb" style={{ display: hasImg ? 'none' : 'flex' }}>🍽️</div>
                  </div>
                  <div className="pm-hero-info">
                    <h2 className="pm-hero-name">{p.product_name || 'Sans nom'}</h2>
                    <p className="pm-hero-brand">{p.brand_name ? `par ${p.brand_name}` : 'Marque inconnue'}</p>
                    <div className="pm-hero-pills">
                      <span className="pm-pill-ns" style={{ background: nsColor, color: ['b','c'].includes(g) ? '#1c1917' : '#fff' }}>
                        {g === 'unknown' ? 'N/A' : g.toUpperCase()}
                      </span>
                      <span className={`pm-pill-q pm-q-${qc}`}>{q}<small>/100</small></span>
                    </div>
                    {p.barcode && <span className="pm-barcode">{p.barcode}</span>}
                  </div>
                </div>
              </div>

              {/* ═══ NUTRISCORE SCALE ═══ */}
              <div className="pm-block">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">🏷️</span>
                  <h3>Nutriscore</h3>
                </div>
                <div className="pm-ns-scale">
                  {['a','b','c','d','e'].map(grade => (
                    <div key={grade} className={`pm-ns-chip ${grade === g ? 'on' : ''}`}
                      style={grade === g ? { background: NS_COLORS[grade], color: ['b','c'].includes(grade) ? '#1c1917' : '#fff', borderColor: 'transparent', transform: 'scale(1.15)', boxShadow: `0 4px 12px ${NS_COLORS[grade]}40` } : {}}>
                      <span className="pm-ns-letter">{grade.toUpperCase()}</span>
                      <span className="pm-ns-word">{NS_LABELS[grade]}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ═══ SCORE DÉCOMPOSITION ═══ */}
              <div className="pm-block pm-block-accent">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">📊</span>
                  <h3>Score qualité</h3>
                </div>

                {/* Big score */}
                <div className="pm-big-score">
                  <div className="pm-big-ring-wrap">
                    <svg className="pm-big-ring" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="var(--border)" strokeWidth="6" />
                      <circle cx="50" cy="50" r="42" fill="none" stroke={nsColor} strokeWidth="6"
                        strokeDasharray={`${(q / 100) * 263.9} ${263.9 - (q / 100) * 263.9}`}
                        strokeDashoffset="66" strokeLinecap="round"
                        style={{ transition: 'stroke-dasharray 1s cubic-bezier(0.16,1,0.3,1)' }} />
                    </svg>
                    <div className="pm-big-ring-inner">
                      <span className="pm-big-num">{q}</span>
                    </div>
                  </div>
                  <div className="pm-big-text">
                    <strong>{q >= 70 ? 'Bonne qualité' : q >= 40 ? 'Qualité moyenne' : 'Qualité faible'}</strong>
                    <p>Combine Nutriscore, complétude des données et équilibre nutritionnel.</p>
                  </div>
                </div>

                {/* Bars */}
                <div className="pm-bars">
                  <Bar label="Nutriscore" val={nsPoints} max={40} color={nsColor} />
                  <Bar label="Complétude" val={compPoints} max={30} color="#3b82f6" approx />
                  <Bar label="Nutrition" val={nutPoints} max={30} color="#f59e0b" approx />
                </div>
              </div>

              {/* ═══ NUTRIMENTS ═══ */}
              <div className="pm-block">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">🧪</span>
                  <h3>Nutriments</h3>
                  <span className="pm-block-sub">pour 100g</span>
                </div>
                {p.nutrients?.length ? (
                  <>
                    <div className="pm-nut-grid">
                      {p.nutrients.map(n => {
                        const meta = NUTRIENT_INFO[n.name] || { label: n.name, emoji: '•', ref: 100, unit: n.unit };
                        const pct = Math.min(100, Math.round((n.value / meta.ref) * 100));
                        const lvl = pct > 75 ? 'high' : pct > 40 ? 'mid' : 'low';
                        return (
                          <div key={n.name} className="pm-nut-card">
                            <div className="pm-nut-top">
                              <span className="pm-nut-emoji">{meta.emoji}</span>
                              <span className="pm-nut-label">{meta.label}</span>
                            </div>
                            <div className="pm-nut-val">
                              <span className="pm-nut-num">{n.value}</span>
                              <span className="pm-nut-unit">{n.unit}</span>
                            </div>
                            <div className="pm-nut-track">
                              <div className={`pm-nut-fill pm-nut-${lvl}`} style={{ width: `${pct}%` }} />
                            </div>
                            <span className="pm-nut-pct">{pct}% AJR</span>
                          </div>
                        );
                      })}
                    </div>
                    <p className="pm-foot">* Apports Journaliers Recommandés pour un adulte (2000 kcal/jour)</p>
                  </>
                ) : <p className="no-data">Aucun nutriment renseigné</p>}
              </div>

              {/* ═══ CATÉGORIES ═══ */}
              <div className="pm-block">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">🗂️</span>
                  <h3>Catégories</h3>
                  <span className="pm-badge">{p.categories?.length || 0}</span>
                </div>
                <div className="pm-tags">
                  {p.categories?.length ? p.categories.map(c => (
                    <span key={c} className="pm-tag pm-tag-blue">{c}</span>
                  )) : <p className="no-data">Aucune catégorie</p>}
                </div>
              </div>

              {/* ═══ ALLERGÈNES ═══ */}
              <div className="pm-block">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">⚠️</span>
                  <h3>Allergènes</h3>
                  <span className={`pm-badge ${p.allergens?.length ? 'pm-badge-red' : 'pm-badge-green'}`}>
                    {p.allergens?.length || 0}
                  </span>
                </div>
                {p.allergens?.length ? (
                  <>
                    <div className="pm-alert-red">
                      ⚠️ Contient {p.allergens.length} allergène{p.allergens.length > 1 ? 's' : ''} détecté{p.allergens.length > 1 ? 's' : ''}.
                    </div>
                    <div className="pm-tags">
                      {p.allergens.map(a => (
                        <span key={a} className="pm-tag pm-tag-red">⚠️ {a}</span>
                      ))}
                    </div>
                  </>
                ) : <div className="pm-alert-green">✅ Aucun allergène détecté dans les ingrédients.</div>}
              </div>

              {/* ═══ FICHE TECHNIQUE ═══ */}
              <div className="pm-block pm-block-muted">
                <div className="pm-block-head">
                  <span className="pm-block-emoji">📋</span>
                  <h3>Fiche technique</h3>
                </div>
                <div className="pm-specs">
                  <Spec label="Nom" val={p.product_name || '—'} />
                  <Spec label="Marque" val={p.brand_name || '—'} />
                  <Spec label="Code-barres" val={p.barcode || '—'} mono />
                  <Spec label="Nutriscore" val={g === 'unknown' ? 'Non renseigné' : g.toUpperCase()} dot={nsColor} />
                  <Spec label="Score qualité" val={`${q} / 100`} />
                  <Spec label="Complétude" val={`${p.completeness || 0}%`} />
                  <Spec label="Nutriments" val={`${p.nutrient_count || 0} / 7`} />
                  <Spec label="Allergènes" val={`${p.allergen_count || 0}`} />
                  <Spec label="Image" val={p.has_image ? '✅ Disponible' : '❌ Absente'} />
                  <Spec label="Ajouté le" val={new Date(p.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })} />
                </div>
              </div>

              {/* ═══ SOURCE ═══ */}
              <div className="pm-source">
                Données issues de <strong>OpenFoodFacts</strong> — enrichies par notre pipeline (normalisation, détection allergènes, score qualité).
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

/* ── Sub-components ── */
function Bar({ label, val, max, color, approx }) {
  const pct = max > 0 ? Math.min(100, (val / max) * 100) : 0;
  return (
    <div className="pm-bar-row">
      <span className="pm-bar-label">{label}</span>
      <div className="pm-bar-track">
        <div className="pm-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="pm-bar-val">{approx ? '~' : ''}{val}/{max}</span>
    </div>
  );
}

function Spec({ label, val, mono, dot }) {
  return (
    <div className="pm-spec">
      <span className="pm-spec-k">{label}</span>
      <span className={`pm-spec-v ${mono ? 'mono' : ''}`}>
        {dot && <span className="pm-spec-dot" style={{ background: dot }} />}
        {val}
      </span>
    </div>
  );
}