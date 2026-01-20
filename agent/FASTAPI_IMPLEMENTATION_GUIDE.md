# FastAPI Agent 服务实现指南

## 项目结构

```
agent/
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI 主应用
│   └── websocket.py        # WebSocket 路由
├── services/
│   ├── __init__.py
│   ├── agent_service.py    # Agent 执行服务（已创建）
│   └── callback.py         # 回调处理器
├── models/
│   ├── __init__.py
│   └── models.py           # SQLAlchemy 模型（已创建）
├── core/
│   ├── __init__.py
│   ├── config.py           # 配置（已创建）
│   ├── security.py         # JWT 验证（已创建）
│   └── database.py         # 数据库连接（已创建）
├── biomni/                 # Biomni Agent 核心（已存在）
│   └── agent/
│       └── a1.py
├── requirements-api.txt    # API 依赖（已创建）
├── .env                    # 环境变量
└── main.py                 # 启动文件
```

---

## 已创建的文件

1. ✅ `core/config.py` - 配置管理
2. ✅ `core/security.py` - JWT 验证
3. ✅ `core/database.py` - 数据库连接
4. ✅ `models/models.py` - 数据模型
5. ✅ `services/agent_service.py` - Agent 服务
6. ✅ `requirements-api.txt` - 依赖列表

---

## 需要创建的文件

### 1. api/app.py（FastAPI 主应用）

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.websocket import router as websocket_router
from core.config import settings

