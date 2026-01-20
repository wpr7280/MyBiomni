# Python Agent 故障排除

## 403 Forbidden 错误

### 问题
```
INFO: connection rejected (403 Forbidden)
```

### 原因
JWT Token 验证失败，可能的原因：

1. **算法不匹配**
   - Spring Boot 使用 HS512
   - Python 配置的是 HS256

2. **密钥不匹配**
   - Spring Boot 和 Python 的密钥不一致

3. **Token 格式错误**
   - Token 已过期
   - Token 格式不正确

---

## 解决方案

### 1. 检查算法

从 Token 中可以看出算法：
```
eyJhbGciOiJIUzUxMiJ9...
```

解码 Header 部分：
```json
{
  "alg": "HS512",  // ← 这里显示算法
  "typ": "JWT"
}
```

**修复**：确保 Python 配置使用相同算法

```env
# agent/.env
JWT_ALGORITHM=HS512
```

```python
# agent/core/config.py
JWT_ALGORITHM: str = "HS512"
```

### 2. 检查密钥

**Spring Boot** (`application.yml`):
```yaml
jwt:
  secret: "your-shared-secret-key-here"
```

**Python** (`.env`):
```env
JWT_SECRET_KEY=your-shared-secret-key-here
```

**确保两边完全一致！**

### 3. 测试 Token 验证

在 Python 中测试：

```python
from jose import jwt

token = "eyJhbGci..."
secret = "your-shared-secret-key-here"

try:
    payload = jwt.decode(token, secret, algorithms=["HS512"])
    print("验证成功:", payload)
except Exception as e:
    print("验证失败:", e)
```

### 4. 添加调试日志

在 `api/websocket.py` 中添加：

```python
@router.websocket("/chat/{conversation_id}")
async def websocket_endpoint(...):
    # 添加调试日志
    print(f"收到 Token: {token[:50]}...")
    
    payload = verify_jwt_token(token)
    print(f"Token 验证结果: {payload}")
    
    if not payload:
        print("Token 验证失败！")
        await websocket.close(code=1008, reason="Invalid token")
        return
```

---

## 快速修复步骤

1. **修改 Python 配置**
   ```bash
   cd agent
   nano .env
   ```
   
   修改为：
   ```env
   JWT_ALGORITHM=HS512
   ```

2. **重启 Python 服务**
   ```bash
   python main.py
   ```

3. **刷新前端页面**
   - 重新登录获取新 Token
   - 尝试发送消息

---

## 验证成功的标志

```
INFO: WebSocket 连接建立: conversation_id=2
用户 1 连接到对话 2
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
