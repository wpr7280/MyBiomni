import { Layout, Space, Typography } from 'antd';
import { GithubOutlined, MailOutlined, GlobalOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

export default function Footer() {
  const { t } = useTranslation();
  
  return (
    <AntFooter
      style={{
        background: '#fafafa',
        borderTop: '1px solid #f0f0f0',
        padding: '24px 32px',
        textAlign: 'center',
      }}
    >
      <Space direction="vertical" size={12} style={{ width: '100%' }}>
        {/* 链接 */}
        <Space size={24}>
          <Link href="https://github.com/biomni" target="_blank">
            <GithubOutlined style={{ fontSize: 16 }} /> {t('footer.github')}
          </Link>
          <Link href="mailto:peirongw@foxmail.com">
            <MailOutlined style={{ fontSize: 16 }} /> {t('footer.contact')}
          </Link>
          <Link href="https://warphelix.com" target="_blank">
            <GlobalOutlined style={{ fontSize: 16 }} /> {t('footer.website')}
          </Link>
        </Space>

        {/* 版权信息 */}
        <Text type="secondary" style={{ fontSize: 12 }}>
          {t('footer.copyright')}
        </Text>

        {/* 描述 */}
        <Text type="secondary" style={{ fontSize: 12 }}>
          {t('footer.description')}
        </Text>
      </Space>
    </AntFooter>
  );
}
