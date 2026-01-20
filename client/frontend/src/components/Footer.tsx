import { Layout, Space, Typography } from 'antd';
import { GithubOutlined, MailOutlined, GlobalOutlined } from '@ant-design/icons';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

export default function Footer() {
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
            <GithubOutlined style={{ fontSize: 16 }} /> GitHub
          </Link>
          <Link href="mailto:contact@biomni.com">
            <MailOutlined style={{ fontSize: 16 }} /> Contact
          </Link>
          <Link href="https://biomni.com" target="_blank">
            <GlobalOutlined style={{ fontSize: 16 }} /> Website
          </Link>
        </Space>

        {/* 版权信息 */}
        <Text type="secondary" style={{ fontSize: 12 }}>
          © 2025 Biomni. All rights reserved. | Powered by AI
        </Text>

        {/* 描述 */}
        <Text type="secondary" style={{ fontSize: 12 }}>
          A universal biomedical AI agent for research and analysis
        </Text>
      </Space>
    </AntFooter>
  );
}
