import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ page, totalPages, setPage }) {
  if (totalPages <= 1) return null;

  const go = p => { if (p >= 1 && p <= totalPages) { setPage(p); window.scrollTo({ top: 0, behavior: 'smooth' }); } };

  const pages = [1];
  if (page > 3) pages.push('...');
  for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) pages.push(i);
  if (page < totalPages - 2) pages.push('...');
  if (totalPages > 1) pages.push(totalPages);

  return (
    <div className="pager">
      <button className="pager-btn" disabled={page <= 1} onClick={() => go(page - 1)}>
        <ChevronLeft size={14} /> Préc
      </button>
      {pages.map((p, i) => p === '...'
        ? <span key={`d${i}`} className="pager-dots">…</span>
        : <button key={p} className={`pager-num ${p === page ? 'active' : ''}`} onClick={() => go(p)}>{p}</button>
      )}
      <button className="pager-btn" disabled={page >= totalPages} onClick={() => go(page + 1)}>
        Suiv <ChevronRight size={14} />
      </button>
    </div>
  );
}