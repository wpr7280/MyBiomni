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
        self.start_time = datetime.now()
    
    async def process_step(self, output: str):
        """处理每个步骤的输出"""
        
        # 检查是否包含 thinking/reasoning（没有标签的文本）
        if output.strip() and '<execute>' not in output and '<observation>' not in output and '<solution>' not in output:
            self.step_order += 1
            await self.on_reasoning(output.strip())
        
        # 检查是否包含 <execute> 标签
        execute_match = re.search(r'<execute>(.*?)</execute>', output, re.DOTALL)
        if execute_match:
            self.step_order += 1
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
    
    async def on_reasoning(self, content: str):
        """推理步骤"""
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='reasoning',
            step_name='分析问题',
            status='success',
            tool_output=content[:500],  # 保存前500字符
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=100
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        # 推送到前端
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'execution_step',
            'step': {
                'id': step.id,
                'conversationId': self.conversation_id,
                'messageId': self.current_message_id or 0,
                'stepOrder': self.step_order,
                'stepType': 'reasoning',
                'stepName': '分析问题',
                'toolOutput': content[:500],
                'status': 'success',
                'startedAt': step.started_at.isoformat(),
                'completedAt': step.completed_at.isoformat(),
                'durationMs': 100
            }
        })
    
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
                'conversationId': self.conversation_id,
                'messageId': self.current_message_id or 0,
                'stepOrder': self.step_order,
                'stepType': 'tool_call',
                'toolName': tool_name,
                'toolInput': tool_input,
                'status': 'running',
                'startedAt': step.started_at.isoformat()
            }
        })
    
    async def on_tool_result(self, tool_output: str):
        """工具结果 - 创建新的 result 类型步骤"""
        self.step_order += 1
        
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='result',
            step_name='执行结果',
            tool_output=tool_output,
            status='success',
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=50
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        self.total_duration_ms += step.duration_ms
        
        # 推送到前端
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'execution_step',
            'step': {
                'id': step.id,
                'conversationId': self.conversation_id,
                'messageId': self.current_message_id or 0,
                'stepOrder': self.step_order,
                'stepType': 'result',
                'stepName': '执行结果',
                'toolOutput': tool_output,
                'status': 'success',
                'startedAt': step.started_at.isoformat(),
                'completedAt': step.completed_at.isoformat(),
                'durationMs': step.duration_ms
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
            'conversationId': self.conversation_id,
            'role': 'assistant',
            'content': assistant_message.content,
            'contentType': 'markdown',
            'tokens': assistant_message.tokens,
            'inputTokens': assistant_message.input_tokens,
            'outputTokens': assistant_message.output_tokens,
            'createdAt': assistant_message.created_at.isoformat()
        }
