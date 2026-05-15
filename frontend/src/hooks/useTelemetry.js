import { useState, useEffect, useCallback } from 'react';
import { getLatestTelemetry, getTelemetryHistory } from '../services/api';

const POLL_INTERVAL = parseInt(import.meta.env.VITE_POLL_INTERVAL) || 5000;

export const useTelemetry = () => {
  const [telemetry, setTelemetry] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLatest = useCallback(async () => {
    try {
      const data = await getLatestTelemetry();
      setTelemetry(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch telemetry:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async (limit = 100) => {
    try {
      const data = await getTelemetryHistory(limit);
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch telemetry history:', err);
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
    telemetry,
    history,
    loading,
    error,
    refresh: fetchLatest,
  };
};

export default useTelemetry;

// Made with Bob
