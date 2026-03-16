import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cámaras
export const cameraApi = {
  getAll: () => api.get<Camera[]>('/cameras'),
  getById: (id: string) => api.get<Camera>(`/cameras/${id}`),
  create: (data: { name: string; ip_address: string; location?: string; brand?: string }) => 
    api.post<Camera>('/cameras', data),
  checkNow: (id: string) => api.post(`/cameras/${id}/check`),
  getLogs: (id: string) => api.get<ConnectivityLog[]>(`/cameras/${id}/logs`),
  checkAll: () => api.post('/cameras/check-all'),
};

// Stats
export const statsApi = {
  getStats: () => api.get('/stats'),
};

export { API_URL };