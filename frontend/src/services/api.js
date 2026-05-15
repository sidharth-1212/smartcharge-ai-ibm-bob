import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Telemetry endpoints
export const getLatestTelemetry = async () => {
  try {
    const response = await api.get('/api/telemetry/latest');
    return response.data;
  } catch (error) {
    // Silently handle empty database 404s
    if (error.response && error.response.status === 404) {
      return null; 
    }
    console.error('Error fetching latest telemetry:', error);
    throw error;
  }
};

export const getTelemetryHistory = async (limit = 100) => {
  try {
    const response = await api.get('/api/telemetry/history', {
      params: { limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching telemetry history:', error);
    throw error;
  }
};

// Decision endpoints
export const getLatestDecision = async () => {
  try {
    const response = await api.get('/api/bob/decisions/latest');
    return response.data;
  } catch (error) {
    console.error('Error fetching latest decision:', error);
    throw error;
  }
};

export const getDecisionHistory = async (limit = 20) => {
  try {
    const response = await api.get('/api/bob/decisions/history', {
      params: { limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching decision history:', error);
    throw error;
  }
};

// Charging status endpoints
export const getChargingStatus = async () => {
  try {
    const response = await api.get('/api/charging/status');
    return response.data;
  } catch (error) {
    console.error('Error fetching charging status:', error);
    throw error;
  }
};

export const setChargingMode = async (mode) => {
  try {
    const response = await api.post('/api/charging/mode', { mode });
    return response.data;
  } catch (error) {
    console.error('Error setting charging mode:', error);
    throw error;
  }
};

// Analytics endpoints
export const getAnalytics = async () => {
  try {
    const response = await api.get('/api/analytics/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    // Return mock data if endpoint doesn't exist yet
    return {
      cost_savings_today: 0,
      renewable_percentage: 0,
      total_energy_charged: 0,
      grid_impact_score: 0,
    };
  }
};

export default api;

// Made with Bob
