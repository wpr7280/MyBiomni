"""Skill 业务逻辑层 — 封装 SkillManager + 文件系统操作。

提供给 API 路由层调用的高级接口，负责：
- 列表/详情/过滤
- 创建 skill（生成目录结构 + 模板文件）
- 更新 skill.yaml / how_to.md / tools/*.yaml
- 启用/禁用
- 热加载
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import yaml

from biomni.skill.manager import SkillManager
from biomni.skill.models import Skill, SkillMetadata, ToolDefinition


# ---------------------------------------------------------------------------
# 默认 skills 目录（与 SkillLoader 保持一致）
# ---------------------------------------------------------------------------

def _default_skills_dir() -> str:
    """从环境变量或项目默认路径获取 skills 目录。"""
    env = os.environ.get("SKILLS_DIR")
    if env:
        return env
    # 与 SkillLoader 默认一致: <project_root>/skills/
    return str(Path(__file__).resolve().parents[1] / "skills")


# ---------------------------------------------------------------------------
# 全局单例
# ---------------------------------------------------------------------------

_manager: SkillManager | None = None


def get_skill_manager() -> SkillManager:
    """获取全局 SkillManager 单例，懒初始化。"""
    global _manager
    if _manager is None:
        skills_dir = _default_skills_dir()
        _manager = SkillManager(skills_dir=skills_dir, auto_load=True)
    return _manager


# ---------------------------------------------------------------------------
# 列表 / 详情 / 过滤
# ---------------------------------------------------------------------------

def list_skills(
    category: str | None = None,
    enabled: bool | None = None,
    search: str | None = None,
) -> list[Skill]:
    """列出 skill，支持按分类、启用状态、关键词过滤。"""
    mgr = get_skill_manager()
    skills = mgr.get_all_skills()

    if category is not None:
        skills = [s for s in skills if s.metadata.category == category]
    if enabled is not None:
        skills = [s for s in skills if s.metadata.enabled == enabled]
    if search:
        q = search.lower()
        skills = [
            s for s in skills
            if q in s.metadata.name.lower()
            or q in s.metadata.display_name.lower()
            or q in s.metadata.description.lower()
            or any(q in t.lower() for t in s.metadata.triggers)
        ]

    return skills


def get_skill(skill_id: str) -> Skill | None:
    """获取单个 skill 详情。"""
    return get_skill_manager().get_skill(skill_id)


def get_categories() -> list[str]:
    """获取所有已加载 skill 的分类列表（去重、排序）。"""
    mgr = get_skill_manager()
    cats = {s.metadata.category for s in mgr.get_all_skills() if s.metadata.category}
    return sorted(cats)


# ---------------------------------------------------------------------------
# 创建 Skill
# ---------------------------------------------------------------------------

_SKILL_YAML_TEMPLATE = """\
# 基础信息
name: {name}
display_name: "{display_name}"
version: "1.0.0"
category: {category}
description: >
  {description}

# 作者
authors: []

# 依赖
dependencies:
  python_packages: []
  data_lake: []

# 工具列表
tools: []

# 触发关键词
triggers: []

# 状态
enabled: true
"""

_HOWTO_TEMPLATE = """\
# {display_name}

## 前置条件

（请填写使用此 Skill 的前置条件）

## 推荐流程

### 步骤 1
（请填写步骤说明）

## 注意事项

