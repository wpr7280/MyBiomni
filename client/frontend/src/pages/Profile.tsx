import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Typography, Divider, Space, Avatar } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

const { Title, Text } = Typography;

export default function Profile() {
  const { user, setAuth } = useAuthStore();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [passwordForm] = Form.useForm();
  const [infoForm] = Form.useForm();

  useEffect(() => {
    if (user) {
      infoForm.setFieldsValue({
        username: user.username,
        email: user.email,
      });
    }
  }, [user, infoForm]);

  // 更新用户信息
  const handleUpdateInfo = async (values: { username: string; email: string }) => {
    setLoading(true);
    try {
      await authApi.updateUserInfo(values.username, values.email);
      
      // 更新本地用户信息
      if (user) {
        const token = localStorage.getItem('token')!;
        setAuth(token, { ...user, username: values.username, email: values.email });
      }
      
      message.success(t('profile.infoUpdateSuccess'));
    } catch (error: any) {
      message.error(error.message || t('profile.infoUpdateFailed'));
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const handleChangePassword = async (values: { oldPassword: string; newPassword: string }) => {
    setLoading(true);
    try {
      await authApi.updatePassword(values.oldPassword, values.newPassword);
      message.success(t('profile.passwordUpdateSuccess'));
      
      // 清除登录状态
      localStorage.clear();
      window.location.href = '/login';
    } catch (error: any) {
      message.error(error.message || t('profile.passwordUpdateFailed'));
    } finally {
      setLoading(false);
    }
  };

  const getRoleText = (role: string) => {
    if (role === 'super_admin') return t('profile.roleSuperAdmin');
    if (role === 'admin') return t('profile.roleAdmin');
    return t('profile.roleUser');
  };

  return (
    <div
      style={{
        padding: 24,
        maxWidth: 1200,
        margin: '0 auto',
      }}
    >
      <Title level={2} style={{ marginBottom: 24 }}>
        {t('profile.title')}
      </Title>

      <div style={{ display: 'flex', gap: 24 }}>
        {/* 左侧：用户信息卡片 */}
        <Card
          style={{ width: 320 }}
          styles={{ body: { textAlign: 'center', padding: 32 } }}
        >
          <Avatar
            size={100}
            icon={<UserOutlined />}
            src={user?.avatar}
            style={{ marginBottom: 16, background: '#1890ff' }}
          />
          <Title level={4} style={{ marginBottom: 8 }}>
            {user?.username}
          </Title>
          <Text type="secondary">{user?.email}</Text>
          <Divider />
          <Space direction="vertical" size={8} style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary">{t('profile.role')}</Text>
              <Text>
                {user?.role && getRoleText(user.role)}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary">{t('profile.userId')}</Text>
              <Text>{user?.id}</Text>
            </div>
          </Space>
        </Card>

        {/* 右侧：表单区域 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* 基本信息 */}
          <Card title={t('profile.basicInfo')}>
            <Form
              form={infoForm}
              layout="vertical"
              onFinish={handleUpdateInfo}
              autoComplete="off"
            >
              <Form.Item
                label={t('profile.username')}
                name="username"
                rules={[{ required: true, message: t('profile.usernameRequired') }]}
              >
                <Input prefix={<UserOutlined />} placeholder={t('profile.usernamePlaceholder')} />
              </Form.Item>

              <Form.Item
                label={t('profile.email')}
                name="email"
                rules={[
                  { required: true, message: t('profile.emailRequired') },
                  { type: 'email', message: t('profile.emailInvalid') },
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder={t('profile.emailPlaceholder')} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  {t('profile.saveButton')}
                </Button>
              </Form.Item>
            </Form>
          </Card>

          {/* 修改密码 */}
          <Card title={t('profile.changePassword')}>
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handleChangePassword}
              autoComplete="off"
            >
              <Form.Item
                label={t('profile.currentPassword')}
                name="oldPassword"
                rules={[{ required: true, message: t('profile.currentPasswordRequired') }]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder={t('profile.currentPasswordPlaceholder')} />
              </Form.Item>

              <Form.Item
                label={t('profile.newPassword')}
                name="newPassword"
                rules={[
                  { required: true, message: t('profile.newPasswordRequired') },
                  { min: 8, message: t('profile.passwordMinLength') },
                  {
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                    message: t('profile.passwordPattern'),
                  },
                ]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder={t('profile.newPasswordPlaceholder')} />
              </Form.Item>

              <Form.Item
                label={t('profile.confirmPassword')}
                name="confirmPassword"
                dependencies={['newPassword']}
                rules={[
                  { required: true, message: t('profile.confirmPasswordRequired') },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('newPassword') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error(t('profile.passwordsNotMatch')));
                    },
                  }),
                ]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder={t('profile.confirmPasswordPlaceholder')} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  {t('profile.changePasswordButton')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>
      </div>
    </div>
  );
}
