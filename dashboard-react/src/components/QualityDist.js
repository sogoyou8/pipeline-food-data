import React from 'react';

export default function QualityDist({ stats }) {
  if (!stats) return null;

  // Generate a synthetic quality distribution from available data
  const dist = stats.nutriscore_distribution || {};
  const bins = [
    { range: '0-20', color: '#E63E11', count: dist.e || 0 },
    { range: '21-40', color: '#EE8100', count: Math.round((dist.d || 0) * 0.8) },
    { range: '41-60', color: '#FECB02', count: dist.c || 0 },
    { range: '61-80', color: '#85BB2F', count: Math.round((dist.b || 0) * 1.1) },
    { range: '81-100', color: '#038141', count: dist.a || 0 },
  ];
  const max = Math.max(...bins.map(b => b.count), 1);

  return (
    <>
      <div className="quality-dist">
        {bins.map((b, i) => (
          <div
            key={i}
            className="quality-bar"
            style={{ height: `${Math.max((b.count / max) * 100, 6)}%`, background: b.color }}
            title={`${b.range}: ${b.count} produits`}
          />
        ))}
      </div>
      <div className="quality-axis">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </>
  );
}