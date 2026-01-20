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
import type { ExecutionStep } from '@/types';

const { Text } = Typography;

interface ExecutionPanelProps {
  steps: ExecutionStep[];
}

export default function ExecutionPanel({ steps }: ExecutionPanelProps) {
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

  const successCount = steps.filter((s) => s.status === 'success').length;

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
            Biomni Executor
          </Text>
        </div>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
          {steps.length > 0 ? `${successCount}/${steps.length} 步骤完成` : '等待执行...'}
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
            <Text type="secondary">Agent 准备就绪</Text>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {steps.map((step, index) => (
              <div
                key={step.id}
                style={{
                  background: '#fff',
                  borderRadius: 8,
                  padding: 16,
                  boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                  border: '1px solid #f0f0f0',
                  position: 'relative',
                  transition: 'all 0.3s',
                }}
              >
                {/* 步骤序号 */}
                <div
                  style={{
                    position: 'absolute',
                    top: -8,
                    left: 16,
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

                {/* 步骤头部 */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 12,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {getStepIcon(step.stepType)}
                    <Text strong style={{ fontSize: 14 }}>
                      {step.stepName || step.stepType}
                    </Text>
                  </div>
                  {getStatusIcon(step.status)}
                </div>

                {/* 工具调用信息 */}
                {step.stepType === 'tool_call' && step.toolName && (
                  <div style={{ marginBottom: 12 }}>
                    <Badge
                      color="#fa8c16"
                      text={
                        <Text type="secondary" style={{ fontSize: 13 }}>
                          {step.toolName}
                        </Text>
                      }
                    />
                  </div>
                )}

                {/* 工具输入/输出 */}
                {(step.toolInput || step.toolOutput) && (
                  <Collapse
                    ghost
                    size="small"
                    items={[
                      ...(step.toolInput
                        ? [
                            {
                              key: 'input',
                              label: (
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                  输入参数
                                </Text>
                              ),
                              children: (
                                <SyntaxHighlighter
                                  language="json"
                                  style={vscDarkPlus}
                                  customStyle={{
                                    fontSize: 11,
                                    margin: 0,
                                    borderRadius: 4,
                                  }}
                                >
                                  {JSON.stringify(step.toolInput, null, 2)}
                                </SyntaxHighlighter>
                              ),
                            },
                          ]
                        : []),
                      ...(step.toolOutput
                        ? [
                            {
                              key: 'output',
                              label: (
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                  执行结果
                                </Text>
                              ),
                              children: (
                                <div
                                  style={{
                                    background: '#f5f5f5',
                                    padding: 12,
                                    borderRadius: 4,
                                    fontSize: 12,
                                    maxHeight: 200,
                                    overflow: 'auto',
                                    fontFamily: 'monospace',
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word',
                                  }}
                                >
                                  {step.toolOutput}
                                </div>
                              ),
                            },
                          ]
                        : []),
                    ]}
                  />
                )}

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
                      ⚠️ {step.errorMessage}
                    </Text>
                  </div>
                )}

                {/* 时间和耗时 */}
                <div
                  style={{
                    marginTop: 12,
                    paddingTop: 12,
                    borderTop: '1px solid #f0f0f0',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {step.startedAt ? new Date(step.startedAt).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    }) : '--:--:--'}
                  </Text>
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
                </div>
              </div>
            ))}
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
