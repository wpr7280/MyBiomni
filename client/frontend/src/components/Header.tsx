import { Layout, Button, Dropdown, Avatar, Space } from 'antd';
import {
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/api/auth';
import LanguageSwitcher from './LanguageSwitcher';
import type { MenuProps } from 'antd';

const { Header: AntHeader } = Layout;

interface HeaderProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Header({ collapsed, onToggle }: HeaderProps) {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();
  const { t } = useTranslation();

  const handleLogout = async () => {
    try {
      await authApi.logout();
      clearAuth();
      navigate('/login');
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  const getRoleText = (role: string) => {
    if (role === 'super_admin') return t('profile.roleSuperAdmin');
    if (role === 'admin') return t('profile.roleAdmin');
    return t('profile.roleUser');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('header.profile'),
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('header.logout'),
      danger: true,
      onClick: handleLogout,
    },
  ];

  return (
    <AntHeader
      style={{
        background: '#fff',
        padding: '0 32px',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 64,
        boxShadow: '0 1px 4px rgba(0,0,0,0.02)',
      }}
    >
      {/* 左侧：折叠按钮 + Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={onToggle}
          style={{
            fontSize: 18,
            width: 40,
            height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 22,
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)',
            }}
          >
            🧬
          </div>
          <div style={{ lineHeight: 1.2 }}>
            <div
              style={{
                fontSize: 20,
                fontWeight: 600,
                color: '#262626',
                letterSpacing: '-0.5px',
              }}
            >
              {t('header.appTitle')}
            </div>
            <div
              style={{
                fontSize: 11,
                color: '#8c8c8c',
                marginTop: 2,
                fontWeight: 400,
              }}
            >
              {t('header.appSubtitle')}
            </div>
          </div>
        </div>
      </div>

      {/* 右侧：语言切换 + 用户信息 */}
      <Space size={16}>
        <LanguageSwitcher />
        
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              cursor: 'pointer',
              padding: '6px 12px',
              borderRadius: 8,
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#fafafa';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <Avatar
              size={36}
              style={{ background: '#1890ff' }}
              icon={<UserOutlined />}
              src={user?.avatar}
            />
            <div style={{ lineHeight: 1.3 }}>
              <div style={{ fontSize: 14, fontWeight: 500, color: '#262626' }}>
                {user?.username}
              </div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                {user?.role && getRoleText(user.role)}
              </div>
            </div>
          </div>
        </Dropdown>
      </Space>
    </AntHeader>
  );
}
