import { useState, useEffect } from 'react';
import { Layout, message } from 'antd';
import { Conversations } from '@ant-design/x';
import Header from '@/components/Header';
import ChatWindow from '@/components/ChatWindow';
import { conversationApi } from '@/api/conversation';
import type { Conversation } from '@/types';

const { Sider, Content } = Layout;

export default function ChatLayout() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  // 加载对话列表
  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    setLoading(true);
    try {
      const data = await conversationApi.getConversations();
      setConversations(data);
      
      // 如果有对话，默认选中第一个
      if (data.length > 0 && !activeConversationId) {
        setActiveConversationId(data[0].id);
      }
    } catch (error: any) {
      message.error(error.message || '加载对话列表失败');
    } finally {
      setLoading(false);
    }
  }

  // 创建新对话
  async function handleCreateConversation() {
    try {
      const newConversation = await conversationApi.createConversation();
      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversationId(newConversation.id);
      message.success('创建成功');
    } catch (error: any) {
      message.error(error.message || '创建失败');
    }
  }

  // 删除对话
  async function handleDeleteConversation(id: number) {
    try {
      await conversationApi.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      
      // 如果删除的是当前对话，切换到第一个
      if (id === activeConversationId) {
        const remaining = conversations.filter((c) => c.id !== id);
        setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
      }
      
      message.success('删除成功');
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  }

  // 转换为 Ant Design X Conversations 组件需要的格式
  const conversationItems = conversations.map((conv) => ({
    key: conv.id.toString(),
    label: conv.title,
    timestamp: new Date(conv.updatedAt).getTime(),
  }));

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 头部导航栏 */}
      <Header collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <Layout style={{ flex: 1, overflow: 'hidden' }}>
        {/* 左侧对话列表（可折叠） */}
        <Sider
          width={280}
          collapsedWidth={0}
          collapsed={collapsed}
          theme="light"
          style={{
            borderRight: '1px solid #f0f0f0',
            transition: 'all 0.2s',
          }}
        >
          <Conversations
            items={conversationItems}
            activeKey={activeConversationId?.toString()}
            onActiveChange={(key) => setActiveConversationId(Number(key))}
            creation={{
              onSubmit: handleCreateConversation,
            }}
            menu={{
              items: [
                {
                  label: '删除',
                  key: 'delete',
                  danger: true,
                },
              ],
              onClick: (menuInfo, itemInfo) => {
                if (menuInfo.key === 'delete') {
                  handleDeleteConversation(Number(itemInfo.key));
                }
              },
            }}
          />
        </Sider>

        {/* 主内容区域 */}
        <Content style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {activeConversationId ? (
            <ChatWindow conversationId={activeConversationId} />
          ) : (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                color: '#bfbfbf',
              }}
            >
              <div style={{ fontSize: 64, marginBottom: 16 }}>🧬</div>
              <div style={{ fontSize: 18, color: '#8c8c8c', marginBottom: 8 }}>
                欢迎使用 Biomni AI 助手
              </div>
              <div style={{ fontSize: 14, color: '#bfbfbf' }}>
                请选择或创建一个对话开始
              </div>
            </div>
          )}
        </Content>
      </Layout>
    </Layout>
  );
}
