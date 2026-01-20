import { apiClient } from './client';
import { mockApi, USE_MOCK } from '@/mock/api';
import type { User, ApiResponse } from '@/types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  userId: string;
  email: string;
  username: string;
  role: string;
  forcePasswordChange: boolean;
}

export const authApi = {
  /**
   * 用户登录
   */
  async login(data: LoginRequest): Promise<{ token: string; user: User }> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.login(data.email, data.password);
    }

    const response = await apiClient.post<ApiResponse<LoginResponse>>(
      '/api/auth/login',
      data
    );
    
    const loginData = response.data.data;
    
    // 转换为前端需要的格式
    return {
      token: loginData.token,
      user: {
        id: parseInt(loginData.userId),
        username: loginData.username,
        email: loginData.email,
        role: loginData.role,
      },
    };
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.getCurrentUser();
    }

    const response = await apiClient.get<ApiResponse<LoginResponse>>('/api/auth/me');
    const data = response.data.data;
    
    // 转换为前端需要的格式
    return {
      id: parseInt(data.userId),
      username: data.username,
      email: data.email,
      role: data.role,
    };
  },

  /**
   * 登出
   */
  async logout(): Promise<void> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.logout();
    }

    await apiClient.post('/api/auth/logout');
  },
};
