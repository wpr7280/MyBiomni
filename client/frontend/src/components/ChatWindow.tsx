import { useEffect, useState, useRef } from 'react';
import { Button, Dropdown, Tag, Upload, message as antdMessage } from 'antd';
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
  'I have a plasmid sequence. Help me clone a CRISPR sgRNA.',
  'Identify potential genetic causes for intellectual disability.',
  'Plan a CRISPR screen of 100 genes for T cell activation.',
  'Research the genetic mechanism of rs6690215',
];

export default function ChatWindow({ conversationId }: ChatWindowProps) {
  const { messages, setMessages, executionSteps, isExecuting, sendMessage } = useWebSocket(conversationId);
  const [showExamples, setShowExamples] = useState(false);
  const [rightPanelWidth, setRightPanelWidth] = useState(420);
  const [isDragging, setIsDragging] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
  }, [conversationId]);

  async function loadMessages() {
    try {
      const data = await conversationApi.getMessages(conversationId);
      setMessages(data);
      setShowExamples(data.length === 0);
    } catch (error) {
      console.error('加载消息失败:', error);
    }
  }

  async function handleSendMessage(content: string) {
    // 如果正在执行，不允许提交
    if (isExecuting) {
      antdMessage.warning('请等待当前问题执行完成');
      return;
    }
    
    try {
      setShowExamples(false);
      
      // 1. 立即添加用户消息到界面
      const userMessage = {
        id: Date.now(),
        conversationId,
        role: 'user' as const,
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      
      // 2. 调用 API 保存消息
      await conversationApi.sendMessage(conversationId, content);
      
      // 3. 通过 WebSocket 发送给 Agent 执行
      sendMessage(content);
      
      // 4. 清空文件列表和关闭上传区域
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
      if (newWidth >= 300 && newWidth <= 600) {
        setRightPanelWidth(newWidth);
      }
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
    <div ref={containerRef} style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#fff' }}>
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px', background: '#fafafa' }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '100px 20px', color: '#bfbfbf' }}>
                <div style={{ fontSize: 64, marginBottom: 16 }}>💬</div>
                <div style={{ fontSize: 18, color: '#8c8c8c', marginBottom: 8 }}>开始新的对话</div>
                <div style={{ fontSize: 14, color: '#bfbfbf' }}>输入您的问题或选择下方的示例问题</div>
              </div>
            ) : (
              messages.map((msg) => (
                <Bubble
                  key={msg.id}
                  placement={msg.role === 'user' ? 'end' : 'start'}
                  content={msg.role === 'assistant' ? <MarkdownContent content={msg.content} /> : msg.content}
                  avatar={msg.role === 'assistant' ? { icon: '🤖', style: { background: '#1890ff' } } : { icon: '👤', style: { background: '#52c41a' } }}
                  loading={msg.role === 'assistant' && isExecuting}
                  style={{ marginBottom: 20 }}
                />
              ))
            )}
          </div>
        </div>

        <div
          onMouseDown={handleMouseDown}
          style={{ width: 4, cursor: 'col-resize', background: isDragging ? '#1890ff' : 'transparent', transition: 'background 0.2s', position: 'relative' }}
          onMouseEnter={(e) => !isDragging && (e.currentTarget.style.background = '#f0f0f0')}
          onMouseLeave={(e) => !isDragging && (e.currentTarget.style.background = 'transparent')}
        >
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 20, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.3 }}>⋮</div>
        </div>

        <div style={{ width: rightPanelWidth, borderLeft: '1px solid #f0f0f0', overflow: 'hidden' }}>
          <ExecutionPanel steps={executionSteps} />
        </div>
      </div>

      <div style={{ borderTop: '1px solid #f0f0f0', background: '#fff' }}>
        {/* 示例问题行 - 始终显示 */}
        <div style={{ padding: '16px 32px', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ marginBottom: 12, fontSize: 13, color: '#8c8c8c', fontWeight: 500 }}>📝 Example Research Questions</div>
          <Prompts 
            items={exampleQuestions.map((q, i) => ({ key: i.toString(), label: q }))} 
            onItemClick={(info) => {
              console.log('点击了示例问题:', info);
              handleSendMessage(info.data.label);
            }} 
          />
        </div>

        {/* 输入框 */}
        <div style={{ padding: '16px 32px' }}>
          {/* 附件列表（有文件时显示） */}
          {fileList.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <Attachments items={fileList} onChange={setFileList} />
            </div>
          )}
          
          {/* 上传区域（点击附件按钮后显示） */}
          {showUpload && (
            <div style={{ marginBottom: 12 }}>
              <Upload.Dragger
                beforeUpload={(file) => {
                  setFileList([...fileList, {
                    uid: file.uid,
                    name: file.name,
                    status: 'done',
                  }]);
                  setShowUpload(false);
                  return false;
                }}
                fileList={[]}
                showUploadList={false}
              >
                <div style={{ padding: '20px 0' }}>
                  <PaperClipOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                  <div style={{ marginTop: 8, fontSize: 14, color: '#8c8c8c' }}>
                    Click or drag files to upload
                  </div>
                </div>
              </Upload.Dragger>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <Sender 
                onSubmit={handleSendMessage} 
                placeholder={isExecuting ? "Agent is working..." : "Ask something or upload a file..."} 
                loading={isExecuting}
                disabled={isExecuting}
              />
            </div>
            <Button 
              icon={<PaperClipOutlined />} 
              size="large"
              style={{ height: 40 }}
              onClick={() => setShowUpload(!showUpload)}
              disabled={isExecuting}
            >
              附件
            </Button>
          </div>
        </div>

        {/* 底部操作栏 - 两行布局 */}
        <div style={{ borderTop: '1px solid #f0f0f0', background: '#fafafa' }}>
          {/* 第一行：Export + 配额 */}
          <div style={{ padding: '12px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Dropdown menu={{ items: exportMenuItems }}>
              <Button type="text" size="small" icon={<DownloadOutlined />}>Export & Download</Button>
            </Dropdown>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Tag color="default" style={{ margin: 0 }}>Weekly: 45/50</Tag>
              <Tag color="default" style={{ margin: 0 }}>Tokens: 2025-06-02</Tag>
            </div>
          </div>

          {/* 第二行：链接 */}
          <div style={{ padding: '8px 32px 12px', borderTop: '1px solid #f0f0f0', display: 'flex', justifyContent: 'center', gap: 12, fontSize: 12 }}>
            <a href="https://github.com/biomni" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c' }}>GitHub</a>
            <span style={{ color: '#d9d9d9' }}>|</span>
            <a href="mailto:contact@biomni.com" style={{ color: '#8c8c8c' }}>Contact</a>
            <span style={{ color: '#d9d9d9' }}>|</span>
            <a href="https://biomni.com" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c' }}>Website</a>
          </div>
        </div>
      </div>
    </div>
  );
}
