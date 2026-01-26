# 下一步工作清单

## 🎯 立即可做（5分钟）

### 1. 创建配额表
```bash
cd admin/backend/data
mysql -u root -p biomni < ../../create_quota_table.sql
```

验证：
```sql
USE biomni;
SHOW TABLES LIKE 'user_quotas';
SELECT * FROM user_quotas;
```

---

## 🔧 前端集成（30分钟）

### 1. 添加配额 API（5分钟）

创建 `client/frontend/src/api/quota.ts`：

```typescript
import { apiClient } from './client';

export interface QuotaInfo {
  totalTokenLimit: number;
  totalTokenUsed: number;
  remaining: number;
}

export const quotaApi = {
  async getQuota(): Promise<QuotaInfo> {
    try {
      const response = await apiClient.get('/api/auth/me');
      const user = response.data.data;
      return {
        totalTokenLimit: user.totalTokenLimit || 1000000,
        totalTokenUsed: user.totalTokenUsed || 0,
        remaining: (user.totalTokenLimit || 1000000) - (user.totalTokenUsed || 0)
      };
    } catch (error) {
      // 如果 API 还没实现，返回默认值
      return {
        totalTokenLimit: 1000000,
        totalTokenUsed: 0,
        remaining: 1000000
      };
    }
  }
};
```

### 2. 更新 ChatWindow 显示配额（15分钟）

修改 `client/frontend/src/components/ChatWindow.tsx`：

```typescript
import { quotaApi, QuotaInfo } from '@/api/quota';

export default function ChatWindow({ conversationId }: ChatWindowProps) {
  const [quota, setQuota] = useState<QuotaInfo>({
    totalTokenLimit: 1000000,
    totalTokenUsed: 0,
    remaining: 1000000
  });

  useEffect(() => {
    loadQuota();
  }, []);

  async function loadQuota() {
    try {
      const data = await quotaApi.getQuota();
      setQuota(data);
    } catch (error) {
      console.error('加载配额失败:', error);
    }
  }

  // 在底部显示配额
  return (
    // ...
    <div style={{ display: 'flex', gap: 10 }}>
      <Tag color={quota.remaining > 100000 ? 'success' : quota.remaining > 10000 ? 'warning' : 'error'}>
        📊 Token: {quota.totalTokenUsed.toLocaleString()} / {quota.totalTokenLimit.toLocaleString()}
      </Tag>
      <Tag color="blue">
        剩余: {quota.remaining.toLocaleString()}
      </Tag>
    </div>
  );
}
```

### 3. 处理配额不足消息（10分钟）

修改 `client/frontend/src/hooks/useWebSocket.ts`：

```typescript
// 在 WebSocket 消息处理中添加
if (data.type === 'quota_exceeded') {
  message.error({
    content: data.error || 'Token 配额已用完',
    duration: 5
  });
  setIsExecuting(false);
  
  // 更新配额显示
  if (data.quota) {
    // 通知父组件更新配额
  }
  return;
}

// 执行完成后刷新配额
if (data.type === 'execution_complete') {
  // ... 现有代码
  
  // 刷新配额
  loadQuota();
}
```

---

## 🏗️ Spring Boot 集成（可选，1小时）

### 1. 创建 UserQuota 实体和 Mapper（20分钟）

```java
// UserQuota.java
@Data
public class UserQuota {
    private Integer id;
    private Integer userId;
    private Integer totalTokenLimit;
    private Integer totalTokenUsed;
    private Date createdAt;
    private Date updatedAt;
}

// UserQuotaMapper.java
@Mapper
public interface UserQuotaMapper {
    UserQuota selectByUserId(Integer userId);
    int updateByUserId(UserQuota quota);
}
```

### 2. 更新用户信息 API（20分钟）

```java
// AuthController.java
@GetMapping("/api/auth/me")
public BaseResult<UserVO> getCurrentUser(@AuthenticationPrincipal AdminVO currentUser) {
    Admin admin = adminMapper.selectById(currentUser.getId());
    UserQuota quota = userQuotaMapper.selectByUserId(currentUser.getId());
    
    UserVO vo = new UserVO();
    vo.setId(admin.getId());
    vo.setEmail(admin.getEmail());
    vo.setUsername(admin.getUsername());
    vo.setRealName(admin.getRealName());
    vo.setAvatar(admin.getAvatar());
    
    // 添加配额信息
    if (quota != null) {
        vo.setTotalTokenLimit(quota.getTotalTokenLimit());
        vo.setTotalTokenUsed(quota.getTotalTokenUsed());
    } else {
        vo.setTotalTokenLimit(1000000);
        vo.setTotalTokenUsed(0);
    }
    
    return BaseResult.success(vo);
}
```

