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
        """处理每个步骤的输出 - 完整处理所有标签
        
        注意：一个输出可能包含多个部分（thinking + execute + observe）
        需要全部处理，不能只处理一个就返回
        """
        import sys
        
        # 累计 Token 使用量
        if usage:
            self.total_input_tokens += usage.get('input_tokens', 0)
            self.total_output_tokens += usage.get('output_tokens', 0)
        
        # 清理输出，移除分隔符
        output = output.replace('================================== Ai Message ==================================', '')
        output = output.replace('================================ Human Message =================================', '')
        output = output.strip()
        
        if not output:
            return
        
        # 使用 stderr 输出调试日志
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"📝 Processing output (length: {len(output)})", file=sys.stderr)
        print(f"   First 200 chars: {output[:200]}...", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        
        # 🔴 关键修复：按顺序处理所有部分，不要提前返回
        
        # 1. 提取 thinking/reasoning 部分（标签之前的文本）
        tag_positions = []
        for tag in ["<execute>", "<solution>", "<observe>", "<observation>", "<function_calls>"]:
            pos = output.find(tag)
            if pos != -1:
                tag_positions.append((pos, tag))
        
        # 如果有标签，提取标签前的思考内容
        if tag_positions:
            first_tag_pos = min(tag_positions, key=lambda x: x[0])[0]
            thinking = output[:first_tag_pos].strip()
            if thinking and len(thinking) > 10:
                print(f"   ✓ 检测到 thinking 内容 (length: {len(thinking)})", file=sys.stderr)
                self.step_order += 1
                await self.on_reasoning(thinking)
        elif len(output) > 10:
            print(f"   ✓ 无标签，作为 reasoning 处理 (length: {len(output)})", file=sys.stderr)
            self.step_order += 1
            await self.on_reasoning(output)
            return  # 如果没有标签，处理完就返回
        
        # 2. 检查并处理 <execute> 标签
        execute_match = re.search(r'<execute>(.*?)</execute>', output, re.DOTALL)
        if execute_match:
            print("   ✓ 检测到 <execute> 标签", file=sys.stderr)
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
        
        # 3. 检查并处理 <observe> 标签（A1 实际使用的标签）
        observe_match = re.search(r'<observe>(.*?)</observe>', output, re.DOTALL)
        if observe_match:
            print("   ✓ 检测到 <observe> 标签", file=sys.stderr)
            observation = observe_match.group(1).strip()
            await self.on_tool_result(observation)
        
        # 4. 检查并处理 <observation> 标签（备用）
        observation_match = re.search(r'<observation>(.*?)</observation>', output, re.DOTALL)
        if observation_match:
            print("   ✓ 检测到 <observation> 标签", file=sys.stderr)
            observation = observation_match.group(1).strip()
            await self.on_tool_result(observation)
        
        # 5. 检查并处理 <solution> 标签
        solution_match = re.search(r'<solution>(.*?)</solution>', output, re.DOTALL)
        if solution_match:
            print("   ✓ 检测到 <solution> 标签", file=sys.stderr)
            self.final_content = solution_match.group(1).strip()
    
    async def on_reasoning(self, content: str):
        """推理步骤 - 显示 AI 的思考过程（不拆分，保持完整）"""
        import sys
        
        # 清理内容
        content = content.replace('================================== Ai Message ==================================', '')
        content = content.replace('================================ Human Message =================================', '')
        content = content.replace('<function_calls>', '')
        content = content.replace('</function_calls>', '')
        content = content.strip()
        
        if not content or len(content) < 5:
            return
        
        # 简单策略：不拆分，保持完整
        # 只限制最大长度
        if len(content) > 8000:
            content = content[:8000] + "\n... (content truncated for display)"
        
        self.step_order += 1
        
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
        
        print(f"✓ Saved reasoning step {self.step_order}: {content[:100]}...", file=sys.stderr)
        
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
        import sys
        
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
        
        print(f"✓ Saved tool_call step {self.step_order}: {language} code ({len(code)} chars)", file=sys.stderr)
        
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
        """工具结果 - 显示执行结果（不拆分，保持完整）"""
        import sys
        
        # 更新之前的 tool_call 步骤状态
        if self.pending_tool_call_step:
            self.pending_tool_call_step.status = 'success'
            self.pending_tool_call_step.completed_at = datetime.now()
            self.pending_tool_call_step.duration_ms = int(
                (self.pending_tool_call_step.completed_at - self.pending_tool_call_step.started_at).total_seconds() * 1000
            )
            self.db.commit()
            
            print(f"✓ Updated tool_call step {self.pending_tool_call_step.step_order} to success", file=sys.stderr)
            
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
        
        # 简单策略：不拆分，保持完整
        # 只限制最大长度
        if len(tool_output) > 10000:
            tool_output = tool_output[:10000] + "\n... (content truncated for display)"
        
        # 检测输出中的图片文件
        images = self._extract_images_from_output(tool_output)
        
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
        
        print(f"✓ Saved result step {self.step_order}: {tool_output[:100]}...", file=sys.stderr)
        
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
                'images': images,
                'status': 'success',
                'startedAt': step.started_at.isoformat(),
                'completedAt': step.completed_at.isoformat(),
                'durationMs': step.duration_ms
            }
        })
    
    def _extract_images_from_output(self, output: str) -> list:
        """从输出中提取图片文件路径并转为 base64（参考 Gradio demo 的简化逻辑）"""
        import os
        import base64
        import sys
        
        images = []
        
        # 支持的图片格式（与 Gradio demo 一致）
        SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        
        # 检查输出中是否包含图片文件扩展名
        if not any(ext in output for ext in SUPPORTED_EXTENSIONS):
            return images
        
        # 使用简单的正则匹配文件路径（与 Gradio demo 类似）
        matches = re.findall(r'(\S+?\.(?:png|jpg|jpeg|gif|bmp|webp))', output, re.IGNORECASE)
        
        valid_matches = []
        for match in matches:
            # 过滤掉明显的错误匹配
            if not (match.startswith('Warning:') or match.startswith('Error:') or match.startswith("'")):
                if not match.startswith('.'):
                    valid_matches.append(match)
        
        for file_path in valid_matches:
            file_path = file_path.strip("\"'").strip()
            
            # 尝试多个可能的路径（与 Gradio demo 类似）
            abs_path = None
            if os.path.isabs(file_path) and os.path.exists(file_path):
                abs_path = file_path
            elif os.path.exists(os.path.join(os.getcwd(), file_path)):
                abs_path = os.path.join(os.getcwd(), file_path)
            elif os.path.exists(os.path.join('./data', file_path)):
                abs_path = os.path.join('./data', file_path)
            elif os.path.exists(os.path.join('./data/biomni_data', file_path)):
                abs_path = os.path.join('./data/biomni_data', file_path)
            
            if abs_path and abs_path.lower().endswith(SUPPORTED_EXTENSIONS):
                try:
                    with open(abs_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                        # 检测图片格式
                        ext = os.path.splitext(abs_path)[1][1:].lower()
                        mime_type = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'
                        
                        images.append({
                            'filename': os.path.basename(abs_path),
                            'data': f'data:{mime_type};base64,{image_data}',
                            'path': abs_path
                        })
                        print(f"✓ 检测到图片: {abs_path}", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️ 读取图片失败 {abs_path}: {e}", file=sys.stderr)
                    continue
        
        return images
    
    def get_result(self):
        """获取最终结果"""
        import sys
        
        print(f"📊 get_result() 开始: conversation_id={self.conversation_id}", file=sys.stderr)
        
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
        
        print(f"✓ 保存 assistant message: id={assistant_message.id}, tokens={assistant_message.tokens}", file=sys.stderr)
        
        # 更新用户配额
        from models.models import UserQuota
        
        quota = self.db.query(UserQuota).filter(UserQuota.user_id == self.user_id).first()
        if quota:
            old_used = quota.total_token_used
            quota.total_token_used += (self.total_input_tokens + self.total_output_tokens)
            quota.updated_at = datetime.now()
            self.db.commit()
            print(f"✓ 更新配额: {old_used} → {quota.total_token_used} (+{self.total_input_tokens + self.total_output_tokens})", file=sys.stderr)
        
        # 更新对话统计
        conversation = self.db.query(Conversation).get(self.conversation_id)
        if conversation:
            old_count = conversation.message_count
            old_tokens = conversation.total_tokens
            old_duration = conversation.total_duration_ms
            
            conversation.message_count += 1
            conversation.total_tokens += assistant_message.tokens
            conversation.total_duration_ms += self.total_duration_ms
            conversation.last_message_at = datetime.now()
            conversation.updated_at = datetime.now()
            self.db.commit()
            
            print(f"✓ 更新 conversation:", file=sys.stderr)
            print(f"  - message_count: {old_count} → {conversation.message_count}", file=sys.stderr)
            print(f"  - total_tokens: {old_tokens} → {conversation.total_tokens}", file=sys.stderr)
            print(f"  - total_duration_ms: {old_duration} → {conversation.total_duration_ms}", file=sys.stderr)
        else:
            print(f"⚠️ Warning: Conversation {self.conversation_id} not found!", file=sys.stderr)
        
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
