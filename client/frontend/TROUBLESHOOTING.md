# 故障排除

## 常见问题

### 1. 模块导入错误

**错误信息**：
```
Failed to resolve import "@/components/ChatWindow"
```

**解决方案**：

```bash
# 方法 1：清除缓存并重启
rm -rf node_modules/.vite
npm run dev:mock

# 方法 2：重新安装依赖
rm -rf node_modules
npm install
npm run dev:mock

# 方法 3：清除所有缓存
rm -rf node_modules/.vite dist
npm run dev:mock
```

### 2. TypeScript 类型错误

**解决方案**：
```bash
# 重新生成类型
npx tsc --noEmit
```

### 3. 端口被占用

**错误信息**：
```
Port 3001 is already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :3001

# 杀死进程
kill -9 <PID>

# 或者修改端口
# 编辑 vite.config.ts，修改 server.port
```

### 4. Mock 模式不生效

**检查清单**：
- ✅ 确认使用 `npm run dev:mock` 启动
- ✅ 检查 `.env.mock` 文件存在
- ✅ 检查控制台是否显示 "🎭 Mock 模式已启用"

### 5. WebSocket 连接失败

**Mock 模式**：
- Mock WebSocket 会自动工作，不需要真实服务

**真实 API 模式**：
- 确保 Python Agent 服务已启动（http://localhost:8000）
- 检查 CORS 配置
- 检查 Token 是否有效

---

## 开发建议

### 推荐的开发流程

1. **首次启动**
   ```bash
   npm install
   npm run dev:mock
   ```

2. **遇到问题时**
   ```bash
   # 清除缓存
   rm -rf node_modules/.vite
   
   # 重启
   npm run dev:mock
   ```

3. **切换到真实 API**
   ```bash
   # 修改 .env.development
   VITE_USE_MOCK=false
   
   # 重启
   npm run dev
   ```

---

**更新时间**: 2025-01-20
