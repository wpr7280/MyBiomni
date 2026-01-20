import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import './index.css';

// Mock 模式提示
if (import.meta.env.VITE_USE_MOCK === 'true') {
  console.log(
    '%c🎭 Mock 模式已启用',
    'background: #722ed1; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
  );
  console.log('测试账号: user@biomni.com / user123');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);
