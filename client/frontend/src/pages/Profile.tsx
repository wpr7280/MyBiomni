import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Typography, Divider, Space, Avatar } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

const { Title, Text } = Typography;

export default function Profile() {
  const { user, setAuth } = useAuthStore();
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
      
      message.success('信息更新成功');
    } catch (error: any) {
      message.error(error.message || '更新失败');
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const handleChangePassword = async (values: { oldPassword: string; newPassword: string }) => {
    setLoading(true);
    try {
      await authApi.updatePassword(values.oldPassword, values.newPassword);
      message.success('密码修改成功，请重新登录');
      
      // 清除登录状态
      localStorage.clear();
      window.location.href = '/login';
    } catch (error: any) {
      message.error(error.message || '密码修改失败');
    } finally {
      setLoading(false);
    }
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
        个人中心
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
              <Text type="secondary">角色</Text>
              <Text>
                {user?.role === 'super_admin'
                  ? '超级管理员'
                  : user?.role === 'admin'
                  ? '管理员'
                  : '用户'}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary">用户 ID</Text>
              <Text>{user?.id}</Text>
            </div>
          </Space>
        </Card>

        {/* 右侧：表单区域 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* 基本信息 */}
          <Card title="基本信息">
            <Form
              form={infoForm}
              layout="vertical"
              onFinish={handleUpdateInfo}
              autoComplete="off"
            >
              <Form.Item
                label="用户名"
                name="username"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input prefix={<UserOutlined />} placeholder="用户名" />
              </Form.Item>

              <Form.Item
                label="邮箱"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' },
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="邮箱地址" />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  保存修改
                </Button>
              </Form.Item>
            </Form>
          </Card>

          {/* 修改密码 */}
          <Card title="修改密码">
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handleChangePassword}
              autoComplete="off"
            >
              <Form.Item
                label="当前密码"
                name="oldPassword"
                rules={[{ required: true, message: '请输入当前密码' }]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder="当前密码" />
              </Form.Item>

              <Form.Item
                label="新密码"
                name="newPassword"
                rules={[
                  { required: true, message: '请输入新密码' },
                  { min: 8, message: '密码长度至少 8 位' },
                  {
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                    message: '密码必须包含大小写字母和数字',
                  },
                ]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder="新密码" />
              </Form.Item>

              <Form.Item
                label="确认新密码"
                name="confirmPassword"
                dependencies={['newPassword']}
                rules={[
                  { required: true, message: '请确认新密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('newPassword') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'));
                    },
                  }),
                ]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder="确认新密码" />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  修改密码
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>
      </div>
    </div>
  );
}
