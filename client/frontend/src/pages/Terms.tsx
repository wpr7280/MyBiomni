import { Button, Typography, Divider, Card } from 'antd';
import { ArrowLeftOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const { Title, Paragraph, Text } = Typography;

export default function Terms() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const sections = [
    {
      title: '1. Acceptance of Terms',
      content: 'By accessing or using the WarpHelix platform ("Service"), you agree to be bound by these Terms of Service. If you do not agree, please do not use the Service.',
    },
    {
      title: '2. Description of Service',
      content: 'WarpHelix is an AI-powered biomedical research assistant that provides intelligent data analysis, literature search, experimental design support, and code execution capabilities for researchers and biomedical professionals.',
    },
    {
      title: '3. User Accounts',
      content: 'You are responsible for maintaining the confidentiality of your account credentials. You agree to notify us immediately of any unauthorized use of your account.',
    },
    {
      title: '4. Acceptable Use',
      content: 'You agree not to:',
      list: [
        'Use the Service for any unlawful purpose or in violation of applicable regulations',
        'Attempt to gain unauthorized access to the Service or its systems',
        'Upload malicious code or attempt to compromise system security',
        'Use the Service to generate harmful, misleading, or unethical research content',
        'Exceed your allocated token quota or circumvent usage limits',
      ],
    },
    {
      title: '5. Intellectual Property',
      content: 'Research results, analyses, and outputs generated through your use of the Service belong to you. However, the Service itself, including its algorithms, models, and infrastructure, remains the property of WarpHelix.',
    },
    {
      title: '6. Data and Privacy',
      content: 'Your use of the Service is also governed by our Privacy Policy. By using the Service, you consent to the collection and use of data as described therein.',
    },
    {
      title: '7. AI-Generated Content Disclaimer',
      content: 'The Service uses artificial intelligence to assist with biomedical research. AI-generated results should be independently verified before use in clinical, diagnostic, or therapeutic decisions. WarpHelix does not guarantee the accuracy, completeness, or reliability of AI-generated outputs.',
      highlight: true,
    },
    {
      title: '8. Limitation of Liability',
      content: 'THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND. WARPHELIX SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING FROM YOUR USE OF THE SERVICE.',
    },
    {
      title: '9. Token Quotas and Billing',
      content: 'Usage of the Service is subject to token quotas assigned to your account. Exceeding your quota may result in temporary suspension of service until additional tokens are allocated.',
    },
    {
      title: '10. Termination',
      content: 'We reserve the right to suspend or terminate your access to the Service at any time for violation of these Terms or for any other reason at our discretion.',
    },
    {
      title: '11. Changes to Terms',
      content: 'We may update these Terms from time to time. Continued use of the Service after changes constitutes acceptance of the updated Terms.',
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
            <SafetyCertificateOutlined style={{ fontSize: 40, color: '#1890ff', marginBottom: 12 }} />
            <Title level={2} style={{ marginBottom: 4 }}>Terms of Service</Title>
            <Text type="secondary">Last updated: March 2026</Text>
          </div>

          <Divider />

          {/* Sections */}
          {sections.map((section, index) => (
            <div key={index} style={{ marginBottom: 28 }}>
              <Title level={4} style={{ color: '#262626', marginBottom: 8 }}>{section.title}</Title>
              {section.highlight ? (
                <div style={{ background: '#fff7e6', border: '1px solid #ffd591', borderRadius: 8, padding: '12px 16px' }}>
                  <Paragraph style={{ marginBottom: 0, color: '#ad6800' }}>{section.content}</Paragraph>
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
            <Title level={4}>12. Contact</Title>
            <Paragraph style={{ color: '#595959' }}>
              For questions about these Terms, please contact us at{' '}
              <a href="mailto:peirongw@foxmail.com" style={{ color: '#1890ff' }}>peirongw@foxmail.com</a>
            </Paragraph>
          </div>
        </Card>

        {/* Footer */}
        <div style={{ textAlign: 'center', padding: '24px 0', color: '#bfbfbf', fontSize: 12 }}>
          © 2026 WarpHelix. All rights reserved.
        </div>
      </div>
    </div>
  );
}
