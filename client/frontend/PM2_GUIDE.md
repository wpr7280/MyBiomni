# Biomni Client Frontend PM2 部署指南

## 快速开始

### 1. 配置远端 API 地址

编辑 `.env.development` 文件，修改为你的远端服务器地址：

```bash
# 修改为实际的服务器地址
VITE_API_URL=http://your-server-ip:9999
VITE_WS_URL=ws://your-server-ip:8000
```

示例：
```bash
# 使用 IP 地址
VITE_API_URL=http://192.168.1.100:9999
VITE_WS_URL=ws://192.168.1.100:8000

# 或使用域名
VITE_API_URL=https://api.biomni.com
VITE_WS_URL=wss://api.biomni.com/ws
```

### 2. 一键启动

```bash
cd client/frontend
chmod +x start-pm2.sh
./start-pm2.sh
```

### 3. 访问应用

打开浏览器访问：http://localhost:5173

---

## 手动启动步骤

### 1. 安装 PM2（如果未安装）

```bash
npm install -g pm2
```

### 2. 安装项目依赖

```bash
cd client/frontend
npm install
```

### 3. 配置环境变量

编辑 `.env.development` 文件：

```bash
VITE_API_URL=http://your-server-ip:9999
VITE_WS_URL=ws://your-server-ip:8000
```

### 4. 启动服务

```bash
# 使用配置文件启动
pm2 start ecosystem.config.cjs

# 或直接启动
pm2 start "npm run dev" --name biomni-client-frontend
```

---

## PM2 常用命令

### 查看服务状态

```bash
# 列出所有进程
pm2 list

# 查看详细信息
pm2 show biomni-client-frontend

# 实时监控
pm2 monit
```

### 查看日志

```bash
# 实时日志
pm2 logs biomni-client-frontend

# 查看最近 100 行
pm2 logs biomni-client-frontend --lines 100

# 只看错误日志
pm2 logs biomni-client-frontend --err

# 清空日志
pm2 flush
```

### 重启/停止服务

```bash
# 重启
pm2 restart biomni-client-frontend

# 停止
pm2 stop biomni-client-frontend

# 删除进程
pm2 delete biomni-client-frontend

# 重载（0 秒停机）
pm2 reload biomni-client-frontend
```

### 开机自启

```bash
# 生成启动脚本
pm2 startup

# 保存当前进程列表
pm2 save

# 取消开机自启
pm2 unstartup
```

---

## 配置说明

### ecosystem.config.cjs

```javascript
module.exports = {
  apps: [
    {
      name: 'biomni-client-frontend',        // 进程名称
      script: 'npx',                         // 执行命令
      args: 'vite --mode development --port 5173 --host 0.0.0.0',
      instances: 1,                          // 实例数量
      autorestart: true,                     // 自动重启
      watch: false,                          // 不监听文件变化
      max_memory_restart: '500M',            // 内存超过 500M 自动重启
      env: {
        NODE_ENV: 'development',
        PORT: 5173,
      },
      error_file: './logs/err.log',          // 错误日志
      out_file: './logs/out.log',            // 输出日志
    },
  ],
};
```

### 修改端口

如果需要修改端口，编辑 `ecosystem.config.cjs`：

```javascript
args: 'vite --mode development --port 8080 --host 0.0.0.0',
env: {
  PORT: 8080,
},
```

---

## 故障排查

### 1. 服务无法启动

```bash
# 查看详细日志
pm2 logs biomni-client-frontend --lines 200

# 检查端口占用
lsof -i :5173
# 或
netstat -tuln | grep 5173

# 杀掉占用进程
kill -9 <PID>
```

### 2. API 请求失败

检查 `.env.development` 配置：
- 确认 API 地址正确
- 确认服务器防火墙已开放端口
- 确认后端服务正在运行

```bash
# 测试 API 连接
curl http://your-server-ip:9999/api/health

# 测试 WebSocket 连接
wscat -c ws://your-server-ip:8000
```

### 3. 跨域问题

如果遇到 CORS 错误，需要在后端配置允许跨域：

```java
// Spring Boot 后端配置
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://localhost:5173")
                .allowedMethods("*")
                .allowCredentials(true);
    }
}
```

### 4. 内存占用过高

```bash
# 查看内存使用
pm2 monit

# 重启服务释放内存
pm2 restart biomni-client-frontend

# 调整内存限制
# 编辑 ecosystem.config.js
max_memory_restart: '1G',
```

---

## 生产环境部署

对于生产环境，建议使用构建后的静态文件 + Nginx：

### 1. 构建项目

```bash
npm run build
```

### 2. 使用 Nginx 部署

```nginx
server {
    listen 80;
    server_name client.biomni.com;
    
    root /path/to/client/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://backend-server:9999;
    }
    
    # WebSocket 代理
    location /ws {
        proxy_pass http://backend-server:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 性能优化

### 1. 启用 Gzip 压缩

Vite 已默认启用，无需额外配置。

### 2. 资源缓存

在 `vite.config.ts` 中配置：

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'antd-vendor': ['antd'],
        },
      },
    },
  },
});
```

### 3. 减少内存占用

```javascript
// ecosystem.config.js
max_memory_restart: '300M',  // 降低内存限制
```

---

## 监控和日志

### 日志文件位置

- 错误日志：`./logs/err.log`
- 输出日志：`./logs/out.log`

### 日志轮转

PM2 自动管理日志文件，可以手动清理：

```bash
# 清空所有日志
pm2 flush

# 安装日志轮转模块
pm2 install pm2-logrotate

# 配置日志轮转
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

---

## 多环境配置

### 开发环境

```bash
pm2 start ecosystem.config.js
```

### 测试环境

创建 `.env.test`：

```bash
VITE_API_URL=http://test-server:9999
VITE_WS_URL=ws://test-server:8000
```

启动：

```bash
pm2 start "npx vite --mode test" --name biomni-client-test
```

---

## 技术支持

如有问题，请查看：
- 项目文档：`README.md`
- API 文档：`../other/docs/API接口文档.md`
- 提交 Issue：GitHub Issues
