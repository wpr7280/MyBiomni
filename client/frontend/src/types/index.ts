// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  realName?: string;
  avatar?: string;
}

// 对话类型
export interface Conversation {
  id: number;
  title: string;
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  messageCount: number;
  lastMessageAt?: string;
  createdAt: string;
  updatedAt: string;
}

// 消息类型
export interface Message {
  id: number;
  conversationId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contentType?: 'text' | 'markdown' | 'code';
  tokens?: number;
  createdAt: string;
}

// 执行步骤类型
export interface ExecutionStep {
  id: number;
  conversationId: number;
  messageId: number;
  stepOrder: number;
  stepType: 'reasoning' | 'tool_call' | 'result';
  stepName?: string;
  toolName?: string;
  toolInput?: any;
  toolOutput?: string;
  status: 'running' | 'success' | 'failed';
  errorMessage?: string;
  durationMs: number;
  startedAt: string;
  completedAt?: string;
}

// WebSocket 消息类型
export interface WSMessage {
  type: 'execution_start' | 'execution_step' | 'execution_complete' | 'execution_error';
  step?: ExecutionStep;
  message?: Message;
  error?: string;
}

// API 响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}
