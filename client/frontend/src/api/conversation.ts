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
      title ? { title } : {}  // 如果没有 title，发送空对象
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
      '/api/messages/list',
      { params: { conversationId, currentPage: page, pageSize: size } }
    );
    return response.data.data;
  },

  /**
   * 获取消息的执行步骤
   */
  async getExecutionSteps(messageId: number): Promise<ExecutionStep[]> {
    // 如果启用 Mock，使用 Mock 数据
    if (USE_MOCK) {
      return mockApi.getExecutionSteps(messageId);
    }

    const response = await apiClient.get<ApiResponse<ExecutionStep[]>>(
      '/api/execution-steps/list',
      { params: { messageId } }
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
      '/api/messages/send',
      { conversationId, content }
    );
    return response.data.data;
  },

  /**
   * 导出对话为 Markdown
   */
  async exportConversation(conversationId: number, includeImages = true): Promise<void> {
    // 如果启用 Mock，模拟下载
    if (USE_MOCK) {
      console.log('Mock: Exporting conversation', conversationId);
      // 创建一个模拟的 Markdown 文件
      const mockContent = `# Conversation ${conversationId}\n\nThis is a mock export.`;
      const blob = new Blob([mockContent], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation_${conversationId}.md`;
      a.click();
      window.URL.revokeObjectURL(url);
      return;
    }

    // 发送导出请求，后端返回文件流
    const response = await apiClient.post(
      '/api/conversations/export',
      { conversationId, includeImages },
      { responseType: 'blob' }  // 重要：告诉 axios 响应是二进制数据
    );

    // 从 Content-Disposition 获取文件名
    const contentDisposition = response.headers['content-disposition'];
    const contentType = response.headers['content-type'] || 'text/markdown';
    let filename = `conversation_${conversationId}_${Date.now()}.md`;
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
      if (match) filename = match[1];
    }

    // 检查是否返回了错误（JSON 而非文件）
    if (contentType.includes('application/json')) {
      const text = await (response.data as Blob).text();
      const error = JSON.parse(text);
      throw new Error(error.error || error.message || 'Export failed');
    }

    // 创建下载链接
    const blob = new Blob([response.data], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },
};
