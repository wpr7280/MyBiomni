# 附件上传功能说明

## 问题排查

如果看不到附件按钮（📎），请按以下步骤排查：

### 1. 检查 Ant Design X 版本

```bash
npm list @ant-design/x
```

确保版本 >= 1.0.0

### 2. 重新安装依赖

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev:mock
```

### 3. 检查浏览器控制台

打开浏览器控制台（F12），查看是否有错误信息。

### 4. 手动测试

在浏览器控制台输入：
```javascript
console.log(window.location.href);
```

确认页面已正确加载。

---

## 附件上传配置

当前配置：
```typescript
<Sender 
  onSubmit={handleSendMessage} 
  placeholder="Ask something or upload a file..." 
  loading={isExecuting}
  attachments={{
    items: [],
    onChange: (files) => {
      console.log('上传文件:', files);
    }
  }}
/>
```

---

## 预期效果

附件按钮应该显示在输入框的左侧，点击后可以选择文件上传。

如果仍然看不到，可能是 Ant Design X 版本问题，建议升级到最新版本。

---

**更新时间**: 2025-01-20
