import { Dropdown, Button } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { MenuProps } from 'antd';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
    // 刷新页面以更新 Ant Design 的语言包
    window.location.reload();
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'zh-CN',
      label: '简体中文',
      onClick: () => handleLanguageChange('zh-CN'),
    },
    {
      key: 'en-US',
      label: 'English',
      onClick: () => handleLanguageChange('en-US'),
    },
  ];

  const currentLanguage = i18n.language === 'en-US' ? 'EN' : '中文';

  return (
    <Dropdown menu={{ items: menuItems }} placement="bottomRight">
      <Button
        type="text"
        icon={<GlobalOutlined />}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 4,
        }}
      >
        {currentLanguage}
      </Button>
    </Dropdown>
  );
}
