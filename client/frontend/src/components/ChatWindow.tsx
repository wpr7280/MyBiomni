import { useEffect, useState, useRef } from 'react';
import { Button, Dropdown, Tag, Upload, message as antdMessage, Collapse } from 'antd';
import { DownloadOutlined, ExportOutlined, PaperClipOutlined } from '@ant-design/icons';
import { Bubble, Sender, Prompts, Attachments } from '@ant-design/x';
import ExecutionPanel from './ExecutionPanel';
import MarkdownContent from './MarkdownContent';
import { useWebSocket } from '@/hooks/useWebSocket';
import { conversationApi } from '@/api/conversation';
import type { MenuProps } from 'antd';

interface ChatWindowProps {
  conversationId: number;
}

const exampleQuestions = [
  'How do different perturbations affect protein expression?',
  'Help me clone a CRISPR sgRNA into a plasmid.',
  'Identify genetic causes for intellectual disability.',
  'Plan a CRISPR screen for T cell activation.',
];

export default function ChatWindow({ conversationId }: ChatWindowProps) {
  const { messages, setMessages, executionSteps, setExecutionSteps, isExecuting, sendMessage } = useWebSocket(conversationId);
  const [rightPanelWidth, setRightPanelWidth] = useState(420);
  const [isDragging, setIsDragging] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 切换对话时清空执行步骤
    setExecutionSteps([]);
    loadMessages();
  }, [conversationId]);

  async function loadMessages() {
    try {
      const data = await conversationApi.getMessages(conversationId);
      setMessages(data);
      
      // 如果有消息，加载最后一对消息（user + assistant）的执行步骤
      // 执行步骤关联到用户消息
      const messages = data;
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === 'assistant' && i > 0 && messages[i - 1].role === 'user') {
          // 找到最后一对消息，使用用户消息的 ID
          const userMessageId = messages[i - 1].id;
          try {
            const steps = await conversationApi.getExecutionSteps(userMessageId);
            setExecutionSteps(steps);
          } catch (error) {
            console.error('加载执行步骤失败:', error);
          }
          break;
        }
      }
    } catch (error) {
      console.error('加载消息失败:', error);
    }
  }

  async function handleSendMessage(content: string) {
    if (isExecuting) {
      antdMessage.warning('请等待当前问题执行完成');
      return;
    }
    
    try {
      const userMessage = {
        id: Date.now(),
        conversationId,
        role: 'user' as const,
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      
      // 直接通过 WebSocket 发送给 Python Agent
      // Python 会负责：保存用户消息、执行 Agent、保存 AI 消息
      sendMessage(content);
      
      setFileList([]);
      setShowUpload(false);
    } catch (error: any) {
      antdMessage.error(error.message || '发送消息失败');
    }
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;
      const containerRect = containerRef.current.getBoundingClientRect();
      const newWidth = containerRect.right - e.clientX;
      if (newWidth >= 300 && newWidth <= 600) setRightPanelWidth(newWidth);
    };
    const handleMouseUp = () => setIsDragging(false);
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const exportMenuItems: MenuProps['items'] = [
    { key: 'markdown', label: 'Export as Markdown', icon: <ExportOutlined /> },
    { key: 'pdf', label: 'Export as PDF', icon: <DownloadOutlined /> },
  ];

  return (
    <div ref={containerRef} style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#f8f9fa' }}>
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', gap: 1 }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#fff' }}>
          <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px' }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '100px 20px' }}>
                <div style={{ fontSize: 64, marginBottom: 16 }}>💬</div>
                <div style={{ fontSize: 18, color: '#595959', marginBottom: 8, fontWeight: 500 }}>开始新的对话</div>
                <div style={{ fontSize: 14, color: '#8c8c8c' }}>输入您的问题或选择示例问题</div>
              </div>
            ) : (
              messages.map((msg, index) => (
                <Bubble
                  key={msg.id}
                  placement={msg.role === 'user' ? 'end' : 'start'}
                  content={msg.role === 'assistant' ? <MarkdownContent content={msg.content} /> : msg.content}
                  avatar={msg.role === 'assistant' ? { icon: '🤖', style: { background: '#1890ff' } } : { icon: '👤', style: { background: '#52c41a' } }}
                  loading={msg.role === 'assistant' && isExecuting && index === messages.length - 1}
                  style={{ marginBottom: 20 }}
                />
              ))
            )}
          </div>
        </div>

        <div
          onMouseDown={handleMouseDown}
          style={{ width: 5, cursor: 'col-resize', background: isDragging ? '#1890ff' : '#e0e0e0', transition: 'all 0.2s' }}
          onMouseEnter={(e) => !isDragging && (e.currentTarget.style.background = '#bfbfbf')}
          onMouseLeave={(e) => !isDragging && (e.currentTarget.style.background = '#e0e0e0')}
        />

        <div style={{ width: rightPanelWidth, background: '#fff', overflow: 'hidden' }}>
          <ExecutionPanel steps={executionSteps} />
        </div>
      </div>

      <div style={{ background: '#fff', boxShadow: '0 -4px 12px rgba(0,0,0,0.08)' }}>
        <Collapse
          ghost
          items={[{
            key: 'examples',
            label: <div style={{ fontSize: 13, color: '#595959', fontWeight: 500 }}>📝 Example Research Questions</div>,
            children: <Prompts items={exampleQuestions.map((q, i) => ({ key: i.toString(), label: q }))} onItemClick={(info) => handleSendMessage(info.data.label)} />,
          }]}
          style={{ padding: '8px 32px 0', borderBottom: '1px solid #f0f0f0' }}
        />

        <div style={{ padding: '16px 32px' }}>
          {fileList.length > 0 && (
            <div style={{ marginBottom: 12, padding: 12, background: '#f5f7fa', borderRadius: 8, border: '1px solid #e8e8e8' }}>
              <Attachments items={fileList} onChange={setFileList} />
            </div>
          )}
          
          {showUpload && (
            <div style={{ marginBottom: 12 }}>
              <Upload.Dragger beforeUpload={(file) => { setFileList([...fileList, { uid: file.uid, name: file.name, status: 'done' }]); setShowUpload(false); return false; }} fileList={[]} showUploadList={false} style={{ background: '#fafafa', borderColor: '#d9d9d9' }}>
                <div style={{ padding: '20px 0' }}>
                  <PaperClipOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                  <div style={{ marginTop: 8, fontSize: 14, color: '#8c8c8c' }}>Click or drag files to upload</div>
                </div>
              </Upload.Dragger>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ flex: 1 }}>
              <Sender onSubmit={handleSendMessage} placeholder={isExecuting ? "Agent is working..." : "Ask something or upload a file..."} loading={isExecuting} disabled={isExecuting} />
            </div>
            <Button icon={<PaperClipOutlined />} size="large" style={{ height: 40 }} onClick={() => setShowUpload(!showUpload)} disabled={isExecuting}>附件</Button>
          </div>
        </div>

        <div style={{ borderTop: '2px solid #f0f0f0', background: 'linear-gradient(to bottom, #fafafa, #f5f5f5)' }}>
          <div style={{ padding: '14px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Dropdown menu={{ items: exportMenuItems }}>
              <Button type="text" size="small" icon={<DownloadOutlined />} style={{ fontWeight: 500 }}>Export & Download</Button>
            </Dropdown>
            <div style={{ display: 'flex', gap: 10 }}>
              <Tag color="processing" style={{ margin: 0, padding: '4px 12px', fontSize: 12 }}>📊 Weekly: 45/50</Tag>
              <Tag color="success" style={{ margin: 0, padding: '4px 12px', fontSize: 12 }}>📅 Tokens: 2025-06-02</Tag>
            </div>
          </div>

          <div style={{ padding: '10px 32px 14px', borderTop: '1px solid #e8e8e8', display: 'flex', justifyContent: 'center', gap: 16, fontSize: 12 }}>
            <a href="https://github.com/biomni" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c', textDecoration: 'none', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#1890ff'} onMouseLeave={(e) => e.currentTarget.style.color = '#8c8c8c'}>GitHub</a>
            <span style={{ color: '#d9d9d9' }}>•</span>
            <a href="mailto:contact@biomni.com" style={{ color: '#8c8c8c', textDecoration: 'none', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#1890ff'} onMouseLeave={(e) => e.currentTarget.style.color = '#8c8c8c'}>Contact</a>
            <span style={{ color: '#d9d9d9' }}>•</span>
            <a href="https://biomni.com" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c', textDecoration: 'none', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#1890ff'} onMouseLeave={(e) => e.currentTarget.style.color = '#8c8c8c'}>Website</a>
          </div>
        </div>
      </div>
    </div>
  );
}
