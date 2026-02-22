import React from 'react';
import { Search, X } from 'lucide-react';

const GRADES = [
  { v: '', l: 'Tous', c: 'all' },
  { v: 'a', l: 'A', c: 'a' },
  { v: 'b', l: 'B', c: 'b' },
  { v: 'c', l: 'C', c: 'c' },
  { v: 'd', l: 'D', c: 'd' },
  { v: 'e', l: 'E', c: 'e' },
];

export default function Filters({ filters, updateFilter, resetFilters }) {
  const hasAny = filters.search || filters.nutriscore || filters.brand || filters.category || filters.minQuality > 0;

  return (
    <div className="filters-bar">
      <div className="search-row">
        <Search className="search-icon" size={18} />
        <input
          id="search-input" type="text" className="search-field"
          placeholder="Rechercher un produit..."
          value={filters.search}
          onChange={e => updateFilter('search', e.target.value)}
          autoComplete="off"
        />
        <kbd className="search-shortcut">⌘K</kbd>
      </div>

      <div className="filters-grid">
        <div className="filter-col">
          <label>Nutriscore</label>
          <div className="grade-pills">
            {GRADES.map(g => (
              <button
                key={g.v}
                className={`grade-pill ${g.c} ${filters.nutriscore === g.v ? 'active' : ''}`}
                onClick={() => updateFilter('nutriscore', g.v)}
              >{g.l}</button>
            ))}
          </div>
        </div>

        <div className="filter-col">
          <label>Marque</label>
          <input type="text" className="filter-field" placeholder="Nestlé..."
            value={filters.brand} onChange={e => updateFilter('brand', e.target.value)} />
        </div>

        <div className="filter-col">
          <label>Catégorie</label>
          <input type="text" className="filter-field" placeholder="Breakfast..."
            value={filters.category} onChange={e => updateFilter('category', e.target.value)} />
        </div>

        <div className="filter-col">
          <label>Qualité ≥ {filters.minQuality}</label>
          <input type="range" className="range-track" min="0" max="100"
            value={filters.minQuality} onChange={e => updateFilter('minQuality', parseInt(e.target.value))} />
        </div>

        <button className="btn-clear" onClick={resetFilters}>
          <X size={14} /> Reset
        </button>
      </div>

      {hasAny && (
        <div className="active-tags">
          {filters.search && <span className="active-tag">"{filters.search}"</span>}
          {filters.nutriscore && <span className="active-tag">Nutriscore {filters.nutriscore.toUpperCase()}</span>}
          {filters.brand && <span className="active-tag">{filters.brand}</span>}
          {filters.category && <span className="active-tag">{filters.category}</span>}
          {filters.minQuality > 0 && <span className="active-tag">≥ {filters.minQuality}</span>}
        </div>
      )}
    </div>
  );
}