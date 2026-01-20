import { apiClient } from './client';
import { mockApi, USE_MOCK } from '@/mock/api';
import type { Conversation, Message, ApiResponse } from '@/types';

export const conversationApi = {
  /**
   * 获取对话列表
   */
  async getConversations(page = 1, size = 20): Promise<Conversation[]> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.getConversations();
    }

    const response = await apiClient.get<ApiResponse<Conversation[]>>(
      '/api/conversations/list',
      { params: { page, size } }
    );
    return response.data.data;
  },

  /**
   * 创建新对话
   */
  async createConversation(title?: string): Promise<Conversation> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.createConversation(title);
    }

    const response = await apiClient.post<ApiResponse<Conversation>>(
      '/api/conversations/create',
      { title: title || '新对话' }
    );
    return response.data.data;
  },

  /**
   * 获取对话详情
   */
  async getConversation(id: number): Promise<Conversation> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.getConversation(id);
    }

    const response = await apiClient.post<ApiResponse<Conversation>>(
      '/api/conversations/get',
      { conversationId: id }
    );
    return response.data.data;
  },

  /**
   * 更新对话标题（重命名）
   */
  async updateConversation(id: number, title: string): Promise<void> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.updateConversation(id, title);
    }

    await apiClient.post(
      '/api/conversations/update',
      { conversationId: id, title }
    );
  },

  /**
   * 删除对话
   */
  async deleteConversation(id: number): Promise<void> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.deleteConversation(id);
    }

    await apiClient.post(
      '/api/conversations/delete',
      { conversationId: id }
    );
  },

  /**
   * 获取对话消息
   */
  async getMessages(conversationId: number, page = 1, size = 50): Promise<Message[]> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.getMessages(conversationId);
    }

    const response = await apiClient.get<ApiResponse<Message[]>>(
      `/api/conversations/${conversationId}/messages`,
      { params: { page, size } }
    );
    return response.data.data;
  },

  /**
   * 发送消息（保存到数据库，检查配额）
   */
  async sendMessage(conversationId: number, content: string): Promise<Message> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.sendMessage(conversationId, content);
    }

    const response = await apiClient.post<ApiResponse<Message>>(
      `/api/conversations/${conversationId}/messages`,
      { content }
    );
    return response.data.data;
  },
};
