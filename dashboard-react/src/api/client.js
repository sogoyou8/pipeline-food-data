const API = 'http://localhost:8000';

export async function checkHealth() {
  const r = await fetch(`${API}/`);
  if (!r.ok) throw new Error('API offline');
  return r.json();
}

export async function fetchStats() {
  const r = await fetch(`${API}/stats`);
  if (!r.ok) throw new Error('Stats error');
  return r.json();
}

export async function fetchProducts(params = {}) {
  const query = new URLSearchParams();
  query.set('page', params.page || 1);
  query.set('page_size', params.pageSize || 20);
  if (params.search) query.set('search', params.search);
  if (params.nutriscore) query.set('nutriscore', params.nutriscore);
  if (params.brand) query.set('brand', params.brand);
  if (params.category) query.set('category', params.category);
  if (params.minQuality > 0) query.set('min_quality', params.minQuality);

  const r = await fetch(`${API}/products?${query}`);
  if (!r.ok) throw new Error('Products error');
  return r.json();
}

export async function fetchProduct(id) {
  const r = await fetch(`${API}/products/${id}`);
  if (!r.ok) throw new Error('Product not found');
  return r.json();
}