# 执行步骤 API 实现

## 需要添加的接口

### 1. 获取消息的执行步骤

**接口**: `GET /api/execution-steps/list?messageId=1`

**Controller**:
```java
@RestController
@RequestMapping("/api/execution-steps")
@CrossOrigin(origins = "*")
public class ExecutionStepController {
    
    @Autowired
    private ExecutionStepService executionStepService;
    
    @RequestMapping("/list")
    public BaseResult<List<ExecutionStepVO>> getExecutionSteps(
        @RequestParam Integer messageId,
        @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            List<ExecutionStepVO> steps = executionStepService.getExecutionSteps(messageId);
            return BaseResult.success(steps);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}
```

**Service**:
```java
@Service
public class ExecutionStepService {
    
    @Autowired
    private ExecutionStepDAO executionStepDAO;
    
    public List<ExecutionStepVO> getExecutionSteps(Integer messageId) {
        ExecutionStepDOExample example = new ExecutionStepDOExample();
        example.createCriteria().andMessageIdEqualTo(messageId);
        example.setOrderByClause("step_order ASC");
        
        List<ExecutionStepDO> steps = executionStepDAO.selectByExample(example);
        
        return steps.stream()
            .map(this::convertToVO)
            .collect(Collectors.toList());
    }
    
    private ExecutionStepVO convertToVO(ExecutionStepDO step) {
        ExecutionStepVO vo = new ExecutionStepVO();
        BeanUtils.copyProperties(step, vo);
        return vo;
    }
}
```

**VO**:
```java
@Data
public class ExecutionStepVO {
    private Integer id;
    private Integer conversationId;
    private Integer messageId;
    private Integer stepOrder;
    private String stepType;
    private String stepName;
    private String toolName;
    private String toolInput;
    private String toolOutput;
    private String status;
    private String errorMessage;
    private Integer durationMs;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
}
```

---

## 前端实现

### 1. 加载历史消息时获取执行步骤

```typescript
// ChatWindow.tsx
async function loadMessages() {
  const data = await conversationApi.getMessages(conversationId);
  setMessages(data);
  
  // 加载最后一条 AI 消息的执行步骤
  const lastAiMessage = data.filter(m => m.role === 'assistant').pop();
  if (lastAiMessage?.id) {
    const steps = await conversationApi.getExecutionSteps(lastAiMessage.id);
    setExecutionSteps(steps);
  }
}
```

### 2. API 调用

```typescript
// conversation.ts
async getExecutionSteps(messageId: number): Promise<ExecutionStep[]> {
  const response = await apiClient.get<ApiResponse<ExecutionStep[]>>(
    '/api/execution-steps/list',
    { params: { messageId } }
  );
  return response.data.data;
}
```

---

## 数据流

```
1. 用户打开对话
   ↓
2. 加载历史消息
   GET /api/messages/list?conversationId=1
   ↓
3. 找到最后一条 AI 消息
   ↓
4. 加载该消息的执行步骤
   GET /api/execution-steps/list?messageId=5
   ↓
5. 显示执行步骤在右侧面板
```

---

## 优势

- ✅ 执行步骤持久化保存
- ✅ 刷新页面后仍可查看
- ✅ 可以查看历史执行过程
- ✅ 便于调试和分析

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
