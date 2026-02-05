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
        self.pending_tool_call_steps = []  # 保存待更新的 tool_call 步骤（栈）
        self.plan_items = []  # 规划步骤列表
        self.plan_step = None  # 规划步骤的 ExecutionStep（用于更新）
        self.current_plan_index = None  # 当前进行中的 plan 序号

    def _normalize_output(self, output: str) -> str:
        """清理 pretty_print 头部与 ANSI，并过滤 Human Message。"""
        if not output:
            return ""

        # 去除 ANSI 颜色码
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)

        lines = output.splitlines()
        if lines and re.match(r"^=+ .* Message =+$", lines[0]):
            # Human Message 直接跳过（避免把用户输入当 reasoning）
            if "Human Message" in lines[0]:
                return ""
            # 去掉头部、Name 行、空行
            lines = lines[1:]
            if lines and lines[0].startswith("Name:"):
                lines = lines[1:]
            if lines and lines[0].strip() == "":
                lines = lines[1:]
            output = "\n".join(lines)

        # 兼容旧逻辑的分隔符清理
        output = output.replace('================================== Ai Message ==================================', '')
        output = output.replace('================================ Human Message =================================', '')
        return output.strip()

    def _extract_plan_items(self, text: str) -> list[dict]:
        """从输出中提取 Plan 列表项（1. [ ] xxx）。仅取首个 Plan 区块，避免重复。"""
        lines = text.splitlines()
        checkbox_re = re.compile(r"^\s*(\d+)\.\s+\[( |x|X|✓)\]\s+(.*\S)\s*$")
        checkmark_re = re.compile(r"^\s*(\d+)\.\s+(✓|☑)\s+(.*\S)\s*$")

        # 1) 优先从 “Plan” 标题之后提取
        start_idx = None
        for i, line in enumerate(lines):
            if re.match(r"^\s*(#+\s*)?Plan\b", line, re.IGNORECASE):
                start_idx = i + 1
                break

        # 2) 如果没有标题，则寻找首个连续的 checkbox 区块
        if start_idx is None:
            for i, line in enumerate(lines):
                if checkbox_re.match(line):
                    start_idx = i
                    break

        if start_idx is None:
            return []

        items = []
        seen = set()
        started = False
        for line in lines[start_idx:]:
            if line.strip() == "":
                if started:
                    break
                continue

            match = checkbox_re.match(line)
            if match:
                started = True
                index = int(match.group(1))
                checked = match.group(2) in ("x", "X", "✓")
                title = match.group(3).strip()
                key = (index, title)
                if key in seen:
                    continue
                seen.add(key)
                items.append({"index": index, "title": title, "done": checked})
                continue
            match = checkmark_re.match(line)
            if match:
                started = True
                index = int(match.group(1))
                title = match.group(3).strip()
                key = (index, title)
                if key in seen:
                    continue
                seen.add(key)
                items.append({"index": index, "title": title, "done": True})
                continue

            # 遇到非 checkbox 行，且已经开始收集，则结束
            if started:
                break

        if len(items) >= 2:
            return items
        return []

    def _merge_plan_items(self, new_items: list[dict]) -> bool:
        """合并 plan 状态，返回是否发生更新。"""
        if not new_items:
            return False
        updated = False
        if not self.plan_items:
            self.plan_items = new_items
            return True
        # 按 index 合并 done 状态与标题
        for item in new_items:
            idx = item["index"]
            for existing in self.plan_items:
                if existing["index"] == idx:
                    if existing["done"] != item["done"]:
                        existing["done"] = item["done"]
                        updated = True
                    if existing["title"] != item["title"]:
                        existing["title"] = item["title"]
                        updated = True
                    break
        return updated

    def _render_plan_markdown(self) -> str:
        lines = ["## Plan", ""]
        for item in sorted(self.plan_items, key=lambda x: x["index"]):
            mark = "✓" if item["done"] else "[ ]"
            suffix = ""
            if self.current_plan_index == item["index"] and not item["done"]:
                suffix = " (in progress)"
            if item["done"]:
                lines.append(f"{item['index']}. {mark} {item['title']}{suffix}")
            else:
                lines.append(f"{item['index']}. {mark} {item['title']}{suffix}")
        return "\n".join(lines)

    def _clean_reasoning_segment(self, content: str) -> str:
        """清理非标签文本片段，去掉 Plan 列表与 Step 状态行。"""
        content = content.replace("<function_calls>", "").replace("</function_calls>", "")
        lines = content.splitlines()
        cleaned = []
        skipping_plan = False

        checkbox_re = re.compile(r"^\s*\d+\.\s+\[( |x|X|✓)\]\s+.*\S$")
        checkmark_re = re.compile(r"^\s*\d+\.\s+(✓|☑)\s+.*\S$")
        step_status_re = re.compile(r"^\s*\[.*\]\s*Step\b", re.IGNORECASE)

        for line in lines:
            if re.match(r"^\s*(#+\s*)?Plan\b", line, re.IGNORECASE):
                skipping_plan = True
                continue

            if skipping_plan:
                if checkbox_re.match(line) or line.strip() == "":
                    continue
                # 非计划项，结束跳过
                skipping_plan = False

            if checkbox_re.match(line) or checkmark_re.match(line):
                continue
            if step_status_re.match(line):
                continue

            cleaned.append(line)

        cleaned_text = "\n".join(cleaned).strip()
        return cleaned_text

    async def _upsert_plan_step(self):
        """创建或更新 Plan 步骤。"""
        if not self.plan_items:
            return

        content = self._render_plan_markdown()
        if self.plan_step is None:
            self.step_order += 1
            step = ExecutionStep(
                conversation_id=self.conversation_id,
                message_id=self.current_message_id or 0,
                step_order=self.step_order,
                step_type='reasoning',
                step_name='🗺️ Plan',
                status='success',
                tool_output=content,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_ms=50
            )
            self.db.add(step)
            self.db.commit()
            self.db.refresh(step)
            self.plan_step = step

            await self.manager.send_message(str(self.conversation_id), {
                'type': 'execution_step',
                'step': {
                    'id': step.id,
                    'conversationId': self.conversation_id,
                    'messageId': self.current_message_id or 0,
                    'stepOrder': self.step_order,
                    'stepType': 'reasoning',
                    'stepName': '🗺️ Plan',
                    'toolOutput': content,
                    'status': 'success',
                    'startedAt': step.started_at.isoformat(),
                    'completedAt': step.completed_at.isoformat(),
                    'durationMs': step.duration_ms
                }
            })
        else:
            self.plan_step.tool_output = content
            self.plan_step.completed_at = datetime.now()
            self.db.commit()

            await self.manager.send_message(str(self.conversation_id), {
                'type': 'execution_step',
                'step': {
                    'id': self.plan_step.id,
                    'conversationId': self.conversation_id,
                    'messageId': self.current_message_id or 0,
                    'stepOrder': self.plan_step.step_order,
                    'stepType': 'reasoning',
                    'stepName': self.plan_step.step_name,
                    'toolOutput': content,
                    'status': 'success',
                    'startedAt': self.plan_step.started_at.isoformat(),
                    'completedAt': self.plan_step.completed_at.isoformat(),
                    'durationMs': self.plan_step.duration_ms
                }
            })

    def _advance_plan_on_execute(self) -> bool:
        """通用策略：每次 execute 开始时，将下一个未完成的 plan 标记为进行中。"""
        if not self.plan_items:
            return False
        if self.current_plan_index is not None:
            return False
        for item in sorted(self.plan_items, key=lambda x: x["index"]):
            if not item["done"]:
                self.current_plan_index = item["index"]
                return True
        return False

    def _complete_plan_on_observation(self) -> bool:
        """通用策略：每次 observation 完成时，完成当前进行中的 plan。"""
        if self.current_plan_index is None:
            return False
        updated = False
        for item in self.plan_items:
            if item["index"] == self.current_plan_index:
                if not item["done"]:
                    item["done"] = True
                    updated = True
                break
        self.current_plan_index = None
        return updated
    
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
        
        # 清理输出，移除分隔符 & pretty_print 头部
        output = self._normalize_output(output)
        
        if not output:
            return
        
        # 使用 stderr 输出调试日志
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"📝 Processing output (length: {len(output)})", file=sys.stderr)
        print(f"   First 200 chars: {output[:200]}...", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        # Plan 提取与更新
        new_plan_items = self._extract_plan_items(output)
        if new_plan_items:
            if self._merge_plan_items(new_plan_items):
                await self._upsert_plan_step()
        
        # 🔴 关键修复：按顺序处理所有部分，不要提前返回
        
        # 1. 解析标签与非标签片段（支持中间 reasoning）
        tag_re = re.compile(r'<(execute|observation|observe|solution)>(.*?)</\1>', re.DOTALL)
        matches = list(tag_re.finditer(output))

        if not matches:
            # 全部作为 reasoning 处理
            cleaned = self._clean_reasoning_segment(output)
            if cleaned and len(cleaned) > 10:
                print(f"   ✓ 无标签，作为 reasoning 处理 (length: {len(cleaned)})", file=sys.stderr)
                await self.on_reasoning(cleaned)
            return

        cursor = 0
        for match in matches:
            # 处理标签前的文本片段
            if match.start() > cursor:
                text_segment = output[cursor:match.start()]
                cleaned = self._clean_reasoning_segment(text_segment)
                if cleaned and len(cleaned) > 10:
                    print(f"   ✓ 检测到 reasoning 片段 (length: {len(cleaned)})", file=sys.stderr)
                    await self.on_reasoning(cleaned)

            tag = match.group(1)
            body = match.group(2).strip()

            if tag == "execute":
                print("   ✓ 检测到 <execute> 标签", file=sys.stderr)
                code = body

                # 检测代码语言
                language = "python"
                if code.strip().startswith("#!R"):
                    language = "r"
                    code = re.sub(r"^#!R", "", code, count=1).strip()
                elif code.strip().startswith("#!BASH") or code.strip().startswith("#!CLI"):
                    language = "bash"
                    code = re.sub(r"^#!BASH|^#!CLI", "", code, count=1).strip()

                await self.on_tool_call('execute_code', {'code': code, 'language': language})
                if self._advance_plan_on_execute():
                    await self._upsert_plan_step()
            elif tag in ("observe", "observation"):
                print(f"   ✓ 检测到 <{tag}> 标签", file=sys.stderr)
                await self.on_tool_result(body)
                if self._complete_plan_on_observation():
                    await self._upsert_plan_step()
            elif tag == "solution":
                print("   ✓ 检测到 <solution> 标签", file=sys.stderr)
                self.final_content = body

            cursor = match.end()

        # 处理最后一个标签后的文本片段
        if cursor < len(output):
            tail_segment = output[cursor:]
            cleaned = self._clean_reasoning_segment(tail_segment)
            if cleaned and len(cleaned) > 10:
                print(f"   ✓ 检测到 reasoning 片段 (length: {len(cleaned)})", file=sys.stderr)
                await self.on_reasoning(cleaned)
    
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

        self.step_order += 1
        
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
        self.pending_tool_call_steps.append(step)
        
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
        if self.pending_tool_call_steps:
            pending_step = self.pending_tool_call_steps.pop()
            pending_step.status = 'success'
            pending_step.completed_at = datetime.now()
            pending_step.duration_ms = int(
                (pending_step.completed_at - pending_step.started_at).total_seconds() * 1000
            )
            self.db.commit()
            
            print(f"✓ Updated tool_call step {pending_step.step_order} to success", file=sys.stderr)
            
            # 推送更新到前端
            await self.manager.send_message(str(self.conversation_id), {
                'type': 'execution_step',
                'step': {
                    'id': pending_step.id,
                    'conversationId': self.conversation_id,
                    'messageId': self.current_message_id or 0,
                    'stepOrder': pending_step.step_order,
                    'stepType': 'tool_call',
                    'stepName': pending_step.step_name,
                    'toolName': pending_step.tool_name,
                    'toolInput': json.loads(pending_step.tool_input) if pending_step.tool_input else {},
                    'status': 'success',
                    'startedAt': pending_step.started_at.isoformat(),
                    'completedAt': pending_step.completed_at.isoformat(),
                    'durationMs': pending_step.duration_ms
                }
            })
        
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
