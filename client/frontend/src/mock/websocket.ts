import type { ExecutionStep, Message } from '@/types';
import { delay } from './data';

// Mock WebSocket 类
export class MockWebSocket {
  private listeners: Record<string, Function[]> = {};
  private conversationId: string;
  public readyState: number = WebSocket.CONNECTING;

  constructor(url: string) {
    // 从 URL 中提取 conversationId
    const match = url.match(/\/ws\/chat\/(\d+)/);
    this.conversationId = match ? match[1] : '1';

    // 模拟连接建立
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.trigger('open', {});
    }, 500);
  }

  addEventListener(event: string, callback: Function) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  removeEventListener(event: string, callback: Function) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter((cb) => cb !== callback);
    }
  }

  send(data: string) {
    const message = JSON.parse(data);

    if (message.type === 'send_message') {
      // 模拟 Agent 执行
      this.simulateAgentExecution(message.content);
    }
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    this.trigger('close', {});
  }

  private trigger(event: string, data: any) {
    if (this.listeners[event]) {
      this.listeners[event].forEach((callback) => callback(data));
    }
  }

  private async simulateAgentExecution(userQuery: string) {
    // 1. 发送执行开始
    await delay(300);
    this.trigger('message', {
      data: JSON.stringify({
        type: 'execution_start',
      }),
    });

    // 2. 模拟执行步骤
    const steps = this.generateMockSteps(userQuery);

    for (const step of steps) {
      await delay(step.durationMs);
      this.trigger('message', {
        data: JSON.stringify({
          type: 'execution_step',
          step,
        }),
      });
    }

    // 3. 发送执行完成
    await delay(1000);
    const assistantMessage = this.generateMockResponse(userQuery);
    this.trigger('message', {
      data: JSON.stringify({
        type: 'execution_complete',
        message: assistantMessage,
      }),
    });
  }

  private generateMockSteps(query: string): ExecutionStep[] {
    const now = new Date();
    const steps: ExecutionStep[] = [];

    // 步骤 1: 分析问题
    steps.push({
      id: Date.now() + 1,
      conversationId: parseInt(this.conversationId),
      messageId: Date.now(),
      stepOrder: 1,
      stepType: 'reasoning',
      stepName: '分析用户问题',
      status: 'success',
      durationMs: 500,
      startedAt: new Date(now.getTime()).toISOString(),
      completedAt: new Date(now.getTime() + 500).toISOString(),
    });

    // 步骤 2: 搜索知识库
    steps.push({
      id: Date.now() + 2,
      conversationId: parseInt(this.conversationId),
      messageId: Date.now(),
      stepOrder: 2,
      stepType: 'tool_call',
      stepName: '搜索相关知识',
      toolName: 'search_knowledge',
      toolInput: {
        query: query.substring(0, 50),
        limit: 5,
      },
      toolOutput: '找到 5 篇相关文献和知识条目',
      status: 'success',
      durationMs: 1200,
      startedAt: new Date(now.getTime() + 500).toISOString(),
      completedAt: new Date(now.getTime() + 1700).toISOString(),
    });

    // 步骤 3: 生成回答
    steps.push({
      id: Date.now() + 3,
      conversationId: parseInt(this.conversationId),
      messageId: Date.now(),
      stepOrder: 3,
      stepType: 'tool_call',
      stepName: '生成回答',
      toolName: 'generate_answer',
      toolInput: {
        context: '相关知识内容',
        question: query,
      },
      toolOutput: '回答生成完成',
      status: 'success',
      durationMs: 2000,
      startedAt: new Date(now.getTime() + 1700).toISOString(),
      completedAt: new Date(now.getTime() + 3700).toISOString(),
    });

    return steps;
  }

  private generateMockResponse(query: string): Message {
    return {
      id: Date.now(),
      conversationId: parseInt(this.conversationId),
      role: 'assistant',
      content: `这是对"${query}"的回答。

## 回答内容

根据您的问题，我为您整理了以下信息：

1. **关键概念**：这是一个关于生物医学的问题
2. **相关知识**：从知识库中检索到相关内容
3. **建议**：您可以进一步了解相关主题

如果您需要更详细的信息，请告诉我！`,
      contentType: 'markdown',
      tokens: 150,
      inputTokens: Math.ceil(query.length / 4),
      outputTokens: 135,
      createdAt: new Date().toISOString(),
    };
  }
}

// 判断是否使用 Mock WebSocket
export function shouldUseMockWebSocket(): boolean {
  return import.meta.env.VITE_USE_MOCK === 'true';
}
