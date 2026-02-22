import React from 'react';

const GRADES = ['a', 'b', 'c', 'd', 'e'];
const COLORS = { a: '#038141', b: '#85BB2F', c: '#FECB02', d: '#EE8100', e: '#E63E11' };
const LABELS = { a: 'Excellent', b: 'Bon', c: 'Correct', d: 'Médiocre', e: 'Mauvais' };

export default function DonutChart({ distribution, totalProducts }) {
  if (!distribution) return null;

  // Total des produits AVEC un nutriscore (exclut les non renseignés)
  const graded = GRADES.reduce((s, g) => s + (distribution[g] || 0), 0);
  const ungraded = (totalProducts || graded) - graded;
  const max = Math.max(...GRADES.map(g => distribution[g] || 0), 1);

  const R = 52, stroke = 14, cx = 65, cy = 65;
  const C = 2 * Math.PI * R;
  let offset = 0;

  const arcs = GRADES.map(g => {
    const count = distribution[g] || 0;
    const pct = graded > 0 ? count / graded : 0;
    const len = pct * C;
    const gap = 2;
    const arc = { grade: g, offset, len: Math.max(len - gap, 0), color: COLORS[g] };
    offset += len;
    return arc;
  });

  return (
    <div className="donut-container">
      <svg className="donut-svg" viewBox="0 0 130 130">
        {arcs.map(a => (
          <circle
            key={a.grade}
            cx={cx} cy={cy} r={R}
            fill="none" stroke={a.color}
            strokeWidth={stroke}
            strokeDasharray={`${a.len} ${C - a.len}`}
            strokeDashoffset={-a.offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 0.8s cubic-bezier(0.16,1,0.3,1)' }}
          />
        ))}
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize="18" fontWeight="800" fill="currentColor">{graded}</text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize="8" fontWeight="500" fill="currentColor" opacity="0.5">notés</text>
      </svg>

      <div className="donut-legend">
        {GRADES.map(g => {
          const count = distribution[g] || 0;
          // Pourcentage calculé sur les produits NOTÉS uniquement
          const pct = graded > 0 ? ((count / graded) * 100).toFixed(0) : '0';
          const w = Math.max((count / max) * 100, 3);
          return (
            <div className="donut-row" key={g}>
              <div className="donut-row-left">
                <span className="donut-swatch" style={{ background: COLORS[g] }} />
                <span className="donut-grade">{LABELS[g]}</span>
              </div>
              <div className="donut-bar-bg">
                <div className="donut-bar-fill" style={{ width: `${w}%`, background: COLORS[g] }} />
              </div>
              <span className="donut-count">{count}</span>
              <span className="donut-pct">{pct}%</span>
            </div>
          );
        })}
        {ungraded > 0 && (
          <div className="donut-ungraded">
            <span>Non renseigné</span>
            <span>{ungraded} produit{ungraded > 1 ? 's' : ''}</span>
          </div>
        )}
      </div>
    </div>
  );
}