import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownContentProps {
  content: string;
}

interface MarkdownContentProps {
  content: string;
}

// 预处理 Markdown 内容，修复表格格式
function preprocessMarkdown(content: string): string {
  // 修复表格：将 | 开头的行识别为表格
  const lines = content.split('\n');
  const processedLines: string[] = [];
  let inTable = false;
  let tableHeaderProcessed = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 检测表格行（以 | 开头和结尾）
    if (line.startsWith('|') && line.endsWith('|')) {
      if (!inTable) {
        // 表格开始
        inTable = true;
        tableHeaderProcessed = false;
        processedLines.push(line);
        
        // 检查下一行是否是分隔符，如果不是则添加
        const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : '';
        if (!nextLine.match(/^\|[\s\-:]+\|/)) {
          // 生成分隔符行
          const columns = line.split('|').filter(c => c.trim()).length;
          const separator = '| ' + Array(columns).fill('---').join(' | ') + ' |';
          processedLines.push(separator);
          tableHeaderProcessed = true;
        }
      } else {
        // 表格中
        if (!tableHeaderProcessed && line.match(/^\|[\s\-:]+\|/)) {
          // 这是分隔符行
          processedLines.push(line);
          tableHeaderProcessed = true;
        } else {
          processedLines.push(line);
        }
      }
    } else {
      // 非表格行
      if (inTable) {
        inTable = false;
        tableHeaderProcessed = false;
      }
      processedLines.push(lines[i]);
    }
  }
  
  return processedLines.join('\n');
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  // 预处理内容
  const processedContent = preprocessMarkdown(content);
  
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}  // 启用 GitHub Flavored Markdown（支持表格）
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              customStyle={{
                borderRadius: 6,
                fontSize: 13,
                margin: '12px 0',
              }}
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code
              style={{
                background: '#f5f5f5',
                padding: '2px 6px',
                borderRadius: 3,
                fontSize: '0.9em',
                fontFamily: 'monospace',
              }}
              {...props}
            >
              {children}
            </code>
          );
        },
        // 表格样式优化
        table: ({ children }) => (
          <div style={{ overflowX: 'auto', marginBottom: 16, marginTop: 12 }}>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: 13,
                border: '1px solid #e8e8e8',
                borderRadius: 4,
                background: '#fff',
              }}
            >
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead style={{ background: '#fafafa' }}>{children}</thead>
        ),
        tbody: ({ children }) => (
          <tbody style={{ background: '#fff' }}>{children}</tbody>
        ),
        tr: ({ children, ...props }) => {
          // 检查是否是表头行
          const isHeader = props.node?.tagName === 'tr' && 
                          props.node?.children?.some((child: any) => child.tagName === 'th');
          
          return (
            <tr 
              style={{ 
                borderBottom: '1px solid #e8e8e8',
                background: isHeader ? '#fafafa' : '#fff',
              }}
            >
              {children}
            </tr>
          );
        },
        th: ({ children }) => (
          <th
            style={{
              padding: '12px 16px',
              textAlign: 'left',
              fontWeight: 600,
              color: '#262626',
              borderRight: '1px solid #e8e8e8',
              background: '#fafafa',
            }}
          >
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td
            style={{
              padding: '10px 16px',
              borderRight: '1px solid #e8e8e8',
              lineHeight: 1.6,
              color: '#595959',
            }}
          >
            {children}
          </td>
        ),
        h1: ({ children }) => (
          <h1 style={{ fontSize: 24, fontWeight: 600, marginTop: 24, marginBottom: 16, color: '#262626' }}>
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 style={{ fontSize: 20, fontWeight: 600, marginTop: 20, marginBottom: 12, color: '#262626' }}>
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 style={{ fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 10, color: '#262626' }}>
            {children}
          </h3>
        ),
        h4: ({ children }) => (
          <h4 style={{ fontSize: 14, fontWeight: 600, marginTop: 14, marginBottom: 8, color: '#262626' }}>
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p style={{ marginBottom: 12, lineHeight: 1.6, color: '#595959' }}>{children}</p>
        ),
        ul: ({ children }) => (
          <ul style={{ marginLeft: 20, marginBottom: 12, lineHeight: 1.6 }}>{children}</ul>
        ),
        ol: ({ children }) => (
          <ol style={{ marginLeft: 20, marginBottom: 12, lineHeight: 1.6 }}>{children}</ol>
        ),
        li: ({ children }) => (
          <li style={{ marginBottom: 6, lineHeight: 1.6, color: '#595959' }}>{children}</li>
        ),
        blockquote: ({ children }) => (
          <blockquote
            style={{
              borderLeft: '4px solid #1890ff',
              paddingLeft: 16,
              marginLeft: 0,
              marginBottom: 12,
              color: '#595959',
              fontStyle: 'italic',
            }}
          >
            {children}
          </blockquote>
        ),
        hr: () => (
          <hr style={{ border: 'none', borderTop: '1px solid #e8e8e8', margin: '16px 0' }} />
        ),
        strong: ({ children }) => (
          <strong style={{ fontWeight: 600, color: '#262626' }}>{children}</strong>
        ),
      }}
    >
      {processedContent}
    </ReactMarkdown>
  );
}
