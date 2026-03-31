import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import enUS from 'antd/locale/en_US';
import App from './App';
import './index.css';
import './i18n';

// 获取当前语言设置
const currentLanguage = localStorage.getItem('language') || 'en-US';
const antdLocale = currentLanguage === 'en-US' ? enUS : zhCN;

// Mock mode notice
if (import.meta.env.VITE_USE_MOCK === 'true') {
  console.log(
    '%c🎭 Mock mode enabled',
    'background: #722ed1; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
  );
  console.log('Test account: user@warphelix.com / user123');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider locale={antdLocale}>
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);