（请填写注意事项）
"""


def create_skill(data: dict[str, Any]) -> Skill:
    """创建新 skill：生成目录结构 + 模板文件，然后加载。

    Parameters
    ----------
    data : dict
        至少包含 name；可选 display_name, category, description 等。

    Returns
    -------
    Skill
        新创建并加载的 Skill 对象。

    Raises
    ------
    ValueError
        如果 name 为空或同名 skill 已存在。
    """
    mgr = get_skill_manager()
    name = data.get("name", "").strip()
    if not name:
        raise ValueError("skill name 不能为空")

    # 检查重名
    if mgr.get_skill(name) is not None:
        raise ValueError(f"skill '{name}' 已存在")

    skills_dir = mgr.loader.skills_dir
    skill_path = os.path.join(skills_dir, name)

    # 创建目录结构
    os.makedirs(skill_path, exist_ok=True)
    os.makedirs(os.path.join(skill_path, "tools"), exist_ok=True)
    os.makedirs(os.path.join(skill_path, "templates"), exist_ok=True)
    os.makedirs(os.path.join(skill_path, "resources"), exist_ok=True)

    # 生成 skill.yaml
    display_name = data.get("display_name", name)
    category = data.get("category", "general")
    description = data.get("description", "新建 Skill，请补充描述。")

    # 如果提供了完整 metadata，直接序列化；否则用模板
    yaml_data: dict[str, Any] = {
        "name": name,
        "display_name": display_name,
        "version": data.get("version", "1.0.0"),
        "category": category,
        "description": description,
        "authors": data.get("authors", []),
        "license": data.get("license", ""),
        "commercial_use": data.get("commercial_use", True),
        "dependencies": data.get("dependencies", {"python_packages": [], "data_lake": []}),
        "tools": data.get("tools", []),
        "triggers": data.get("triggers", []),
        "enabled": data.get("enabled", True),
    }

    yaml_path = os.path.join(skill_path, "skill.yaml")
    with open(yaml_path, "w", encoding="utf-8") as fh:
        yaml.dump(yaml_data, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 生成 how_to.md
    howto_path = os.path.join(skill_path, "how_to.md")
    howto_content = data.get("howto", _HOWTO_TEMPLATE.format(display_name=display_name))
    with open(howto_path, "w", encoding="utf-8") as fh:
        fh.write(howto_content)

    # 加载新 skill
    skill = mgr.loader.reload_skill(name)
    if skill is None:
        raise RuntimeError(f"创建后加载 skill '{name}' 失败")

    # 清除 tool cache
    mgr._tool_cache.pop(name, None)
    return skill


# ---------------------------------------------------------------------------
# 更新 skill.yaml
# ---------------------------------------------------------------------------

def update_skill_metadata(skill_id: str, data: dict[str, Any]) -> Skill:
    """更新 skill.yaml 中的元数据字段。

    只更新 data 中提供的字段，其余保持不变。

    Raises
    ------
    FileNotFoundError
        如果 skill 不存在。
    """
    mgr = get_skill_manager()
    skill = mgr.get_skill(skill_id)
    if skill is None:
        raise FileNotFoundError(f"skill '{skill_id}' 不存在")

    yaml_path = os.path.join(skill.directory, "skill.yaml")

    # 读取现有 YAML
    with open(yaml_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    # 不允许修改 name（用作 ID）
    data.pop("name", None)

    # 合并更新
    raw.update(data)

    with open(yaml_path, "w", encoding="utf-8") as fh:
        yaml.dump(raw, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 重新加载
    reloaded = mgr.reload_skill(skill_id)
    if reloaded is None:
        raise RuntimeError(f"更新后加载 skill '{skill_id}' 失败")
    return reloaded


# ---------------------------------------------------------------------------
# 启用 / 禁用
# ---------------------------------------------------------------------------

def enable_skill(skill_id: str) -> Skill:
    """启用 skill（修改 skill.yaml 的 enabled 字段）。"""
    return update_skill_metadata(skill_id, {"enabled": True})


def disable_skill(skill_id: str) -> Skill:
    """禁用 skill（修改 skill.yaml 的 enabled 字段）。"""
    return update_skill_metadata(skill_id, {"enabled": False})


# ---------------------------------------------------------------------------
# 软删除
# ---------------------------------------------------------------------------

def delete_skill(skill_id: str) -> Skill:
    """软删除 skill：设 enabled: false + 添加 _deleted 标记。"""
    return update_skill_metadata(skill_id, {"enabled": False, "_deleted": True})


# ---------------------------------------------------------------------------
# How-To
# ---------------------------------------------------------------------------

def get_howto(skill_id: str) -> str:
    """获取 skill 的 how-to markdown 内容。"""
    mgr = get_skill_manager()
    skill = mgr.get_skill(skill_id)
    if skill is None:
        raise FileNotFoundError(f"skill '{skill_id}' 不存在")
    return skill.howto


def update_howto(skill_id: str, content: str) -> str:
    """更新 skill 的 how_to.md 文件内容。"""
    mgr = get_skill_manager()
    skill = mgr.get_skill(skill_id)
    if skill is None:
        raise FileNotFoundError(f"skill '{skill_id}' 不存在")

    howto_path = os.path.join(skill.directory, "how_to.md")
    with open(howto_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    # 重新加载使内存状态更新
    mgr.reload_skill(skill_id)
    return content


# ---------------------------------------------------------------------------
# Tool 操作
# ---------------------------------------------------------------------------

def get_tools(skill_id: str) -> list[ToolDefinition]:
    """获取 skill 内所有 tool 定义。"""
    mgr = get_skill_manager()
    skill = mgr.get_skill(skill_id)
    if skill is None:
        raise FileNotFoundError(f"skill '{skill_id}' 不存在")
    return skill.tool_definitions


def get_tool(skill_id: str, tool_name: str) -> ToolDefinition | None:
    """获取 skill 内单个 tool 定义。"""
    tools = get_tools(skill_id)
    for td in tools:
        if td.name == tool_name:
            return td
    return None


def update_tool(skill_id: str, tool_name: str, data: dict[str, Any]) -> ToolDefinition:
    """更新 skill 内某个 tool 的 YAML 文件。

    Raises
    ------
    FileNotFoundError
        如果 skill 或 tool 不存在。
    """
    mgr = get_skill_manager()
    skill = mgr.get_skill(skill_id)
    if skill is None:
        raise FileNotFoundError(f"skill '{skill_id}' 不存在")

    tool_path = os.path.join(skill.directory, "tools", f"{tool_name}.yaml")
    if not os.path.isfile(tool_path):
        raise FileNotFoundError(f"tool '{tool_name}' 在 skill '{skill_id}' 中不存在")

    # 读取现有 YAML
    with open(tool_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    # 不允许修改 name
    data.pop("name", None)

    # 合并更新
    raw.update(data)

    with open(tool_path, "w", encoding="utf-8") as fh:
        yaml.dump(raw, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 重新加载
    reloaded_skill = mgr.reload_skill(skill_id)
    if reloaded_skill is None:
        raise RuntimeError(f"更新 tool 后加载 skill '{skill_id}' 失败")

    # 返回更新后的 tool
    td = get_tool(skill_id, tool_name)
    if td is None:
        raise RuntimeError(f"更新后找不到 tool '{tool_name}'")
    return td


# ---------------------------------------------------------------------------
# 热加载
# ---------------------------------------------------------------------------

def reload_skill(skill_id: str) -> Skill | None:
    """热加载单个 skill。"""
    return get_skill_manager().reload_skill(skill_id)


def reload_all() -> list[str]:
    """热加载所有 skill，返回加载的 skill ID 列表。"""
    mgr = get_skill_manager()
    mgr.reload_all()
    return [s.id for s in mgr.get_all_skills()]
