import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response || error.message);
    return Promise.reject(error);
  }
);

export const alertService = {
  getStats: () => api.get('/alerts/statistics'),
  getAlerts: (params) => api.get('/alerts', { params }),
  getAlert: (id) => api.get(`/alerts/${id}`),
  createAlert: (data) => api.post('/alerts', data),
  updateAlert: (id, data) => api.put(`/alerts/${id}`, data),
};

export const playbookService = {
  getPlaybooks: () => api.get('/playbooks'),
  getPlaybook: (id) => api.get(`/playbooks/${id}`),
  runPlaybook: (id) => api.post(`/playbooks/${id}/execute`),
};

export default api;