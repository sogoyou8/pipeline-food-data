import { useState, useEffect } from 'react';
import { fetchStats } from '../api/client';

export function useStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading, error };
}