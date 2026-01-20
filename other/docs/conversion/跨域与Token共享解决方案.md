# 跨域与 Token 共享解决方案

## 1. 问题分析

### 1.1 跨域问题

```
Admin 前端: http://localhost:3000
Client 前端: http://localhost:3001
Spring Boot: http://localhost:8083
Python Agent: http://localhost:8000

问题：
1. 不同端口 = 不同源 = 跨域
2. localStorage 不能跨域共享
3. Cookie 需要特殊配置才能跨域
```

### 1.2 localStorage 隔离

```javascript
// Admin 前端 (localhost:3000)
localStorage.setItem('token', 'xxx');  // 只能在 3000 端口访问

// Client 前端 (localhost:3001)
localStorage.getItem('token');  // ❌ 读不到！因为是不同的域
```

---

## 2. 解决方案（推荐）

### 方案 A：URL 参数传递 Token（最简单）

#### 2.1 工作流程

```
1. 用户在 Admin 前端登录
   ↓
2. Admin 前端保存 Token 到 localStorage (localhost:3000)
   ↓
3. 用户点击"进入对话"
   ↓
4. Admin 前端跳转到 Client 前端，Token 作为 URL 参数
   http://localhost:3001/auth/sso?token=eyJhbGci...
   ↓
5. Client 前端从 URL 获取 Token
   ↓
6. Client 前端保存 Token 到 localStorage (localhost:3001)
   ↓
7. 完成！两个前端都有 Token 了
```

#### 2.2 实现代码

**Admin 前端（Vue3）**

```vue
<!-- admin/frontend/src/layout/components/Header.vue -->
<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

function goToClientPortal() {
  // 1. 从 localStorage 获取 Token
  const token = localStorage.getItem('token');
  
  if (!token) {
    message.error('请先登录');
    return;
  }
  
  // 2. 跳转到 Client 前端，Token 作为 URL 参数
  const clientUrl = `http://localhost:3001/auth/sso?token=${encodeURIComponent(token)}`;
  
  // 3. 新窗口打开（或者当前窗口跳转）
  window.open(clientUrl, '_blank');
  // 或者：window.location.href = clientUrl;
}
</script>

<template>
  <div class="header">
    <button @click="goToClientPortal">
      <i class="icon-chat" />
      进入对话
    </button>
  </div>
</template>
```

**Client 前端（React）**

```tsx
// client/frontend/src/pages/SSOLogin.tsx
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { message } from 'antd';
import axios from 'axios';

export default function SSOLogin() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      message.error('缺少 Token');
      navigate('/login');
      return;
    }
    
    // 验证 Token 是否有效
    verifyAndSaveToken(token);
  }, [searchParams, navigate]);
  
  async function verifyAndSaveToken(token: string) {
    try {
      // 1. 验证 Token（调用后端接口）
      const response = await axios.get('http://localhost:8083/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const user = response.data.data;
      
      // 2. Token 有效，保存到 localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // 3. 清除 URL 中的 Token（安全考虑）
      window.history.replaceState({}, document.title, '/');
      
      // 4. 跳转到首页
      message.success(`欢迎，${user.username}！`);
      navigate('/');
      
    } catch (error) {
      // Token 无效
      message.error('Token 无效或已过期，请重新登录');
      navigate('/login');
    }
  }
  
  return (
    <div style={{ textAlign: 'center', padding: '100px' }}>
      <Spin size="large" />
      <p>正在登录...</p>
    </div>
  );
}
```

**路由配置**

```tsx
// client/frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SSOLogin from './pages/SSOLogin';
import Home from './pages/Home';
import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth/sso" element={<SSOLogin />} />
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### 方案 B：使用同一个域名（生产环境推荐）

#### 2.1 Nginx 反向代理

```nginx
# nginx.conf
server {
    listen 80;
    server_name biomni.example.com;

    # Admin 前端
    location /admin {
        alias /usr/share/nginx/html/admin;
        try_files $uri $uri/ /admin/index.html;
    }

    # Client 前端
    location / {
        root /usr/share/nginx/html/client;
        try_files $uri $uri/ /index.html;
    }

    # Spring Boot API
    location /api {
        proxy_pass http://backend:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Python Agent WebSocket
    location /ws {
        proxy_pass http://agent:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**优势**：
- ✅ 同一个域名，没有跨域问题
- ✅ localStorage 可以共享
- ✅ 更安全（Token 不会出现在 URL 中）

**访问地址**：
```
Admin 前端: http://biomni.example.com/admin
Client 前端: http://biomni.example.com/
API: http://biomni.example.com/api
WebSocket: ws://biomni.example.com/ws
```

---

## 3. 跨域配置（开发环境）

### 3.1 Spring Boot CORS 配置

```java
// config/CorsConfig.java
@Configuration
public class CorsConfig {
    
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        
        // 允许的源
        config.addAllowedOrigin("http://localhost:3000");  // Admin 前端
        config.addAllowedOrigin("http://localhost:3001");  // Client 前端
        
        // 允许的方法
        config.addAllowedMethod("*");
        
        // 允许的头
        config.addAllowedHeader("*");
        
        // 允许携带凭证
        config.setAllowCredentials(true);
        
