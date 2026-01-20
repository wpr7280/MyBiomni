# 数据库配置说明

## 错误信息

```
Access denied for user 'root'@'185.199.111.133' (using password: YES)
```

## 原因

`.env` 文件中的数据库配置不正确。

---

## 解决方案

### 1. 修改 `.env` 文件

```bash
cd agent
nano .env
```

修改数据库配置：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://用户名:密码@主机:端口/数据库名

# 示例（本地数据库）
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/biomni_app

# 示例（远程数据库）
DATABASE_URL=mysql+pymysql://biomni_user:password@192.168.1.100:3306/biomni_app
```

### 2. 参数说明

```
mysql+pymysql://用户名:密码@主机:端口/数据库名
                ↓      ↓    ↓    ↓      ↓
                user   pwd  host port   db
```

### 3. 常见配置

**本地开发**:
```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/biomni_app
```

**Docker**:
```env
DATABASE_URL=mysql+pymysql://root:password@mysql:3306/biomni_app
```

**远程服务器**:
```env
DATABASE_URL=mysql+pymysql://biomni:password@your-server.com:3306/biomni_app
```

---

## 特殊字符处理

### 密码中包含特殊字符

如果密码包含特殊字符（如 `@`, `:`, `/`, `#`, `?` 等），需要进行 URL 编码：

| 字符 | URL 编码 |
|------|----------|
| @ | %40 |
| : | %3A |
| / | %2F |
| # | %23 |
| ? | %3F |
| & | %26 |
| = | %3D |
| + | %2B |
| % | %25 |

**示例**：

密码是 `pass@word123`，需要编码为 `pass%40word123`

```env
DATABASE_URL=mysql+pymysql://root:pass%40word123@localhost:3306/biomni_app
```

### Python 自动编码

也可以使用 Python 的 `urllib.parse.quote` 来编码：

```python
from urllib.parse import quote

password = "pass@word123"
encoded_password = quote(password, safe='')
print(encoded_password)  # 输出: pass%40word123

# 完整 URL
DATABASE_URL = f"mysql+pymysql://root:{encoded_password}@localhost:3306/biomni_app"
```

### 在线工具

使用在线 URL 编码工具：
- https://www.urlencoder.org/

---

```python
# test_db.py
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/biomni_app"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("✅ 数据库连接成功！")
    connection.close()
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
```

运行测试：
```bash
python test_db.py
```

---

## 创建数据库

如果数据库不存在，需要先创建：

```sql
CREATE DATABASE IF NOT EXISTS biomni_app 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;
```

---

## 完整的 .env 示例

```env
# JWT 配置
JWT_SECRET_KEY=your-shared-secret-key-here
JWT_ALGORITHM=HS512

# 数据库（修改这里！）
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/biomni_app

# Agent 配置
AGENT_DATA_PATH=./data
DEFAULT_LLM=claude-sonnet-4-5

# Mock 模式
USE_MOCK_AGENT=true

# CORS
CORS_ORIGINS=["http://localhost:3001","http://localhost:3000"]
```

---

## 重启服务

修改配置后重启：

```bash
python main.py
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
