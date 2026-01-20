import { useEffect } from 'react';
import { Layout } from 'antd';
import { Bubble, Sender } from '@ant-design/x';
import ExecutionPanel from './ExecutionPanel';
import { useWebSocket } from '@/hooks/useWebSocket';
import { conversationApi } from '@/api/conversation';

const { Content } = Layout;

interface ChatWindowProps {
  conversationId: number;
}

export default function ChatWindow({ conversationId }: ChatWindowProps) {
  const { messages, setMessages, executionSteps, isExecuting, sendMessage } =
    useWebSocket(conversationId);

  // 加载历史消息
  useEffect(() => {
    loadMessages();
  }, [conversationId]);

  async function loadMessages() {
    try {
      const data = await conversationApi.getMessages(conversationId);
      setMessages(data);
    } catch (error) {
      console.error('加载消息失败:', error);
    }
  }

  async function handleSendMessage(content: string) {
    try {
      // 1. 先调用 Spring Boot API 保存消息和检查配额
      await conversationApi.sendMessage(conversationId, content);

      // 2. 通过 WebSocket 发送给 Python Agent 执行
      sendMessage(content);
    } catch (error: any) {
      console.error('发送消息失败:', error);
    }
  }

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: '#fff',
      }}
    >
      {/* 上部分：左右布局 */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* 左侧：对话区域 */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              flex: 1,
              overflow: 'auto',
              padding: '24px 32px',
              background: '#fafafa',
            }}
          >
            {messages.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  padding: '100px 20px',
                  color: '#bfbfbf',
                }}
              >
                <div style={{ fontSize: 64, marginBottom: 16 }}>💬</div>
                <div style={{ fontSize: 16, color: '#8c8c8c' }}>
                  开始新的对话
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <Bubble
                  key={msg.id}
                  placement={msg.role === 'user' ? 'end' : 'start'}
                  content={msg.content}
                  avatar={
                    msg.role === 'assistant'
                      ? { icon: '🤖', style: { background: '#1890ff' } }
                      : { icon: '👤', style: { background: '#52c41a' } }
                  }
                  loading={msg.role === 'assistant' && isExecuting}
                  style={{ marginBottom: 20 }}
                />
              ))
            )}
          </div>
        </div>

        {/* 右侧：执行过程面板 */}
        <div
          style={{
            width: 420,
            borderLeft: '1px solid #f0f0f0',
            overflow: 'hidden',
          }}
        >
          <ExecutionPanel steps={executionSteps} />
        </div>
      </div>

      {/* 下部分：输入区域 */}
      <div
        style={{
          borderTop: '1px solid #f0f0f0',
          background: '#fff',
          padding: '16px 32px 24px',
        }}
      >
        <Sender
          onSubmit={handleSendMessage}
          placeholder="Ask something or upload a file..."
          loading={isExecuting}
        />
      </div>
    </div>
  );
}
