import { Typography, Badge, Collapse } from 'antd';
import {
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  CodeOutlined,
} from '@ant-design/icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import { useTranslation } from 'react-i18next';
import type { ExecutionStep } from '@/types';

const { Text } = Typography;

interface ExecutionPanelProps {
  steps: ExecutionStep[];
}

export default function ExecutionPanel({ steps }: ExecutionPanelProps) {
  const { t } = useTranslation();
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <LoadingOutlined spin style={{ color: '#1890ff', fontSize: 16 }} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 16 }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'reasoning':
        return <BulbOutlined style={{ color: '#1890ff' }} />;
      case 'tool_call':
        return <ThunderboltOutlined style={{ color: '#fa8c16' }} />;
      case 'result':
        return <CodeOutlined style={{ color: '#52c41a' }} />;
      default:
        return null;
    }
  };

  const getStepBadgeColor = (stepType: string) => {
    switch (stepType) {
      case 'reasoning':
        return '#1890ff';
      case 'tool_call':
        return '#fa8c16';
      case 'result':
        return '#52c41a';
      default:
        return '#d9d9d9';
    }
  };
  
  // 格式化步骤名称
  const formatStepName = (step: ExecutionStep) => {
    if (step.stepName) {
      return step.stepName;
    }
    
    // 根据类型生成默认名称
    switch (step.stepType) {
      case 'reasoning':
        return '🤔 Thinking';
      case 'tool_call':
        return '🛠️ Executing';
      case 'result':
        return '📋 Result';
      default:
        return step.stepType;
    }
  };

  const successCount = steps.filter((s) => s.status === 'success').length;

  // 渲染代码块
  const renderCode = (code: string, language: string = 'python') => {
    return (
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        customStyle={{
          fontSize: 12,
          margin: 0,
          borderRadius: 4,
          maxHeight: 400,
        }}
      >
        {code}
      </SyntaxHighlighter>
    );
  };

  // 渲染步骤内容
  const renderStepContent = (step: ExecutionStep) => {
    // Reasoning 类型：使用 Markdown 渲染
    if (step.stepType === 'reasoning' && step.toolOutput) {
      // 清理内容
      let content = step.toolOutput;
      
      // 移除多余的分隔符
      content = content.replace(/={50,}/g, '');
      content = content.replace(/Ai Message/g, '');
      content = content.replace(/Human Message/g, '');
      
      // 移除 function_calls 标签
      content = content.replace(/<\/?function_calls>/g, '');
      
      // 清理多余的空行
      content = content.replace(/\n{3,}/g, '\n\n');
      content = content.trim();
      
      if (!content) return null;
      
      return (
        <div
          style={{
            padding: 12,
            background: '#fafafa',
            borderRadius: 4,
            fontSize: 13,
            lineHeight: 1.6,
          }}
        >
          <ReactMarkdown
            components={{
              // 自定义代码块样式
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const language = match ? match[1] : '';
                
                return !inline && language ? (
                  <SyntaxHighlighter
                    language={language}
                    style={vscDarkPlus}
                    customStyle={{
                      fontSize: 12,
                      margin: '8px 0',
                      borderRadius: 4,
                    }}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code
                    className={className}
                    style={{
                      background: '#f0f0f0',
                      padding: '2px 6px',
                      borderRadius: 3,
                      fontSize: 12,
                      fontFamily: 'monospace',
                    }}
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              // 自定义列表样式
              ul: ({ children }) => (
                <ul style={{ marginLeft: 20, marginTop: 8, marginBottom: 8 }}>
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol style={{ marginLeft: 20, marginTop: 8, marginBottom: 8 }}>
                  {children}
                </ol>
              ),
              // 自定义标题样式
              h1: ({ children }) => <h3 style={{ marginTop: 12, marginBottom: 8 }}>{children}</h3>,
              h2: ({ children }) => <h4 style={{ marginTop: 10, marginBottom: 6 }}>{children}</h4>,
              h3: ({ children }) => <h5 style={{ marginTop: 8, marginBottom: 4 }}>{children}</h5>,
              // 自定义段落样式
              p: ({ children }) => <p style={{ marginTop: 4, marginBottom: 4 }}>{children}</p>,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      );
    }

    // Tool Call 类型：显示代码
    if (step.stepType === 'tool_call' && step.toolInput) {
      const input = typeof step.toolInput === 'string' ? JSON.parse(step.toolInput) : step.toolInput;
      const code = input.code || '';
      const language = input.language || 'python';
      
      return renderCode(code, language);
    }

    // Result 类型：显示执行结果 + 图片
    if (step.stepType === 'result' && step.toolOutput) {
      return (
        <div>
          {/* 文本输出 */}
          <div
            style={{
              padding: 12,
              background: '#f5f5f5',
              borderRadius: 4,
              fontSize: 12,
              maxHeight: 400,
              overflow: 'auto',
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {step.toolOutput}
          </div>
          
          {/* 图片展示 */}
          {step.images && step.images.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                🖼️ Generated Images:
              </Text>
              {step.images.map((img, idx) => (
                <div key={idx} style={{ marginBottom: 12 }}>
                  <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 4 }}>
                    {img.filename}
                  </Text>
                  <img
                    src={img.data}
                    alt={img.filename}
                    style={{
                      maxWidth: '100%',
                      borderRadius: 4,
                      border: '1px solid #e8e8e8',
                      cursor: 'pointer',
                    }}
                    onClick={() => window.open(img.data, '_blank')}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: '#fafafa',
      }}
    >
      {/* 头部 */}
      <div
        style={{
          padding: '20px 24px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: steps.length > 0 ? '#52c41a' : '#d9d9d9',
              animation: steps.some((s) => s.status === 'running') ? 'pulse 2s infinite' : 'none',
            }}
          />
          <Text strong style={{ fontSize: 16 }}>
            {t('execution.title')}
          </Text>
        </div>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
          {steps.length > 0 ? t('execution.stepsCompleted', { success: successCount, total: steps.length }) : t('execution.waiting')}
        </Text>
      </div>

      {/* 执行步骤列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
        {steps.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '60px 20px',
              color: '#bfbfbf',
            }}
          >
            <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
            <Text type="secondary">{t('execution.ready')}</Text>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {steps.map((step, index) => {
              const content = renderStepContent(step);
              
              return (
                <Collapse
                  key={step.id}
                  defaultActiveKey={['1']}
                  ghost
                  items={[
                    {
                      key: '1',
                      label: (
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            width: '100%',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            {/* 步骤序号 */}
                            <div
                              style={{
                                background: getStepBadgeColor(step.stepType),
                                color: '#fff',
                                width: 24,
                                height: 24,
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 12,
                                fontWeight: 'bold',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                              }}
                            >
                              {index + 1}
                            </div>
                            {getStepIcon(step.stepType)}
                            <Text strong style={{ fontSize: 14 }}>
                              {formatStepName(step)}
                            </Text>
                            {/* 时间 */}
                            <Text type="secondary" style={{ fontSize: 11, marginLeft: 8 }}>
                              {step.startedAt ? new Date(step.startedAt).toLocaleTimeString('zh-CN', {
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                              }) : '--:--:--'}
                            </Text>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            {step.durationMs > 0 && (
                              <Badge
                                count={`${step.durationMs}ms`}
                                style={{
                                  background: '#f0f0f0',
                                  color: '#595959',
                                  fontSize: 11,
                                  boxShadow: 'none',
                                }}
                              />
                            )}
                            {getStatusIcon(step.status)}
                          </div>
                        </div>
                      ),
                      children: content ? (
                        <div style={{ marginTop: 8 }}>
                          {content}
                          {/* 错误信息 */}
                          {step.errorMessage && (
                            <div
                              style={{
                                marginTop: 12,
                                padding: 12,
                                background: '#fff2f0',
                                border: '1px solid #ffccc7',
                                borderRadius: 4,
                              }}
                            >
                              <Text type="danger" style={{ fontSize: 12 }}>
                                {t('execution.error', { message: step.errorMessage })}
                              </Text>
                            </div>
                          )}
                        </div>
                      ) : null,
                    },
                  ]}
                  style={{
                    background: '#fff',
                    borderRadius: 8,
                    border: '1px solid #f0f0f0',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                  }}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* 添加脉冲动画 */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
}
