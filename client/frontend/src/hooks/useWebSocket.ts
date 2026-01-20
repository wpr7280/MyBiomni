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
      antdMessage.error('请先登录');
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/ws/chat/${conversationId}?token=${encodeURIComponent(token)}`;

    // 判断是否使用 Mock WebSocket
    const ws = shouldUseMockWebSocket() ? new MockWebSocket(url) : new WebSocket(url);

    ws.addEventListener('open', () => {
      console.log('WebSocket 已连接');
    });

    ws.addEventListener('message', (event: any) => {
      try {
        const data: WSMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'execution_start':
            setIsExecuting(true);
            setExecutionSteps([]);
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
              setMessages((prev) => [...prev, data.message!]);
            }
            break;

          case 'execution_error':
            setIsExecuting(false);
            antdMessage.error(data.error || '执行失败');
            break;
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error);
      }
    });

    ws.addEventListener('error', (error: any) => {
      console.error('WebSocket 错误:', error);
      antdMessage.error('连接失败');
    });

    ws.addEventListener('close', () => {
      console.log('WebSocket 已断开');
      // 5秒后尝试重连（仅在非 Mock 模式下）
      if (!shouldUseMockWebSocket()) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('尝试重新连接...');
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
      wsRef.current.send(JSON.stringify({
        type: 'send_message',
        content,
      }));

      // 立即添加用户消息到界面
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          conversationId: conversationId!,
          role: 'user',
          content,
          createdAt: new Date().toISOString(),
        },
      ]);
    } else {
      antdMessage.error('连接未建立，请稍后重试');
    }
  }, [conversationId]);

  return {
    messages,
    setMessages,
    executionSteps,
    isExecuting,
    sendMessage,
  };
}
