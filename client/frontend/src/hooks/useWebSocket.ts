import { useEffect, useState, useRef, useCallback } from 'react';
import { message as antdMessage } from 'antd';
import { MockWebSocket, shouldUseMockWebSocket } from '@/mock/websocket';
import { agentApiClient } from '@/api/agentClient';
import type { Message, ExecutionStep, WSMessage } from '@/types';

export function useWebSocket(conversationId: number | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const wsRef = useRef<WebSocket | MockWebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const retryCountRef = useRef(0);
  const maxRetries = 5;
  const isExecutingRef = useRef(false); // Track execution state across reconnects

  // Check if conversation is currently executing (on connect/reconnect)
  const checkExecutionStatus = useCallback(async () => {
    if (!conversationId) return false;
    try {
      const response = await agentApiClient.get(`/agent-api/execution-status/${conversationId}`);
      return response.data?.executing === true;
    } catch {
      return false;
    }
  }, [conversationId]);

  const connect = useCallback(() => {
    if (!conversationId) return;

    const token = localStorage.getItem('token');
    if (!token) {
      console.log('Not logged in, skipping WebSocket connection');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`;
    const url = `${wsUrl}/ws/chat/${conversationId}?token=${encodeURIComponent(token)}`;

    console.log('正在连接 WebSocket:', {
      url: url.replace(/token=[^&]+/, 'token=***'),
      conversationId,
      retryCount: retryCountRef.current,
      timestamp: new Date().toISOString(),
    });

    const ws = shouldUseMockWebSocket() ? new MockWebSocket(url) : new WebSocket(url);
    let hasConnected = false;

    ws.addEventListener('open', async () => {
      hasConnected = true;
      retryCountRef.current = 0;
      console.log('✅ WebSocket 连接成功');

      // Check if there's an active execution we need to resume
      const executing = await checkExecutionStatus();
      if (executing) {
        console.log('🔄 检测到正在执行的任务，恢复执行状态');
        setIsExecuting(true);
        isExecutingRef.current = true;
        // Add temporary thinking message if not already present
        setMessages((prev) => {
          const hasThinking = prev.some((m) => (m as any).isTemporary);
          if (!hasThinking) {
            return [...prev, {
              id: Date.now(),
              conversationId: conversationId!,
              role: 'assistant' as const,
              content: '🔄 Reconnected — execution in progress...',
              createdAt: new Date().toISOString(),
              isTemporary: true,
            }];
          }
          return prev;
        });
      }
    });

    ws.addEventListener('message', (event: any) => {
      try {
        const data: WSMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'execution_start':
            setIsExecuting(true);
            isExecutingRef.current = true;
            setExecutionSteps([]);
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

          case 'execution_resumed':
            // Server tells us execution is still running after reconnect
            setIsExecuting(true);
            isExecutingRef.current = true;
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
            isExecutingRef.current = false;
            if (data.message) {
              setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
              setMessages((prev) => [...prev, data.message!]);
            }
            break;

          case 'execution_error':
            setIsExecuting(false);
            isExecutingRef.current = false;
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            
            const errorMessage = data.error || '执行失败';
            const technicalDetails = data.technical_details;
            
            const errorBubble = {
              id: Date.now(),
              conversationId: conversationId!,
              role: 'assistant' as const,
              content: `❌ **Execution Failed**\n\n${errorMessage}${technicalDetails ? `\n\n<details>\n<summary>Technical Details</summary>\n\n\`\`\`\n${technicalDetails}\n\`\`\`\n</details>` : ''}`,
              createdAt: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorBubble]);
            
            antdMessage.error({
              content: errorMessage,
              duration: 8,
            });
            break;

          case 'config_error':
            setIsExecuting(false);
            isExecutingRef.current = false;
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            antdMessage.error({
              content: data.error || 'System configuration error',
              duration: 8,
            });
            break;

          case 'quota_exceeded':
            setIsExecuting(false);
            isExecutingRef.current = false;
            setMessages((prev) => prev.filter((m) => !(m as any).isTemporary));
            antdMessage.error({
              content: data.error || 'Token quota exhausted',
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
        error,
        readyState: ws.readyState,
        timestamp: new Date().toISOString(),
      });
    });

    ws.addEventListener('close', (event: any) => {
      console.log('WebSocket 已断开:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        hasConnected,
        isExecuting: isExecutingRef.current,
        retryCount: retryCountRef.current,
        timestamp: new Date().toISOString(),
      });
      
      if (!hasConnected && event.code === 1006) {
        retryCountRef.current += 1;
        if (retryCountRef.current > maxRetries) {
          antdMessage.error({
            content: 'WebSocket connection failed after multiple retries',
            duration: 5,
          });
        }
      }
      
      // Auto-reconnect with exponential backoff
      // Always reconnect if execution is in progress
      const shouldReconnect = !shouldUseMockWebSocket() && (
        (event.code === 1006 && retryCountRef.current <= maxRetries) ||
        isExecutingRef.current
      );
      
      if (shouldReconnect) {
        const retryDelay = Math.min(1000 * Math.pow(2, retryCountRef.current - 1), 5000);
        console.log(`🔄 Will reconnect in ${retryDelay}ms (executing: ${isExecutingRef.current})`);
        reconnectTimeoutRef.current = setTimeout(() => {
          retryCountRef.current += 1;
          connect();
        }, retryDelay);
      }
    });

    wsRef.current = ws;
  }, [conversationId, checkExecutionStatus]);

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

  const sendMessage = useCallback((content: string, fileIds: number[] = []) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'send_message',
        content,
        file_ids: fileIds,
      }));
    } else {
      antdMessage.error('Connection not established, please try again');
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
