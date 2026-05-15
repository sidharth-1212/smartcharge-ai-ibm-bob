import { useState, useEffect, useCallback } from 'react';
import { getLatestDecision, getDecisionHistory } from '../services/api';

const POLL_INTERVAL = parseInt(import.meta.env.VITE_POLL_INTERVAL) || 5000;

export const useDecisions = () => {
  const [decision, setDecision] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLatest = useCallback(async () => {
    try {
      const data = await getLatestDecision();
      setDecision(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch decision:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async (limit = 20) => {
    try {
      const data = await getDecisionHistory(limit);
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch decision history:', err);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchLatest();
    fetchHistory();

    // Set up polling
    const interval = setInterval(() => {
      fetchLatest();
      fetchHistory();
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchLatest, fetchHistory]);

  return {
    decision,
    history,
    loading,
    error,
    refresh: fetchLatest,
  };
};

export default useDecisions;

// Made with Bob
