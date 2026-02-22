import React, { useState } from 'react';
import { LayoutGrid, List } from 'lucide-react';
import Filters from '../components/Filters';
import ProductGrid from '../components/ProductGrid';
import Pagination from '../components/Pagination';
import ProductModal from '../components/ProductModal';
import { useProducts } from '../hooks/useProducts';

export default function ProductsPage() {
  const { data, loading, page, setPage, filters, updateFilter, resetFilters } = useProducts();
  const [view, setView] = useState('grid');
  const [selectedId, setSelectedId] = useState(null);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Explorer</h1>
        <p className="page-subtitle">Recherchez et filtrez les produits de la base</p>
      </div>

      <div style={{ marginTop: '1.25rem' }}>
        <Filters filters={filters} updateFilter={updateFilter} resetFilters={resetFilters} />

        <div className="toolbar">
          <span className="toolbar-count">
            <strong>{data.total.toLocaleString('fr-FR')}</strong> résultat{data.total !== 1 ? 's' : ''}
          </span>
          <div className="toolbar-views">
            <button className={`view-btn ${view === 'grid' ? 'active' : ''}`} onClick={() => setView('grid')}>
              <LayoutGrid size={16} />
            </button>
            <button className={`view-btn ${view === 'list' ? 'active' : ''}`} onClick={() => setView('list')}>
              <List size={16} />
            </button>
          </div>
        </div>

        <ProductGrid products={data.items} loading={loading} view={view} onSelect={setSelectedId} />
        <Pagination page={page} totalPages={data.total_pages} setPage={setPage} />
      </div>

      {selectedId && <ProductModal productId={selectedId} onClose={() => setSelectedId(null)} />}
    </>
  );
}