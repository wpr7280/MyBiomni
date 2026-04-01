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
        self.output_dir = None  # Output directory for generated files

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
        # 清理孤立的 closing tags
        content = re.sub(r'</(?:execute|observation|observe|solution)>', '', content)
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
        
        try:
            await self._process_step_inner(output, usage)
        except Exception as e:
            print(f"❌ process_step error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # 通知前端出错，但不中断整个流程
            try:
                self.step_order += 1
                step = ExecutionStep(
                    conversation_id=self.conversation_id,
                    message_id=self.current_message_id or 0,
                    step_order=self.step_order,
                    step_type='reasoning',
                    step_name='⚠️ Processing Warning',
                    status='success',
                    tool_output=f"A step encountered a processing issue: {str(e)[:200]}. Execution continues.",
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    duration_ms=0
                )
                self.db.add(step)
                self.db.commit()
                self.db.refresh(step)
                await self.manager.send_message(str(self.conversation_id), {
                    'type': 'execution_step',
                    'step': {
                        'id': step.id,
                        'conversationId': self.conversation_id,
                        'messageId': self.current_message_id or 0,
                        'stepOrder': self.step_order,
                        'stepType': 'reasoning',
                        'stepName': '⚠️ Processing Warning',
                        'toolOutput': f"A step encountered a processing issue: {str(e)[:200]}. Execution continues.",
                        'status': 'success',
                        'startedAt': step.started_at.isoformat(),
                        'completedAt': step.completed_at.isoformat(),
                        'durationMs': 0
                    }
                })
            except Exception:
                pass

    async def _process_step_inner(self, output: str, usage: dict = None):
        """process_step 的实际逻辑，被 process_step 包裹以捕获异常"""
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
            # 尝试匹配不完整的 solution 标签（AI 可能只输出 <solution>content 没有 closing tag）
            incomplete_solution = re.search(r'<solution>(.*?)$', output, re.DOTALL)
            if incomplete_solution:
                body = incomplete_solution.group(1).strip()
                if body:
                    print(f"   ✓ 检测到不完整的 <solution> 标签", file=sys.stderr)
                    self.final_content = body
                    # 处理 solution 前的文本为 reasoning
                    pre_text = output[:incomplete_solution.start()]
                    cleaned = self._clean_reasoning_segment(pre_text)
                    if cleaned and len(cleaned) > 2:
                        await self.on_reasoning(cleaned)
                    return
            
            # 全部作为 reasoning 处理
            cleaned = self._clean_reasoning_segment(output)
            if cleaned and len(cleaned) > 2:
                print(f"   ✓ 无标签，作为 reasoning 处理 (length: {len(cleaned)})", file=sys.stderr)
                await self.on_reasoning(cleaned)
            return

        cursor = 0
        for match in matches:
            # 处理标签前的文本片段
            if match.start() > cursor:
                text_segment = output[cursor:match.start()]
                cleaned = self._clean_reasoning_segment(text_segment)
                if cleaned and len(cleaned) > 2:
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
            if cleaned and len(cleaned) > 2:
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
        content = re.sub(r'</(?:execute|observation|observe|solution)>', '', content)
        content = content.strip()
        
        if not content or len(content) < 2:
            return
        
        # 过滤掉 A1 的自我纠正提示（这些是框架自动生成的，对用户没有价值）
        skip_patterns = [
            "Each response must include thinking process followed by either",
            "There are no tags in the current response",
            "Please follow the instruction, fix and regenerate",
            "Execution terminated due to repeated parsing errors",
        ]
        for pattern in skip_patterns:
            if pattern in content:
                print(f"   ⏭️ 跳过自我纠正消息: {content[:80]}...", file=sys.stderr)
                return
        
        # 简单策略：不拆分，保持完整
        # 只限制最大长度
        if len(content) > 8000:
            content = content[:8000] + "\n... (content truncated for display)"
        
        # 根据内容生成更有描述性的名称
        step_name = '🤔 Reasoning'
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('#'):
            # 如果内容以标题开头，用标题作为名称
            step_name = '🤔 ' + first_line.lstrip('#').strip()[:60]
        elif 'plan' in first_line.lower():
            step_name = '🤔 Planning'
        elif 'analy' in first_line.lower():
            step_name = '🤔 Analysis'
        
        self.step_order += 1
        
        step = ExecutionStep(
            conversation_id=self.conversation_id,
            message_id=self.current_message_id or 0,
            step_order=self.step_order,
            step_type='reasoning',
            step_name=step_name,
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
                'stepName': step_name,
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
        
        # 清理未完成的 tool_call 步骤（超时或出错导致 on_tool_result 未被调用）
        for pending_step in self.pending_tool_call_steps:
            pending_step.status = 'timeout'
            pending_step.completed_at = datetime.now()
            pending_step.duration_ms = int(
                (pending_step.completed_at - pending_step.started_at).total_seconds() * 1000
            )
            print(f"⚠️ 清理未完成的 tool_call step {pending_step.step_order} → timeout", file=sys.stderr)
        if self.pending_tool_call_steps:
            self.db.commit()
            self.pending_tool_call_steps.clear()
        
        # Fallback: 如果模型从未输出 <solution> 标签，从最后的步骤中提取内容
        if not self.final_content:
            print("⚠️ final_content 为空，尝试从执行步骤中提取 fallback 内容", file=sys.stderr)
            
            # 首先尝试从 result 类型步骤获取（最可靠）
            result_steps = self.db.query(ExecutionStep).filter(
                ExecutionStep.conversation_id == self.conversation_id,
                ExecutionStep.step_type == 'result',
                ExecutionStep.status == 'success'
            ).order_by(ExecutionStep.step_order.desc()).limit(3).all()
            
            for step in result_steps:
                if step.tool_output and len(step.tool_output) > 50:
                    self.final_content = step.tool_output
                    print(f"   ✓ 使用 result step {step.step_order} 作为 fallback", file=sys.stderr)
                    break
            
            # 如果没有 result，尝试 reasoning（但过滤掉模型纠错/元对话内容）
            if not self.final_content:
                _meta_patterns = [
                    "I need to provide my thinking",
                    "You're absolutely right",
                    "Let me fix this",
                    "I should follow the instruction",
                    "There are no tags",
                    "must include thinking process",
                ]
                last_steps = self.db.query(ExecutionStep).filter(
                    ExecutionStep.conversation_id == self.conversation_id,
                    ExecutionStep.step_type == 'reasoning',
                    ExecutionStep.status == 'success'
                ).order_by(ExecutionStep.step_order.desc()).limit(5).all()
                
                for step in last_steps:
                    if step.tool_output and len(step.tool_output) > 50:
                        # 跳过模型纠错/元对话内容
                        if any(pat.lower() in step.tool_output.lower() for pat in _meta_patterns):
                            print(f"   ⚠️ 跳过 meta-dialogue reasoning step {step.step_order}", file=sys.stderr)
                            continue
                        self.final_content = step.tool_output
                        print(f"   ✓ 使用 reasoning step {step.step_order} 作为 fallback", file=sys.stderr)
                        break
            
            if not self.final_content:
                self.final_content = "Analysis complete. Please review the execution steps above for detailed results."
        
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
        
        # 将所有执行步骤的 message_id 更新为 assistant message id
        updated_count = self.db.query(ExecutionStep).filter(
            ExecutionStep.conversation_id == self.conversation_id,
            ExecutionStep.message_id == (self.current_message_id or 0)
        ).update({ExecutionStep.message_id: assistant_message.id})
        self.db.commit()
        print(f"✓ 更新 {updated_count} 个执行步骤的 message_id → {assistant_message.id}", file=sys.stderr)
        
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
        
        # --- Scan for generated files ---
        generated_files_list = self._scan_and_register_files(assistant_message.id)
        
        result = {
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
        
        if generated_files_list:
            result['generatedFiles'] = generated_files_list
        
        return result

    def _scan_and_register_files(self, message_id: int) -> list:
        """Scan for new files created during execution, copy to output dir, register in DB."""
        import sys
        import os
        import shutil
        import mimetypes
        from core.config import settings
        from models.models import GeneratedFile

        data_path = os.path.abspath(settings.AGENT_DATA_PATH)
        
        # Directories to exclude from scanning
        EXCLUDE_DIRS = {
            'outputs', 'user_uploads', 'biomni_data', '__pycache__', '.git',
            'data_lake', '.ipynb_checkpoints', 'node_modules', '.cache',
            'upload', '.venv', 'env', 'venv',
        }

        start_ts = self.start_time.timestamp()
        found_files = []

        # 1. Scan data_path for NEW files (mtime > start_time)
        try:
            for root, dirs, files in os.walk(data_path):
                # Prune excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        st = os.stat(fpath)
                        if st.st_mtime > start_ts and st.st_size > 0:
                            found_files.append(fpath)
                    except OSError:
                        continue
        except Exception as e:
            print(f"⚠️ Error scanning data dir: {e}", file=sys.stderr)

        if not found_files and not self.output_dir:
            return []

        # 2. Ensure output dir exists, copy found files there
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            
            copied = []
            for fpath in found_files:
                # Don't copy if already inside output_dir
                if os.path.abspath(fpath).startswith(os.path.abspath(self.output_dir)):
                    continue
                dest = os.path.join(self.output_dir, os.path.basename(fpath))
                # Handle name collisions
                if os.path.exists(dest):
                    base, ext = os.path.splitext(os.path.basename(fpath))
                    dest = os.path.join(self.output_dir, f"{base}_{id(fpath) % 10000}{ext}")
                try:
                    shutil.copy2(fpath, dest)
                    copied.append(dest)
                except Exception as e:
                    print(f"⚠️ Failed to copy {fpath} → {dest}: {e}", file=sys.stderr)

            # 3. Now scan output_dir for all files (includes agent-written + copied)
            all_output_files = []
            if os.path.isdir(self.output_dir):
                for fname in os.listdir(self.output_dir):
                    fpath = os.path.join(self.output_dir, fname)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                        all_output_files.append(fpath)
        else:
            all_output_files = found_files

        if not all_output_files:
            return []

        # 4. Register in DB
        result = []
        for fpath in all_output_files:
            try:
                st = os.stat(fpath)
                mime, _ = mimetypes.guess_type(fpath)
                gf = GeneratedFile(
                    user_id=self.user_id,
                    conversation_id=self.conversation_id,
                    message_id=message_id,
                    filename=os.path.basename(fpath),
                    path=fpath,
                    size=st.st_size,
                    mime_type=mime,
                )
                self.db.add(gf)
                self.db.commit()
                self.db.refresh(gf)

                result.append({
                    'id': gf.id,
                    'filename': gf.filename,
                    'size': gf.size,
                    'mimeType': gf.mime_type,
                    'createdAt': gf.created_at.isoformat() if gf.created_at else None,
                })
                print(f"✓ Registered generated file: {gf.filename} ({gf.size} bytes)", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Failed to register file {fpath}: {e}", file=sys.stderr)

        print(f"📁 Total generated files: {len(result)}", file=sys.stderr)
        return result
