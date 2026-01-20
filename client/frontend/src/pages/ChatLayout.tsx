import { useState, useEffect } from 'react';
import { Layout, message, Button, Modal, Input } from 'antd';
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
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [renamingId, setRenamingId] = useState<number | null>(null);
  const [newTitle, setNewTitle] = useState('');

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
      console.log('创建的对话:', newConversation);
      
      if (newConversation && newConversation.id) {
        setConversations((prev) => [newConversation, ...prev]);
        setActiveConversationId(newConversation.id);
        message.success('创建成功');
      } else {
        console.error('对话数据无效:', newConversation);
        message.error('创建失败：数据无效');
      }
    } catch (error: any) {
      console.error('创建对话失败:', error);
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

  // 重命名对话
  function showRenameModal(id: number) {
    const conversation = conversations.find((c) => c.id === id);
    if (conversation) {
      setRenamingId(id);
      setNewTitle(conversation.title);
      setRenameModalOpen(true);
    }
  }

  async function handleRename() {
    if (!renamingId || !newTitle.trim()) {
      message.error('请输入对话标题');
      return;
    }

    try {
      // 调用后端 API 更新标题
      await conversationApi.updateConversation(renamingId, newTitle);
      
      // 更新本地状态
      setConversations((prev) =>
        prev.map((c) => (c.id === renamingId ? { ...c, title: newTitle } : c))
      );
      
      setRenameModalOpen(false);
      message.success('重命名成功');
    } catch (error: any) {
      message.error(error.message || '重命名失败');
    }
  }

  // 转换为 Ant Design X Conversations 组件需要的格式
  const conversationItems = conversations
    .filter((conv) => conv && conv.id)  // 过滤掉无效数据
    .map((conv) => ({
      key: conv.id.toString(),
      label: conv.title || '新对话',
      timestamp: conv.updatedAt ? new Date(conv.updatedAt).getTime() : Date.now(),
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
          {/* 新建对话按钮 */}
          <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
            <Button
              type="primary"
              block
              icon={<span style={{ fontSize: 16 }}>➕</span>}
              onClick={handleCreateConversation}
              size="large"
            >
              新建对话
            </Button>
          </div>
          
          <Conversations
            items={conversationItems}
            activeKey={activeConversationId?.toString()}
            onActiveChange={(key) => setActiveConversationId(Number(key))}
            menu={{
              items: [
                {
                  label: '重命名',
                  key: 'rename',
                },
                {
                  label: '删除',
                  key: 'delete',
                  danger: true,
                },
              ],
              onClick: (menuInfo, itemInfo) => {
                console.log('菜单点击:', menuInfo, itemInfo);
                if (!menuInfo || !menuInfo.key) return;
                
                // 从 itemInfo 或 menuInfo 中获取对话 ID
                const conversationKey = itemInfo?.key || activeConversationId?.toString();
                if (!conversationKey) return;
                
                const id = Number(conversationKey);
                
                if (menuInfo.key === 'rename') {
                  showRenameModal(id);
                } else if (menuInfo.key === 'delete') {
                  handleDeleteConversation(id);
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

      {/* 重命名对话弹窗 */}
      <Modal
        title="重命名对话"
        open={renameModalOpen}
        onOk={handleRename}
        onCancel={() => setRenameModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Input
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="请输入对话标题"
          onPressEnter={handleRename}
          autoFocus
        />
      </Modal>
    </Layout>
  );
}
