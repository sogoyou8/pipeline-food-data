import React from 'react';
import ProductCard from './ProductCard';

export default function ProductGrid({ products, loading, view, onSelect }) {
  if (loading) return <div className="loading"><div className="spinner" /><p>Chargement...</p></div>;
  if (!products?.length) return <div className="empty-state">Aucun produit trouvé</div>;

  return (
    <div className={view === 'grid' ? 'products-grid' : 'products-list'}>
      {products.map((p, i) => <ProductCard key={p.id} product={p} index={i} onClick={onSelect} />)}
    </div>
  );
}