import type { User, Conversation, Message } from '@/types';
import {
  mockUsers,
  mockConversations,
  mockMessages,
  generateMockToken,
  delay,
} from './data';

// 是否启用 Mock（通过环境变量控制）
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Mock 状态
let currentConversations = [...mockConversations];
let nextConversationId = 4;
let nextMessageId = 9;

export const mockApi = {
  /**
   * 登录
   */
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    await delay(800);

    const userInfo = mockUsers[email];
    if (!userInfo || userInfo.password !== password) {
      throw new Error('邮箱或密码错误');
    }

    return {
      token: generateMockToken(userInfo.user.id),
      user: userInfo.user,
    };
  },

  /**
   * 获取当前用户
   */
  async getCurrentUser(): Promise<User> {
    await delay(300);

    // 从 localStorage 获取 token
    const token = localStorage.getItem('token');
    if (!token || !token.startsWith('mock_token_')) {
      throw new Error('Token 无效');
    }

    // 从 token 中提取 userId
    const userId = parseInt(token.split('_')[2]);
    const user = Object.values(mockUsers).find((u) => u.user.id === userId);

    if (!user) {
      throw new Error('用户不存在');
    }

    return user.user;
  },

  /**
   * 登出
   */
  async logout(): Promise<void> {
    await delay(300);
    // Mock 登出不需要做任何事
  },

  /**
   * 获取对话列表
   */
  async getConversations(): Promise<Conversation[]> {
    await delay(500);
    return [...currentConversations].sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  },

  /**
   * 创建对话
   */
  async createConversation(title?: string): Promise<Conversation> {
    await delay(500);

    const newConversation: Conversation = {
      id: nextConversationId++,
      title: title || '新对话',
      status: 'active',
      messageCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    currentConversations.unshift(newConversation);
    mockMessages[newConversation.id] = [];

    return newConversation;
  },

  /**
   * 获取对话详情
   */
  async getConversation(id: number): Promise<Conversation> {
    await delay(300);

    const conversation = currentConversations.find((c) => c.id === id);
    if (!conversation) {
      throw new Error('对话不存在');
    }

    return conversation;
  },

  /**
   * 删除对话
   */
  async deleteConversation(id: number): Promise<void> {
    await delay(500);

    currentConversations = currentConversations.filter((c) => c.id !== id);
    delete mockMessages[id];
  },

  /**
   * 获取消息列表
   */
  async getMessages(conversationId: number): Promise<Message[]> {
    await delay(500);

    return mockMessages[conversationId] || [];
  },

  /**
   * 发送消息
   */
  async sendMessage(conversationId: number, content: string): Promise<Message> {
    await delay(300);

    const newMessage: Message = {
      id: nextMessageId++,
      conversationId,
      role: 'user',
      content,
      contentType: 'text',
      tokens: Math.ceil(content.length / 4),
      createdAt: new Date().toISOString(),
    };

    if (!mockMessages[conversationId]) {
      mockMessages[conversationId] = [];
    }

    mockMessages[conversationId].push(newMessage);

    // 更新对话
    const conversation = currentConversations.find((c) => c.id === conversationId);
    if (conversation) {
      conversation.messageCount++;
      conversation.lastMessageAt = newMessage.createdAt;
      conversation.updatedAt = newMessage.createdAt;
    }

    return newMessage;
  },
};

// 导出是否使用 Mock
export { USE_MOCK };
