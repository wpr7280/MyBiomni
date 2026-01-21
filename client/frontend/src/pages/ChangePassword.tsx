import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography, Alert } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { authApi } from '@/api/auth';

const { Title, Text } = Typography;

export default function ChangePassword() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const onFinish = async (values: { oldPassword: string; newPassword: string }) => {
    setLoading(true);
    try {
      await authApi.updatePassword(values.oldPassword, values.newPassword);
      message.success(t('changePassword.success'));
      
      // 清除登录状态
      localStorage.clear();
      navigate('/login');
    } catch (error: any) {
      message.error(error.message || t('changePassword.failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 480,
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 12,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 32,
              marginBottom: 16,
            }}
          >
            🔐
          </div>
          <Title level={3} style={{ marginBottom: 8 }}>
            {t('changePassword.title')}
          </Title>
          <Text type="secondary">{t('changePassword.subtitle')}</Text>
        </div>

        <Alert
          message={t('changePassword.requirementsTitle')}
          description={t('changePassword.requirementsDesc')}
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form form={form} name="changePassword" onFinish={onFinish} autoComplete="off" size="large">
          <Form.Item
            name="oldPassword"
            rules={[{ required: true, message: t('changePassword.oldPasswordRequired') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('changePassword.oldPasswordPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="newPassword"
            rules={[
              { required: true, message: t('changePassword.newPasswordRequired') },
              { min: 8, message: t('changePassword.passwordMinLength') },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                message: t('changePassword.passwordPattern'),
              },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('changePassword.newPasswordPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['newPassword']}
            rules={[
              { required: true, message: t('changePassword.confirmPasswordRequired') },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('newPassword') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error(t('changePassword.passwordsNotMatch')));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('changePassword.confirmPasswordPlaceholder')} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              {t('changePassword.submitButton')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
