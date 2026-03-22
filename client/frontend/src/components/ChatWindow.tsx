import { useEffect, useState, useRef } from 'react';
import { Button, Dropdown, Tag, Upload, message as antdMessage, Collapse } from 'antd';
import { DownloadOutlined, ExportOutlined, PaperClipOutlined } from '@ant-design/icons';
import { Bubble, Sender, Prompts, Attachments } from '@ant-design/x';
import { useTranslation } from 'react-i18next';
import ExecutionPanel from './ExecutionPanel';
import MarkdownContent from './MarkdownContent';
import { useWebSocket } from '@/hooks/useWebSocket';
import { conversationApi } from '@/api/conversation';
import { uploadAttachment } from '@/api/upload';
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
  const { t } = useTranslation();
  const { messages, setMessages, executionSteps, setExecutionSteps, isExecuting, sendMessage } = useWebSocket(conversationId);
  const [rightPanelWidth, setRightPanelWidth] = useState(750);  // Executor 默认更宽
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
      
      // Load execution steps for the last assistant message
      const messages = data;
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === 'assistant') {
          try {
            const steps = await conversationApi.getExecutionSteps(messages[i].id);
            if (steps && steps.length > 0) {
              setExecutionSteps(steps);
            }
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
      antdMessage.warning(t('chat.waitingExecution'));
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
      
      // 添加用户消息
      setMessages((prev) => [...prev, userMessage]);
      
      // 添加临时的"正在思考"消息
      const thinkingMessage = {
        id: Date.now() + 1,
        conversationId,
        role: 'assistant' as const,
        content: '🤔 Thinking...',
        createdAt: new Date().toISOString(),
        isTemporary: true,  // 标记为临时消息
      };
      setMessages((prev) => [...prev, thinkingMessage]);
      
      let uploadedFileIds: number[] = [];
      if (fileList.length > 0) {
        const uploads = await Promise.all(
          fileList.map((file: any) => {
            const originFile = file.originFileObj || file;
            return uploadAttachment(conversationId, originFile);
          })
        );
        uploadedFileIds = uploads.map((item) => item.id);
      }

      // 直接通过 WebSocket 发送给 Python Agent
      // Python 会负责：保存用户消息、执行 Agent、保存 AI 消息
      sendMessage(content, uploadedFileIds);
      
      setFileList([]);
      setShowUpload(false);
    } catch (error: any) {
      antdMessage.error(error.message || t('chat.sendFailed'));
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
      const newWidth = containerRect.right - e.clientX;  // 从右边计算
      // 调整范围：400-800
      if (newWidth >= 400 && newWidth <= 800) setRightPanelWidth(newWidth);
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
    { 
      key: 'markdown', 
      label: t('chat.exportMarkdown'), 
      icon: <DownloadOutlined />,
      onClick: async () => {
        try {
          antdMessage.loading({ content: t('chat.exporting'), key: 'export' });
          await conversationApi.exportConversation(conversationId, true);
          antdMessage.success({ content: t('chat.exportSuccess'), key: 'export', duration: 2 });
        } catch (error: any) {
          antdMessage.error({ content: error.message || t('chat.exportFailed'), key: 'export', duration: 3 });
        }
      }
    },
  ];

  return (
    <div ref={containerRef} style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#f8f9fa' }}>
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', gap: 1 }}>
        {/* 左侧 Chat 面板 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#fff' }}>
          <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px' }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '100px 20px' }}>
                <div style={{ fontSize: 64, marginBottom: 16 }}>💬</div>
                <div style={{ fontSize: 18, color: '#595959', marginBottom: 8, fontWeight: 500 }}>{t('chat.emptyTitle')}</div>
                <div style={{ fontSize: 14, color: '#8c8c8c' }}>{t('chat.emptySubtitle')}</div>
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

        {/* 拖动分隔条 */}
        <div
          onMouseDown={handleMouseDown}
          style={{ width: 5, cursor: 'col-resize', background: isDragging ? '#1890ff' : '#e0e0e0', transition: 'all 0.2s' }}
          onMouseEnter={(e) => !isDragging && (e.currentTarget.style.background = '#bfbfbf')}
          onMouseLeave={(e) => !isDragging && (e.currentTarget.style.background = '#e0e0e0')}
        />

        {/* 右侧 Executor 面板 */}
        <div style={{ width: rightPanelWidth, background: '#fff', overflow: 'hidden' }}>
          <ExecutionPanel steps={executionSteps} />
        </div>
      </div>

      <div style={{ background: '#fff', boxShadow: '0 -4px 12px rgba(0,0,0,0.08)' }}>
        <Collapse
          ghost
          items={[{
            key: 'examples',
            label: <div style={{ fontSize: 13, color: '#595959', fontWeight: 500 }}>{t('chat.exampleQuestionsTitle')}</div>,
            children: <Prompts items={exampleQuestions.map((q, i) => ({ key: i.toString(), label: q }))} onItemClick={(info) => handleSendMessage(info.data.label as string)} />,
          }]}
          style={{ padding: '8px 32px 0', borderBottom: '1px solid #f0f0f0' }}
        />

        <div style={{ padding: '16px 32px' }}>
          {fileList.length > 0 && (
            <div style={{ marginBottom: 12, padding: 12, background: '#f5f7fa', borderRadius: 8, border: '1px solid #e8e8e8' }}>
              <Attachments items={fileList} onChange={(info) => setFileList(info.fileList)} />
            </div>
          )}
          
          {showUpload && (
            <div style={{ marginBottom: 12 }}>
              <Upload.Dragger beforeUpload={(file) => { setFileList([...fileList, { uid: file.uid, name: file.name, status: 'done', originFileObj: file }]); setShowUpload(false); return false; }} fileList={[]} showUploadList={false} style={{ background: '#fafafa', borderColor: '#d9d9d9' }}>
                <div style={{ padding: '20px 0' }}>
                  <PaperClipOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                  <div style={{ marginTop: 8, fontSize: 14, color: '#8c8c8c' }}>{t('chat.uploadHint')}</div>
                </div>
              </Upload.Dragger>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ flex: 1 }}>
              <Sender onSubmit={handleSendMessage} placeholder={isExecuting ? t('chat.inputPlaceholderExecuting') : t('chat.inputPlaceholder')} loading={isExecuting} disabled={isExecuting} />
            </div>
            <Button icon={<PaperClipOutlined />} size="large" style={{ height: 40 }} onClick={() => setShowUpload(!showUpload)} disabled={isExecuting}>{t('chat.attachButton')}</Button>
          </div>
        </div>

        <div style={{ borderTop: '2px solid #f0f0f0', background: 'linear-gradient(to bottom, #fafafa, #f5f5f5)' }}>
          <div style={{ padding: '14px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Dropdown menu={{ items: exportMenuItems }}>
              <Button type="text" size="small" icon={<DownloadOutlined />} style={{ fontWeight: 500 }}>{t('chat.exportDownload')}</Button>
            </Dropdown>
            <div style={{ display: 'flex', gap: 10 }}>
              <Tag color="processing" style={{ margin: 0, padding: '4px 12px', fontSize: 12 }}>{t('chat.weeklyQuota', { used: 45, total: 50 })}</Tag>
              <Tag color="success" style={{ margin: 0, padding: '4px 12px', fontSize: 12 }}>{t('chat.tokensExpiry', { date: '2025-06-02' })}</Tag>
            </div>
          </div>

          <div style={{ padding: '10px 32px 14px', borderTop: '1px solid #e8e8e8', display: 'flex', justifyContent: 'center', gap: 16, fontSize: 12 }}>
            <a href="https://biomni.com/contact" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c', textDecoration: 'none', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#1890ff'} onMouseLeave={(e) => e.currentTarget.style.color = '#8c8c8c'}>{t('footer.contact')}</a>
            <span style={{ color: '#d9d9d9' }}>•</span>
            <a href="https://biomni.com/" target="_blank" rel="noopener noreferrer" style={{ color: '#8c8c8c', textDecoration: 'none', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#1890ff'} onMouseLeave={(e) => e.currentTarget.style.color = '#8c8c8c'}>{t('footer.website')}</a>
          </div>
        </div>
      </div>
    </div>
  );
}