### 3. 创建配额管理 API（20分钟）

```java
// QuotaController.java
@RestController
@RequestMapping("/api/admin/quota")
@RequireRole("admin")
public class QuotaController {
    
    @Autowired
    private UserQuotaService userQuotaService;
    
    @PostMapping("/update")
    public BaseResult<Void> updateQuota(@RequestBody UpdateQuotaRequest request) {
        userQuotaService.updateQuota(request.getUserId(), request.getTotalTokenLimit());
        return BaseResult.success(null);
    }
    
    @PostMapping("/reset")
    public BaseResult<Void> resetQuota(@RequestBody ResetQuotaRequest request) {
        userQuotaService.resetUsage(request.getUserId());
        return BaseResult.success(null);
    }
}
```

---

## 🎨 管理后台集成（可选，1小时）

### 1. 用户列表显示配额（30分钟）

修改 `admin/frontend/src/views/system/users/index.vue`：

```vue
<!-- 添加列 -->
<el-table-column label="Token配额" width="120" align="right">
  <template #default="{ row }">
    {{ (row.totalTokenLimit || 0).toLocaleString() }}
  </template>
</el-table-column>

<el-table-column label="已使用" width="120" align="right">
  <template #default="{ row }">
    {{ (row.totalTokenUsed || 0).toLocaleString() }}
  </template>
</el-table-column>

<el-table-column label="使用率" width="100" align="center">
  <template #default="{ row }">
    <el-tag 
      :type="getUsageType(row.totalTokenUsed, row.totalTokenLimit)"
      size="small"
    >
      {{ getUsagePercent(row.totalTokenUsed, row.totalTokenLimit) }}%
    </el-tag>
  </template>
</el-table-column>

<script setup>
function getUsagePercent(used, limit) {
  if (!limit) return 0;
  return ((used / limit) * 100).toFixed(1);
}

function getUsageType(used, limit) {
  const percent = (used / limit) * 100;
  if (percent < 50) return 'success';
  if (percent < 80) return 'warning';
  return 'danger';
}
</script>
```

### 2. 编辑用户配额（30分钟）

在用户编辑对话框中添加：

```vue
<el-form-item label="Token配额" prop="totalTokenLimit">
  <el-input-number 
    v-model="formData.totalTokenLimit" 
    :min="0" 
    :step="100000"
    :controls="true"
  />
  <span style="margin-left: 10px; color: #999;">
    当前已使用: {{ (formData.totalTokenUsed || 0).toLocaleString() }}
  </span>
</el-form-item>

<el-form-item>
  <el-button 
    type="warning" 
    @click="resetQuota"
    :loading="resetting"
  >
    重置使用量
  </el-button>
  <span style="margin-left: 10px; color: #999; font-size: 12px;">
    将已使用量重置为 0
  </span>
</el-form-item>
```

---

## ✅ 测试清单

### 1. 配额检查测试
- [ ] 用户发送消息时检查配额
- [ ] 配额不足时显示错误消息
- [ ] 配额不足时阻止消息发送

### 2. Token 统计测试
- [ ] Mock Agent 返回正确的 token 数量
- [ ] Callback 正确累计 input_tokens 和 output_tokens
- [ ] 数据库正确更新 total_token_used

### 3. 前端显示测试
- [ ] 正确显示当前配额
- [ ] 正确显示已使用量
- [ ] 正确显示剩余量
- [ ] 配额不足时显示红色警告

### 4. 管理后台测试（可选）
- [ ] 用户列表显示配额信息
- [ ] 可以编辑用户配额
- [ ] 可以重置使用量

---

## 🐛 已知问题

### 1. 真实 A1 Agent 的 Token 统计
- 当前：Mock Agent 返回模拟数据
- 待做：从真实 LLM response 中提取 `usage_metadata`
- 位置：`agent/biomni/agent/a1.py`

### 2. 配额缓存优化
- 当前：每次从数据库查询
- 可选：使用 Redis 缓存，提高性能

---

## 📚 相关文档

- `QUOTA_IMPLEMENTATION_STATUS.md` - 配额功能实现状态
- `other/docs/conversion/简化配额方案.md` - 配额方案设计
- `agent/create_quota_table.sql` - 数据库脚本
- `agent/models/models.py` - UserQuota 模型
- `agent/api/websocket.py` - 配额检查逻辑
- `agent/services/callback.py` - Token 统计和配额更新

---

**优先级**：
1. 🔴 高优先级：创建配额表、前端显示配额
2. 🟡 中优先级：Spring Boot API、处理配额不足
3. 🟢 低优先级：管理后台、配额缓存优化

**预计时间**：
- 核心功能：35 分钟
- 完整功能：2.5 小时
