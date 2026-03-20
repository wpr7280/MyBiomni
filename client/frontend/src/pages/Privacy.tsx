import { Button, Typography, Divider, Card } from 'antd';
import { ArrowLeftOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const { Title, Paragraph, Text } = Typography;

export default function Privacy() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const sections = [
    {
      title: '1. Introduction',
      content: 'WarpHelix ("we", "our", "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our AI-powered biomedical research platform.',
    },
    {
      title: '2. Information We Collect',
      subsections: [
        { subtitle: 'Account Information', text: 'When you create an account, we collect your email address, username, and authentication credentials.' },
        { subtitle: 'Usage Data', text: 'We collect information about your interactions with the Service, including queries submitted, code executed, analysis results, token usage, and session metadata.' },
        { subtitle: 'Uploaded Files', text: 'Files you upload for analysis (datasets, sequences, documents) are stored securely on our servers for processing purposes.' },
      ],
    },
    {
      title: '3. How We Use Your Information',
      content: 'We use your information to:',
      list: [
        'Provide and improve the Service',
        'Process your research queries and execute analyses',
        'Manage your account and token quotas',
        'Ensure platform security and prevent abuse',
        'Communicate important updates about the Service',
      ],
    },
    {
      title: '4. Data Storage and Security',
      content: 'Your data is stored on secure cloud infrastructure (AWS). We implement industry-standard security measures including encryption at rest and in transit, access controls, and regular security audits.',
      highlight: true,
    },
    {
      title: '5. Data Retention',
      content: 'Conversation history and analysis results are retained for the duration of your account. Uploaded files are retained as long as needed for analysis and may be deleted upon your request. Deleted conversations are soft-deleted and may be retained for administrative purposes.',
    },
    {
      title: '6. Data Sharing',
      content: 'We do not sell your personal information. We may share data with:',
      list: [
        'Cloud service providers (AWS) for infrastructure purposes',
        'AI model providers (Anthropic, OpenAI) for query processing — only the query content is shared, not your personal information',
        'Law enforcement when required by applicable law',
      ],
    },
    {
      title: '7. Your Rights',
      content: 'You have the right to:',
      list: [
        'Access your personal data',
        'Request correction of inaccurate data',
        'Request deletion of your data',
        'Export your conversation history',
        'Withdraw consent for data processing',
      ],
    },
    {
      title: '8. Research Data',
      content: 'We understand the sensitivity of biomedical research data. Your research queries, uploaded datasets, and analysis results are treated as confidential. We do not use your research data to train AI models without your explicit consent.',
      highlight: true,
    },
    {
      title: '9. Cookies and Tracking',
      content: 'We use essential cookies for authentication and session management. We do not use third-party tracking cookies or analytics services.',
    },
    {
      title: '10. Children\'s Privacy',
      content: 'The Service is not intended for users under 18 years of age. We do not knowingly collect information from minors.',
    },
    {
      title: '11. Changes to This Policy',
      content: 'We may update this Privacy Policy periodically. We will notify you of significant changes via email or through the Service.',
    },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)' }}>
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1px solid #f0f0f0', padding: '12px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 10 }}>
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ fontSize: 14 }}>
          Back
        </Button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 20 }}>🧬</span>
          <Text strong style={{ fontSize: 16 }}>WarpHelix</Text>
        </div>
        <div style={{ width: 80 }} />
      </div>

      {/* Content */}
      <div style={{ maxWidth: 820, margin: '0 auto', padding: '32px 24px 64px' }}>
        <Card
          style={{ borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}
          bodyStyle={{ padding: '40px 48px' }}
        >
          {/* Title section */}
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <LockOutlined style={{ fontSize: 40, color: '#52c41a', marginBottom: 12 }} />
            <Title level={2} style={{ marginBottom: 4 }}>Privacy Policy</Title>
            <Text type="secondary">Last updated: March 2026</Text>
          </div>

          <Divider />

          {/* Sections */}
          {sections.map((section, index) => (
            <div key={index} style={{ marginBottom: 28 }}>
              <Title level={4} style={{ color: '#262626', marginBottom: 8 }}>{section.title}</Title>

              {section.subsections ? (
                section.subsections.map((sub, i) => (
                  <div key={i} style={{ marginBottom: 12, paddingLeft: 16, borderLeft: '3px solid #e8e8e8' }}>
                    <Text strong style={{ color: '#262626' }}>{sub.subtitle}</Text>
                    <Paragraph style={{ color: '#595959', lineHeight: 1.8, marginBottom: 0, marginTop: 4 }}>{sub.text}</Paragraph>
                  </div>
                ))
              ) : section.highlight ? (
                <div style={{ background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 8, padding: '12px 16px' }}>
                  <Paragraph style={{ marginBottom: 0, color: '#389e0d' }}>{section.content}</Paragraph>
                </div>
              ) : (
                <Paragraph style={{ color: '#595959', lineHeight: 1.8 }}>{section.content}</Paragraph>
              )}

              {section.list && (
                <ul style={{ color: '#595959', lineHeight: 2, paddingLeft: 24 }}>
                  {section.list.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}

          <Divider />

          {/* Contact */}
          <div style={{ textAlign: 'center', padding: '16px 0' }}>
            <Title level={4}>12. Contact Us</Title>
            <Paragraph style={{ color: '#595959' }}>
              For privacy-related inquiries, please contact us at{' '}
              <a href="mailto:peirongw@foxmail.com" style={{ color: '#1890ff' }}>peirongw@foxmail.com</a>
            </Paragraph>
          </div>
        </Card>

        {/* Footer */}
        <div style={{ textAlign: 'center', padding: '24px 0', color: '#bfbfbf', fontSize: 12 }}>
          © 2025 WarpHelix. All rights reserved.
        </div>
      </div>
    </div>
  );
}
