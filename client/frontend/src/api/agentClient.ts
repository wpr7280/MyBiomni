import axios from 'axios';

export const agentApiClient = axios.create({
  baseURL: import.meta.env.VITE_AGENT_API_URL || '',  // 空字符串 = 同源
  timeout: 60000,
});

agentApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
