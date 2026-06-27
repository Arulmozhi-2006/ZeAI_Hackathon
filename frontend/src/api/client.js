import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const createClient = (token) => {
  const headers = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return axios.create({
    baseURL: API_BASE_URL,
    headers,
  })
}

export const createClientWithApiKey = (apiKey) => {
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
  })
}

// Auth endpoints
export const authAPI = {
  register: (email, password, fullName) =>
    createClient().post('/auth/register', { email, password, full_name: fullName }),
  login: (email, password) =>
    createClient().post('/auth/login', { email, password }),
  refresh: (refreshToken) =>
    createClient().post('/auth/refresh', { refresh_token: refreshToken }),
  me: (token) =>
    createClient(token).get('/auth/me'),
}

// Firewall endpoints
export const firewallAPI = {
  analyze: (prompt, provider, token) =>
    createClient(token).post('/firewall/analyze', { prompt, provider }),
}

// Logs endpoints
export const logsAPI = {
  getPromptLogs: (page = 1, pageSize = 20, token) =>
    createClient(token).get('/logs/prompts', { params: { page, page_size: pageSize } }),
  getThreatLogs: (page = 1, pageSize = 20, severity = null, token) =>
    createClient(token).get('/logs/threats', { params: { page, page_size: pageSize, severity } }),
  getDetectionDetail: (promptLogId, token) =>
    createClient(token).get(`/logs/${promptLogId}`),
}

// Analytics endpoints
export const analyticsAPI = {
  getOverview: (days = 30, token) =>
    createClient(token).get('/analytics/overview', { params: { days } }),
  getCategories: (days = 30, token) =>
    createClient(token).get('/analytics/categories', { params: { days } }),
  getSeverity: (days = 30, token) =>
    createClient(token).get('/analytics/severity', { params: { days } }),
  getTrends: (days = 14, token) =>
    createClient(token).get('/analytics/trends', { params: { days } }),
}

// Models endpoints
export const modelsAPI = {
  getMetrics: (token) =>
    createClient(token).get('/models/metrics'),
}

// API Keys endpoints
export const apiKeysAPI = {
  create: (name, expiresAt, token) =>
    createClient(token).post('/auth/api-keys', { name, expires_at: expiresAt }),
  list: (token) =>
    createClient(token).get('/auth/api-keys'),
  revoke: (keyId, token) =>
    createClient(token).delete(`/auth/api-keys/${keyId}`),
}