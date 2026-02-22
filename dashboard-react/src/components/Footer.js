import React from 'react';

const techs = ['Python', 'FastAPI', 'MongoDB', 'PostgreSQL', 'React'];

export default function Footer() {
  return (
    <footer className="foot">
      <div className="foot-inner">
        <span>Food Data Pipeline — B3 Ynov</span>
        <div className="foot-stack">
          {techs.map(t => <span key={t} className="foot-tech">{t}</span>)}
        </div>
      </div>
    </footer>
  );
}