        // 预检请求的有效期
        config.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        
        return new CorsFilter(source);
    }
}
```

### 3.2 Python Agent CORS 配置

```python
# api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Admin 前端
        "http://localhost:3001",  # Client 前端
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 4. 安全考虑

### 4.1 URL 参数传递 Token 的安全问题

**问题**：
- ❌ Token 会出现在浏览器历史记录中
- ❌ Token 可能被日志记录
- ❌ Token 可能被第三方脚本读取

**解决方案**：

```tsx
// Client 前端 - 立即清除 URL 中的 Token
useEffect(() => {
  const token = searchParams.get('token');
  
  if (token) {
    // 1. 保存 Token
    localStorage.setItem('token', token);
    
    // 2. 立即清除 URL 中的 Token
    window.history.replaceState({}, document.title, '/');
    
    // 3. 验证 Token
    verifyToken(token);
  }
}, []);
```

### 4.2 Token 过期时间

```java
// 短期 Token（用于 SSO）
@PostMapping("/generate-sso-token")
public Result<String> generateSSOToken() {
    Long userId = getCurrentUserId();
    
    // 生成短期 Token（1小时）
    String token = jwtTokenUtil.generateToken(userId, 3600000);
    
    return Result.success(token);
}
```

### 4.3 HTTPS（生产环境必须）

```nginx
# 生产环境必须使用 HTTPS
server {
    listen 443 ssl;
    server_name biomni.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ...
}
```

---

## 5. 完整流程示例

### 5.1 开发环境（URL 参数传递）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户在 Admin 前端登录 (localhost:3000)                   │
│    ↓                                                         │
│ 2. 获得 Token，保存到 localStorage                          │
│    localStorage.setItem('token', 'eyJhbGci...')             │
│    ↓                                                         │
│ 3. 点击"进入对话"                                            │
│    ↓                                                         │
│ 4. 跳转到 Client 前端                                        │
│    http://localhost:3001/auth/sso?token=eyJhbGci...         │
│    ↓                                                         │
│ 5. Client 前端从 URL 获取 Token                              │
│    const token = searchParams.get('token')                  │
│    ↓                                                         │
│ 6. 验证 Token（调用 Spring Boot API）                       │
│    GET http://localhost:8083/api/auth/me                    │
│    Headers: Authorization: Bearer eyJhbGci...               │
│    ↓                                                         │
│ 7. Token 有效，保存到 localStorage                          │
│    localStorage.setItem('token', token)                     │
│    ↓                                                         │
│ 8. 清除 URL 中的 Token                                       │
│    window.history.replaceState({}, '', '/')                 │
│    ↓                                                         │
│ 9. 跳转到首页，开始使用对话功能                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 生产环境（Nginx 反向代理）

```
┌─────────────────────────────────────────────────────────────┐
│ 所有服务在同一个域名下                                       │
│                                                              │
│ Admin 前端:  https://biomni.com/admin                       │
│ Client 前端: https://biomni.com/                            │
│ API:         https://biomni.com/api                         │
│ WebSocket:   wss://biomni.com/ws                            │
│                                                              │
│ 优势：                                                       │
│ ✅ 没有跨域问题                                              │
│ ✅ localStorage 可以共享                                     │
│ ✅ Cookie 可以共享                                           │
│ ✅ 更安全                                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 代码示例汇总

### 6.1 Admin 前端（跳转）

```vue
<script setup>
function goToClientPortal() {
  const token = localStorage.getItem('token');
  const clientUrl = `http://localhost:3001/auth/sso?token=${encodeURIComponent(token)}`;
  window.open(clientUrl, '_blank');
}
</script>

<template>
  <button @click="goToClientPortal">进入对话</button>
</template>
```

### 6.2 Client 前端（接收）

```tsx
// pages/SSOLogin.tsx
export default function SSOLogin() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      window.history.replaceState({}, '', '/');
      navigate('/');
    }
  }, []);
  
  return <div>正在登录...</div>;
}
```

### 6.3 Spring Boot（CORS）

```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("http://localhost:3000");
        config.addAllowedOrigin("http://localhost:3001");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
```

### 6.4 Nginx（生产环境）

```nginx
server {
    listen 80;
    server_name biomni.example.com;

    location /admin {
        alias /usr/share/nginx/html/admin;
        try_files $uri $uri/ /admin/index.html;
    }

    location / {
        root /usr/share/nginx/html/client;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8083;
    }

    location /ws {
        proxy_pass http://agent:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 7. 总结

### 开发环境方案

✅ **URL 参数传递 Token**
- 简单易实现
- 需要配置 CORS
- Token 会短暂出现在 URL 中（需要立即清除）

### 生产环境方案

✅ **Nginx 反向代理（推荐）**
- 同一个域名，没有跨域问题
- localStorage 可以共享
- 更安全
- 更专业

### 关键点

1. **开发环境**：URL 参数 + CORS 配置
2. **生产环境**：Nginx 反向代理
3. **安全**：立即清除 URL 中的 Token
4. **验证**：接收 Token 后立即验证有效性

这样就完美解决了跨域和 Token 共享的问题！🎉

---

**文档版本**: v1.0  
**创建日期**: 2025-01-20  
**作者**: Biomni Team
