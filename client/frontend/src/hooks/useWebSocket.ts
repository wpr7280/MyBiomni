import { useEffect, useState, useRef, useCallback } from 'react';
import { message as antdMessage } from 'antd';
import { MockWebSocket, shouldUseMockWebSocket } from '@/mock/websocket';
import type { Message, ExecutionStep, WSMessage } from '@/types';

export function useWebSocket(conversationId: number | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const wsRef = useRef<WebSocket | MockWebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!conversationId) return;

    const token = localStorage.getItem('token');
    if (!token) {
      console.log('未登录，跳过 WebSocket 连接');
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/ws/chat/${conversationId}?token=${encodeURIComponent(token)}`;

    console.log('正在连接 WebSocket:', {
      url: url.replace(/token=[^&]+/, 'token=***'),
      conversationId,
      wsUrl,
      timestamp: new Date().toISOString(),
    });

    // 判断是否使用 Mock WebSocket
    const ws = shouldUseMockWebSocket() ? new MockWebSocket(url) : new WebSocket(url);
    
    // 标记连接是否成功过
    let hasConnected = false;

    ws.addEventListener('open', () => {
      hasConnected = true;
      console.log('✅ WebSocket 连接成功:', {
        url: url.replace(/token=[^&]+/, 'token=***'),
        readyState: ws.readyState,
        timestamp: new Date().toISOString(),
      });
    });

    ws.addEventListener('message', (event: any) => {
      try {
        const data: WSMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'execution_start':
            setIsExecuting(true);
            setExecutionSteps([]);
            // 如果还没有临时消息，添加一个
            setMessages((prev) => {
              const hasThinking = prev.some((m) => (m as any).isTemporary);
              if (!hasThinking) {
                return [...prev, {
                  id: Date.now(),
                  conversationId: conversationId!,
                  role: 'assistant' as const,
                  content: '🤔 Thinking...',
                  createdAt: new Date().toISOString(),
                  isTemporary: true,
                }];
              }
              return prev;
            });
            break;

          case 'execution_step':
            if (data.step) {
              setExecutionSteps((prev) => {
                const existingIndex = prev.findIndex((s) => s.id === data.step!.id);
                if (existingIndex >= 0) {
                  const newSteps = [...prev];
                  newSteps[existingIndex] = data.step!;
                  return newSteps;
                }
                return [...prev, data.step!];
              });
            }
            break;

          case 'execution_complete':
            setIsExecuting(false);
            if (data.message) {
              // 移除临时的"正在思考"消息
              setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
              // 添加真实的 AI 回复
              setMessages((prev) => [...prev, data.message!]);
            }
            break;

          case 'execution_error':
            setIsExecuting(false);
            // 移除临时消息
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            
            // 显示错误消息
            const errorMessage = data.error || '执行失败';
            const technicalDetails = data.technical_details;
            
            // 在聊天窗口显示错误消息
            const errorBubble = {
              id: Date.now(),
              conversationId: conversationId!,
              role: 'assistant' as const,
              content: `❌ **执行失败**\n\n${errorMessage}${technicalDetails ? `\n\n<details>\n<summary>技术详情</summary>\n\n\`\`\`\n${technicalDetails}\n\`\`\`\n</details>` : ''}`,
              createdAt: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorBubble]);
            
            // 同时显示通知
            antdMessage.error({
              content: errorMessage,
              duration: 8,
            });
            break;

          case 'config_error':
            setIsExecuting(false);
            // 移除临时消息
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            antdMessage.error({
              content: data.error || '系统配置错误',
              duration: 8,
            });
            break;

          case 'quota_exceeded':
            setIsExecuting(false);
            // 移除临时消息
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            antdMessage.error({
              content: data.error || 'Token 配额已用完',
              duration: 5,
            });
            break;
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error);
      }
    });

    ws.addEventListener('error', (error: any) => {
      console.error('WebSocket 连接错误:', {
        url,
        error,
        readyState: ws.readyState,
        timestamp: new Date().toISOString(),
      });
      
      // 不立即显示错误，等待 close 事件判断
    });

    ws.addEventListener('close', (event: any) => {
      console.log('WebSocket 已断开:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        url,
        timestamp: new Date().toISOString(),
      });
      
      // 只有在从未成功连接过，且是异常关闭时才显示错误
      if (!hasConnected && event.code !== 1000) {
        console.error('WebSocket 连接失败:', {
          code: event.code,
          reason: event.reason || '未知原因',
        });
        
        // 显示用户友好的错误信息
        let errorMessage = 'WebSocket 连接失败';
        if (event.code === 1006) {
          errorMessage = 'WebSocket 连接失败：无法连接到服务器';
        } else if (event.code === 1002) {
          errorMessage = 'WebSocket 连接失败：认证失败';
        }
        
        antdMessage.error({
          content: errorMessage,
          duration: 5,
        });
      }
      
      // 5秒后尝试重连（仅在非 Mock 模式下）
      if (!shouldUseMockWebSocket()) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('尝试重新连接 WebSocket...');
          connect();
        }, 5000);
      }
    });

    wsRef.current = ws;
  }, [conversationId]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // 只发送消息，不添加到界面（等待 WebSocket 返回）
      wsRef.current.send(JSON.stringify({
        type: 'send_message',
        content,
      }));
    } else {
      antdMessage.error('连接未建立，请稍后重试');
    }
  }, [conversationId]);

  return {
    messages,
    setMessages,
    executionSteps,
    setExecutionSteps,
    isExecuting,
    sendMessage,
  };
}