app = FastAPI(
    title="Biomni Agent API",
    description="Biomni Agent WebSocket 服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

@app.get("/")
async def root():
    return {"message": "Biomni Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2. api/websocket.py（WebSocket 路由）

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict
import json

from core.security import verify_jwt_token, get_user_id_from_token
from core.database import get_db
from services.agent_service import AgentService
from services.callback import WebSocketCallback

router = APIRouter()

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
    
    def disconnect(self, conversation_id: str):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
    
    async def send_message(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            try:
                await self.active_connections[conversation_id].send_json(message)
            except Exception as e:
                print(f"发送消息失败: {e}")

manager = ConnectionManager()

@router.websocket("/chat/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket 连接处理"""
    
    # 1. 验证 Token
    payload = verify_jwt_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = int(payload.get("sub"))
    
    # 2. 建立连接
    await manager.connect(conversation_id, websocket)
    
    try:
        while True:
            # 接收前端消息
            data = await websocket.receive_json()
            
            if data['type'] == 'send_message':
                # 执行 Agent
                await handle_agent_execution(
                    conversation_id=int(conversation_id),
                    user_id=user_id,
                    content=data['content'],
                    manager=manager,
                    db=db
                )
    
    except WebSocketDisconnect:
        manager.disconnect(conversation_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(conversation_id)

async def handle_agent_execution(
    conversation_id: int,
    user_id: int,
    content: str,
    manager: ConnectionManager,
    db: Session
):
    """执行 Agent 并推送结果"""
    
    try:
        # 1. 通知开始执行
        await manager.send_message(str(conversation_id), {
            'type': 'execution_start'
        })
        
        # 2. 创建回调处理器
        callback = WebSocketCallback(
            conversation_id=conversation_id,
            manager=manager,
            db=db
        )
        
        # 3. 执行 Agent（流式）
        result = await AgentService.execute_agent_stream(
            conversation_id=conversation_id,
            user_id=user_id,
            query=content,
            callback=callback
        )
        
        # 4. 通知完成
        await manager.send_message(str(conversation_id), {
            'type': 'execution_complete',
            'message': result
        })
        
    except Exception as e:
        await manager.send_message(str(conversation_id), {
            'type': 'execution_error',
            'error': str(e)
        })
```

### 3. services/callback.py（回调处理器）

```python
from datetime import datetime
from models.models import Message, ExecutionStep, Conversation
import json
import re

class WebSocketCallback:
    """WebSocket 回调处理器"""
    
    def __init__(self, conversation_id: int, manager, db):
        self.conversation_id = conversation_id
        self.manager = manager
        self.db = db
        self.step_order = 0
        self.current_message_id = None
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_duration_ms = 0
        self.final_content = ""
    
    async def process_step(self, output: str):
        """处理每个步骤的输出"""
        self.step_order += 1
        
        # 解析输出，提取执行步骤信息
        # 这里需要根据 a1.py 的输出格式来解析
        
        # 检查是否包含 <execute> 标签
        execute_match = re.search(r'<execute>(.*?)</execute>', output, re.DOTALL)
        if execute_match:
            code = execute_match.group(1).strip()
            await self.on_tool_call('execute_code', {'code': code})
        
        # 检查是否包含 <observation> 标签
        observation_match = re.search(r'<observation>(.*?)</observation>', output, re.DOTALL)
        if observation_match:
            observation = observation_match.group(1).strip()
            await self.on_tool_result(observation)
        
        # 检查是否包含 <solution> 标签
        solution_match = re.search(r'<solution>(.*?)</solution>', output, re.DOTALL)
        if solution_match:
            self.final_content = solution_match.group(1).strip()
    
    async def on_tool_call(self, tool_name: str, tool_input: dict):
        """工具调用"""
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='tool_call',
            tool_name=tool_name,
            tool_input=json.dumps(tool_input),
            status='running',
            started_at=datetime.now()
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        # 推送到前端
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'execution_step',
            'step': {
                'id': step.id,
                'step_type': 'tool_call',
                'tool_name': tool_name,
                'tool_input': tool_input,
                'status': 'running',
                'started_at': step.started_at.isoformat()
            }
        })
    
    async def on_tool_result(self, tool_output: str):
        """工具结果"""
        # 更新最后一个步骤
        step = self.db.query(ExecutionStep).filter(
            ExecutionStep.conversation_id == self.conversation_id,
            ExecutionStep.step_order == self.step_order
        ).first()
        
        if step:
            step.tool_output = tool_output
            step.status = 'success'
            step.completed_at = datetime.now()
            step.duration_ms = int((step.completed_at - step.started_at).total_seconds() * 1000)
            self.db.commit()
            
            self.total_duration_ms += step.duration_ms
            
            # 推送到前端
            await self.manager.send_message(str(self.conversation_id), {
                'type': 'execution_step',
                'step': {
                    'id': step.id,
                    'tool_output': tool_output,
                    'status': 'success',
                    'completed_at': step.completed_at.isoformat(),
                    'duration_ms': step.duration_ms
                }
            })
    
    def get_result(self):
        """获取最终结果"""
        # 保存 AI 消息
        assistant_message = Message(
            conversation_id=self.conversation_id,
            role='assistant',
            content=self.final_content,
            content_type='markdown',
            tokens=self.total_input_tokens + self.total_output_tokens,
            input_tokens=self.total_input_tokens,
            output_tokens=self.total_output_tokens,
            created_at=datetime.now()
        )
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)
        
        # 更新对话统计
        conversation = self.db.query(Conversation).get(self.conversation_id)
        if conversation:
            conversation.message_count += 1
            conversation.total_tokens += assistant_message.tokens
            conversation.total_duration_ms += self.total_duration_ms
            conversation.last_message_at = datetime.now()
            conversation.updated_at = datetime.now()
            self.db.commit()
        
        return {
            'id': assistant_message.id,
            'role': 'assistant',
            'content': assistant_message.content,
            'tokens': assistant_message.tokens,
            'created_at': assistant_message.created_at.isoformat()
        }
```

### 4. main.py（启动文件）

```python
import uvicorn
from api.app import app

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### 5. .env（环境变量）

```env
# JWT 配置（与 Spring Boot 共享）
JWT_SECRET_KEY=your-shared-secret-key-here
JWT_ALGORITHM=HS256

# Spring Boot API
SPRING_BOOT_URL=http://localhost:8083
INTERNAL_SECRET=your-internal-api-secret

# 数据库
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/biomni_app

# Agent 配置
AGENT_DATA_PATH=./data
DEFAULT_LLM=claude-sonnet-4-5
DEFAULT_TEMPERATURE=0.7

# CORS
CORS_ORIGINS=["http://localhost:3001","http://localhost:3000"]
```

---

## 启动步骤

### 1. 安装依赖

```bash
cd agent
pip install -r requirements-api.txt
pip install -r requirements.txt  # Biomni Agent 依赖
```

### 2. 配置环境变量

创建 `.env` 文件，填入上述配置

### 3. 启动服务

```bash
python main.py
```

服务将在 http://localhost:8000 启动

---

## 关键实现点

### 1. Agent 实例池

```python
agent_pool: Dict[int, A1] = {}

def get_or_create_agent(user_id: int) -> A1:
    if user_id not in agent_pool:
        agent_pool[user_id] = A1(path='./data', llm='claude-sonnet-4-5')
    return agent_pool[user_id]
```

### 2. 使用 go_stream 流式执行

```python
for step in agent.go_stream(query):
    output = step.get('output', '')
    await callback.process_step(output)
```

### 3. thread_id 使用对话 ID

在 A1 的 go_stream 方法中，config 参数：

```python
config = {"recursion_limit": 500, "configurable": {"thread_id": conversation_id}}
```

需要修改 `agent_service.py` 中的调用。

---

## 下一步

由于代码量较大，建议：

1. 先创建基础文件结构
2. 测试 WebSocket 连接
3. 集成 Biomni Agent
4. 测试流式输出
5. 完善回调处理

完整代码已经规划好，可以按照这个指南逐步实现！

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
