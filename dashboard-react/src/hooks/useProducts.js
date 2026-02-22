import { useState, useEffect, useCallback } from 'react';
import { fetchProducts } from '../api/client';
import { useDebounce } from './useDebounce';

export function useProducts() {
  const [data, setData] = useState({ items: [], total: 0, total_pages: 1 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    search: '', nutriscore: '', brand: '', category: '', minQuality: 0
  });

  const debouncedSearch = useDebounce(filters.search);
  const debouncedBrand = useDebounce(filters.brand);
  const debouncedCategory = useDebounce(filters.category);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchProducts({
        page,
        pageSize: 20,
        search: debouncedSearch,
        nutriscore: filters.nutriscore,
        brand: debouncedBrand,
        category: debouncedCategory,
        minQuality: filters.minQuality,
      });
      setData(result);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, filters.nutriscore, debouncedBrand, debouncedCategory, filters.minQuality]);

  useEffect(() => { load(); }, [load]);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const resetFilters = () => {
    setFilters({ search: '', nutriscore: '', brand: '', category: '', minQuality: 0 });
    setPage(1);
  };

  return { data, loading, page, setPage, filters, updateFilter, resetFilters };
}