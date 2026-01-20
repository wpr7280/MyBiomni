import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownContentProps {
  content: string;
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <ReactMarkdown
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
        h1: ({ children }) => (
          <h1 style={{ fontSize: 24, fontWeight: 600, marginTop: 24, marginBottom: 16 }}>
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 style={{ fontSize: 20, fontWeight: 600, marginTop: 20, marginBottom: 12 }}>
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 style={{ fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 10 }}>
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p style={{ marginBottom: 12, lineHeight: 1.6 }}>{children}</p>
        ),
        ul: ({ children }) => (
          <ul style={{ marginLeft: 20, marginBottom: 12 }}>{children}</ul>
        ),
        ol: ({ children }) => (
          <ol style={{ marginLeft: 20, marginBottom: 12 }}>{children}</ol>
        ),
        li: ({ children }) => (
          <li style={{ marginBottom: 6, lineHeight: 1.6 }}>{children}</li>
        ),
        blockquote: ({ children }) => (
          <blockquote
            style={{
              borderLeft: '4px solid #1890ff',
              paddingLeft: 16,
              marginLeft: 0,
              color: '#595959',
              fontStyle: 'italic',
            }}
          >
            {children}
          </blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
