import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { MailOutlined, LockOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

const { Title, Text } = Typography;

export default function Login() {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const { token, user } = await authApi.login(values);
      setAuth(token, user);
      
      // 检查是否需要强制修改密码
      const response = await authApi.getCurrentUser();
      if ((response as any).forcePasswordChange) {
        message.warning(t('login.forcePasswordChange'));
        navigate('/change-password');
      } else {
        message.success(t('login.loginSuccess', { username: user.username }));
        navigate('/');
      }
    } catch (error: any) {
      message.error(error.message || t('login.loginFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      {/* 左侧：介绍区域 */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 60,
          color: '#fff',
        }}
      >
        <div
          style={{
            width: 120,
            height: 120,
            borderRadius: 24,
            background: 'rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 64,
            marginBottom: 32,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          }}
        >
          🧬
        </div>
        <Title level={1} style={{ color: '#fff', marginBottom: 16, fontSize: 48 }}>
          {t('login.appTitle')}
        </Title>
        <Title level={3} style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 400, marginBottom: 32 }}>
          {t('login.appSubtitle')}
        </Title>
        <div style={{ maxWidth: 500, textAlign: 'center', lineHeight: 1.8 }}>
          <Text style={{ color: 'rgba(255, 255, 255, 0.85)', fontSize: 16 }}>
            {t('login.appDescription')}
          </Text>
        </div>
        <div
          style={{
            marginTop: 48,
            display: 'flex',
            gap: 40,
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: 14,
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>🔬</div>
            <div>{t('login.feature1')}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📊</div>
            <div>{t('login.feature2')}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📚</div>
            <div>{t('login.feature3')}</div>
          </div>
        </div>
      </div>

      {/* 右侧：登录表单 */}
      <div
        style={{
          width: 500,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#fff',
          padding: 60,
        }}
      >
        <div style={{ width: '100%', maxWidth: 400 }}>
          <div style={{ marginBottom: 40, textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              欢迎回来
            </Title>
            <Text type="secondary">登录您的 Biomni 账户</Text>
          </div>

          <Form name="login" onFinish={onFinish} autoComplete="off" size="large">
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="邮箱地址" />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="密码" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block size="large">
                登录
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              登录即表示您同意我们的{' '}
              <a href="#" style={{ color: '#1890ff' }}>
                服务条款
              </a>{' '}
              和{' '}
              <a href="#" style={{ color: '#1890ff' }}>
                隐私政策
              </a>
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
}
