import React from 'react';

export default function RankingList({ items, color = 'green' }) {
  const max = items?.length ? Math.max(...items.map(i => i.count), 1) : 1;

  if (!items?.length) return <div className="no-data">Chargement...</div>;

  return (
    <div className="rank-list">
      {items.slice(0, 8).map((item, i) => (
        <div className="rank-item" key={item.name} style={{ animationDelay: `${i * 40}ms` }}>
          <span className="rank-num">{i + 1}</span>
          <span className="rank-name">{item.name}</span>
          <div className="rank-bar-bg">
            <div className={`rank-bar-fill ${color}`} style={{ width: `${Math.max((item.count / max) * 100, 8)}%` }} />
          </div>
          <span className="rank-val">{item.count}</span>
        </div>
      ))}
    </div>
  );
}