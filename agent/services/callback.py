from datetime import datetime
from models.models import Message, ExecutionStep, Conversation
import json
import re

class WebSocketCallback:
    """WebSocket 回调处理器 - 匹配 A1 的输出格式"""
    
    def __init__(self, conversation_id: int, manager, db, user_id: int):
        self.conversation_id = conversation_id
        self.manager = manager
        self.db = db
        self.user_id = user_id
        self.step_order = 0
        self.current_message_id = None
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_duration_ms = 0
        self.final_content = ""
        self.start_time = datetime.now()
        self.pending_tool_call_step = None  # 保存待更新的 tool_call 步骤
    
    async def process_step(self, output: str, usage: dict = None):
        """处理每个步骤的输出 - 匹配 A1 的流式输出格式"""
        
        # 累计 Token 使用量
        if usage:
            self.total_input_tokens += usage.get('input_tokens', 0)
            self.total_output_tokens += usage.get('output_tokens', 0)
        
        # 提取 thinking/reasoning 部分（标签之前的文本）
        tag_positions = []
        for tag in ["<execute>", "<solution>", "<observation>"]:
            pos = output.find(tag)
            if pos != -1:
                tag_positions.append(pos)
        
        # 如果有标签，提取标签前的思考内容
        if tag_positions:
            first_tag_pos = min(tag_positions)
            thinking = output[:first_tag_pos].strip()
            if thinking:
                self.step_order += 1
                await self.on_reasoning(thinking)
        
        # 检查是否包含 <execute> 标签
        execute_match = re.search(r'<execute>(.*?)</execute>', output, re.DOTALL)
        if execute_match:
            self.step_order += 1
            code = execute_match.group(1).strip()
            
            # 检测代码语言
            language = "python"
            if code.strip().startswith("#!R"):
                language = "r"
                code = re.sub(r"^#!R", "", code, count=1).strip()
            elif code.strip().startswith("#!BASH") or code.strip().startswith("#!CLI"):
                language = "bash"
                code = re.sub(r"^#!BASH|^#!CLI", "", code, count=1).strip()
            
            await self.on_tool_call('execute_code', {'code': code, 'language': language})
        
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
        """推理步骤 - 显示 AI 的思考过程"""
        # 清理内容，移除不必要的分隔符
        content = content.replace('================================== Ai Message ==================================', '')
        content = content.replace('================================ Human Message =================================', '')
        content = content.strip()
        
        if not content:
            return
        
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='reasoning',
            step_name='🤔 Reasoning',
            status='success',
            tool_output=content,
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
                'stepName': '🤔 Reasoning',
                'toolOutput': content,
                'status': 'success',
                'startedAt': step.started_at.isoformat(),
                'completedAt': step.completed_at.isoformat(),
                'durationMs': 100
            }
        })
    
    async def on_tool_call(self, tool_name: str, tool_input: dict):
        """工具调用 - 显示正在执行的代码"""
        code = tool_input.get('code', '')
        language = tool_input.get('language', 'python')
        
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='tool_call',
            step_name=f'🛠️ Executing {language.upper()} code',
            tool_name=tool_name,
            tool_input=json.dumps({'code': code, 'language': language}),
            status='running',
            started_at=datetime.now()
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        # 保存这个步骤，等待 observation 时更新
        self.pending_tool_call_step = step
        
        # 推送到前端 - 代码在 toolInput 中
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'execution_step',
            'step': {
                'id': step.id,
                'conversationId': self.conversation_id,
                'messageId': self.current_message_id or 0,
                'stepOrder': self.step_order,
                'stepType': 'tool_call',
                'stepName': f'🛠️ Executing {language.upper()} code',
                'toolName': tool_name,
                'toolInput': {'code': code, 'language': language},
                'status': 'running',
                'startedAt': step.started_at.isoformat()
            }
        })
    
    async def on_tool_result(self, tool_output: str):
        """工具结果 - 显示执行结果，并检测生成的图片"""
        # 更新之前的 tool_call 步骤状态
        if self.pending_tool_call_step:
            self.pending_tool_call_step.status = 'success'
            self.pending_tool_call_step.completed_at = datetime.now()
            self.pending_tool_call_step.duration_ms = int(
                (self.pending_tool_call_step.completed_at - self.pending_tool_call_step.started_at).total_seconds() * 1000
            )
            self.db.commit()
            
            # 推送更新到前端
            await self.manager.send_message(str(self.conversation_id), {
                'type': 'execution_step',
                'step': {
                    'id': self.pending_tool_call_step.id,
                    'conversationId': self.conversation_id,
                    'messageId': self.current_message_id or 0,
                    'stepOrder': self.pending_tool_call_step.step_order,
                    'stepType': 'tool_call',
                    'stepName': self.pending_tool_call_step.step_name,
                    'toolName': self.pending_tool_call_step.tool_name,
                    'toolInput': json.loads(self.pending_tool_call_step.tool_input) if self.pending_tool_call_step.tool_input else {},
                    'status': 'success',
                    'startedAt': self.pending_tool_call_step.started_at.isoformat(),
                    'completedAt': self.pending_tool_call_step.completed_at.isoformat(),
                    'durationMs': self.pending_tool_call_step.duration_ms
                }
            })
            
            self.pending_tool_call_step = None
        
        # 检测输出中的图片文件
        images = self._extract_images_from_output(tool_output)
        
        # 创建新的 result 步骤
        self.step_order += 1
        
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='result',
            step_name='📋 Observation',
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
                'stepName': '📋 Observation',
                'toolOutput': tool_output,
                'images': images,  # 添加图片数据
                'status': 'success',
                'startedAt': step.started_at.isoformat(),
                'completedAt': step.completed_at.isoformat(),
                'durationMs': step.duration_ms
            }
        })
    
    def _extract_images_from_output(self, output: str) -> list:
        """从输出中提取图片文件路径并转为 base64"""
        import os
        import base64
        
        images = []
        
        # 支持的图片格式
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        
        # 使用正则提取文件路径
        file_patterns = [
            r"saved to[:\s]+['\"]?([^'\"\s]+\.(?:png|jpg|jpeg|gif|bmp|webp))['\"]?",
            r"Plot saved to[:\s]+['\"]?([^'\"\s]+\.(?:png|jpg|jpeg|gif|bmp|webp))['\"]?",
            r"Figure saved as[:\s]+['\"]?([^'\"\s]+\.(?:png|jpg|jpeg|gif|bmp|webp))['\"]?",
            r"Saved (?:visualization|plot|figure) to[:\s]+['\"]?([^'\"\s]+\.(?:png|jpg|jpeg|gif|bmp|webp))['\"]?",
            r"([^\s]+\.(?:png|jpg|jpeg|gif|bmp|webp))",  # 通用匹配
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for match in matches:
                file_path = match.strip("'\"")
                
                # 尝试多个可能的路径
                possible_paths = [
                    file_path,  # 原始路径
                    os.path.join(os.getcwd(), file_path),  # 当前目录
                    os.path.join('./data', file_path),  # data 目录
                    os.path.join('./data/biomni_data', file_path),  # biomni_data 目录
                ]
                
                for path in possible_paths:
                    if os.path.exists(path) and path.lower().endswith(image_extensions):
                        try:
                            with open(path, 'rb') as f:
                                image_data = base64.b64encode(f.read()).decode('utf-8')
                                # 检测图片格式
                                ext = os.path.splitext(path)[1][1:].lower()
                                mime_type = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'
                                
                                images.append({
                                    'filename': os.path.basename(path),
                                    'data': f'data:{mime_type};base64,{image_data}',
                                    'path': path
                                })
                                print(f"✓ 检测到图片: {path}")
                                break  # 找到就跳出
                        except Exception as e:
                            print(f"读取图片失败 {path}: {e}")
                            continue
        
        return images
    
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
        
        # 更新用户配额
        from models.models import UserQuota
        
        quota = self.db.query(UserQuota).filter(UserQuota.user_id == self.user_id).first()
        if quota:
            quota.total_token_used += (self.total_input_tokens + self.total_output_tokens)
            quota.updated_at = datetime.now()
            self.db.commit()
        
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
