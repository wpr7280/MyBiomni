import axios from 'axios';
import type { ApiResponse } from '@/types';

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',  // 空字符串 = 同源，由 Nginx 代理
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：统一处理响应
apiClient.interceptors.response.use(
  (response) => {
    // 跳过 blob 响应（如文件下载）
    if (response.config.responseType === 'blob') {
      return response;
    }

    const data: ApiResponse = response.data;
    
    // 如果是标准的 ApiResponse 格式
    if (data.code !== undefined) {
      if (data.code === 200) {
        return response;
      } else {
        return Promise.reject(new Error(data.message || '请求失败'));
      }
    }
    
    return response;
  },
  (error) => {
    // 处理 401 未授权
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // 处理其他错误
    const message = error.response?.data?.message || error.message || '网络错误';
    return Promise.reject(new Error(message));
  }
);
