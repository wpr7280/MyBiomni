# Execution Steps 前端展示方案

## 🎯 方案说明

**后端保存完整内容，前端智能拆分和展示。**

### 核心思路

1. **后端**：保存完整的步骤内容（不拆分）
   - Reasoning：完整保存，最多 8000 字符
   - Result：完整保存，最多 10000 字符
   - 避免内容截断问题

2. **前端**：智能解析和展示（动态拆分）
   - 检测分隔符（`===`, `---`）
   - 检测章节标题（数字开头、全大写）
   - 按逻辑块拆分显示
   - 支持折叠/展开

## 🎨 前端实现

### 1. 智能拆分函数

```typescript
const splitLongContent = (content: string): string[] => {
  if (!content || content.length < 1000) {
    return [content]; // 短内容不拆分
  }
  
  const sections: string[] = [];
  const lines = content.split('\n');
  let currentSection: string[] = [];
  let currentLength = 0;
  
  for (const line of lines) {
    const stripped = line.trim();
    
    // 检测分隔符（=== 或 --- 长度>50）
    const isSeparator = (stripped.startsWith('===') && stripped.length > 50) ||
                       (stripped.startsWith('---') && stripped.length > 50);
    
    // 检测章节标题（数字开头或全大写）
    const isTitle = stripped.match(/^\d+\./) ||
                   (stripped.length > 10 && stripped.length < 100 && 
                    stripped === stripped.toUpperCase());
    
    // 在分隔符或标题处拆分
    if ((isSeparator || isTitle) && currentSection.length > 5 && currentLength > 300) {
      sections.push(currentSection.join('\n'));
      currentSection = [line];
      currentLength = line.length;
    } else {
      currentSection.push(line);
      currentLength += line.length;
      
      // 如果累积长度超过1500，在此处拆分
      if (currentLength > 1500) {
        sections.push(currentSection.join('\n'));
        currentSection = [];
        currentLength = 0;
      }
    }
  }
  
  // 保存最后一个section
  if (currentSection.length > 0) {
    sections.push(currentSection.join('\n'));
  }
  
  return sections.filter(s => s.trim().length > 20);
};
```

### 2. 折叠/展开显示

```typescript
// Reasoning 类型
if (sections.length > 1) {
  // 多个部分，使用折叠面板
  return (
    <div>
      {sections.map((section, index) => (
        <div key={index}>
          {/* 折叠头部 */}
          <div onClick={() => toggleSection(step.id, index)}>
            Section {index + 1}/{sections.length}
            <DownOutlined />
          </div>
          
          {/* 内容（可折叠） */}
          {isExpanded ? (
            <ReactMarkdown>{section}</ReactMarkdown>
          ) : (
            <Text>{preview}...</Text>
          )}
        </div>
      ))}
    </div>
  );
}
```

### 3. Result 类型展示

```typescript
// Result 类型：同样支持拆分
const sections = splitLongContent(content);

return (
  <div>
    {sections.map((section, index) => (
      <div key={index}>
        {sections.length > 1 && (
          <div onClick={() => toggleSection(step.id, index)}>
            Part {index + 1}/{sections.length}
          </div>
        )}
        {isExpanded ? (
          <pre>{section}</pre>
        ) : (
          <Text>{preview}...</Text>
        )}
      </div>
    ))}
    
    {/* 图片 */}
    {step.images && step.images.map(...)}
  </div>
);
```

## 📊 显示效果

### 短内容（<1000字符）
```
Step 5: 🤔 Reasoning
┌─────────────────────────────────────┐
│ I'll help you analyze...            │
│                                     │
│ Let me create a plan:               │
│ 1. [ ] First step                   │
│ 2. [ ] Second step                  │
└─────────────────────────────────────┘
```

### 长内容（>1000字符）
```
Step 6: 📋 Observation
┌─────────────────────────────────────┐
│ Section 1/5 ▼                       │
│ ================                    │
│ PERTURBATION EFFECTS...             │
│ (完整显示)                           │
├─────────────────────────────────────┤
│ Section 2/5 ▼                       │
│ 1. TYPES OF PERTURBATIONS...        │
│ (完整显示)                           │
├─────────────────────────────────────┤
│ Section 3/5 ▶ (折叠)                │
│ Genetic Perturbations... (预览)     │
├─────────────────────────────────────┤
│ Section 4/5 ▶ (折叠)                │
│ Chemical Perturbations... (预览)    │
├─────────────────────────────────────┤
│ Section 5/5 ▼                       │
│ Environmental Perturbations...      │
│ (完整显示)                           │
└─────────────────────────────────────┘
```

## ✅ 优势

1. **后端简单**：
   - 不需要复杂的拆分逻辑
   - 避免内容截断问题
   - 数据库存储完整内容

2. **前端灵活**：
   - 动态拆分，按需展示
   - 用户可以折叠/展开
   - 不影响数据完整性

3. **用户体验好**：
   - 默认展开重要部分
   - 可以折叠冗长部分
   - 清晰的章节导航

## 🚀 使用效果

- ✅ 所有内容都被保存（后端）
- ✅ 智能拆分显示（前端）
- ✅ 可折叠/展开（交互）
- ✅ 内容完整不截断
- ✅ 步骤数量合理（10-20个）
- ✅ 显示详细丰富（前端拆分为30-50个子部分）

重启前端服务即可看到效果。
