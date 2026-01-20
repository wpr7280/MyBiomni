import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin, message } from 'antd';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

export default function SSOLogin() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      message.error('缺少 Token');
      navigate('/login');
      return;
    }

    verifyAndSaveToken(token);
  }, [searchParams, navigate, setAuth]);

  async function verifyAndSaveToken(token: string) {
    try {
      // 验证 Token
      const user = await authApi.getCurrentUser();

      // Token 有效，保存
      setAuth(token, user);

      // 清除 URL 中的 Token
      window.history.replaceState({}, document.title, '/');

      // 跳转到首页
      message.success(`欢迎，${user.username}！`);
      navigate('/');
    } catch (error: any) {
      message.error('Token 无效或已过期，请重新登录');
      navigate('/login');
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
      }}
    >
      <Spin size="large" />
      <p style={{ marginTop: 20, fontSize: 16 }}>正在登录...</p>
    </div>
  );
}
