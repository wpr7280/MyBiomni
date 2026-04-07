"""Skill 管理 REST API 路由。

提供 Skill 的 CRUD、how-to 编辑、tool 管理、热加载等 endpoints。
所有修改直接操作文件系统，skill.yaml / how_to.md / tools/*.yaml 为 source of truth。
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field

from core.security import verify_jwt_token
from services import skill_service

router = APIRouter()


def _ok(data: Any = None, message: str = "success") -> dict:
    """包装为前端期望的 {code: 200, data: ...} 格式。"""
    return {"code": 200, "data": data, "message": message}


def _reload_agent_skills():
    """通知所有缓存的 agent 实例重新加载 skill。"""
    try:
        from services.agent_service import agent_pool
        for user_id, (config_hash, agent) in list(agent_pool.items()):
            if hasattr(agent, 'skill_manager') and agent.skill_manager:
                agent.skill_manager.reload_all()
                print(f"🎯 Reloaded skills for agent (user {user_id})")
    except Exception as e:
        print(f"⚠️ Failed to reload agent skills: {e}")


# ---------------------------------------------------------------------------
# 鉴权依赖
# ---------------------------------------------------------------------------

def _require_auth(authorization: str | None = Header(None)) -> dict:
    """从 Authorization header 解析并验证 JWT Token。

    支持 'Bearer <token>' 和直接传 token 两种格式。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization header")

    token = authorization
    if token.lower().startswith("bearer "):
        token = token[7:]

    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的 Token")
    return payload


# ---------------------------------------------------------------------------
# Response / Request Models
# ---------------------------------------------------------------------------

class SkillSummary(BaseModel):
    """Skill 列表中的摘要信息。"""
    id: str = ""
    name: str
    display_name: str = ""
    version: str = "1.0.0"
    category: str = ""
    description: str = ""
    enabled: bool = True
    tool_count: int = 0
    triggers: list[str] = Field(default_factory=list)


class AuthorOut(BaseModel):
    name: str
    role: str = "contributor"


class DependenciesOut(BaseModel):
    python_packages: list[str] = Field(default_factory=list)
    data_lake: list[str] = Field(default_factory=list)


class SkillDetail(BaseModel):
    """Skill 完整详情（含 skill.yaml 全部信息）。"""
    id: str = ""
    name: str
    display_name: str = ""
    version: str = "1.0.0"
    category: str = ""
    description: str = ""
    enabled: bool = True
    authors: list[AuthorOut] = Field(default_factory=list)
    license: str = ""
    commercial_use: bool = True
    dependencies: DependenciesOut = Field(default_factory=DependenciesOut)
    tools: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    howto: str = ""
    tool_count: int = 0
    directory: str = ""


class CreateSkillRequest(BaseModel):
    """创建 Skill 的请求体。"""
    name: str
    display_name: str = ""
    category: str = "general"
    description: str = ""
    version: str = "1.0.0"
    authors: list[dict[str, str]] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    enabled: bool = True
    howto: str | None = None


class UpdateSkillRequest(BaseModel):
    """更新 Skill 元数据的请求体。"""
    display_name: str | None = None
    category: str | None = None
    description: str | None = None
    version: str | None = None
    authors: list[dict[str, str]] | None = None
    triggers: list[str] | None = None
    license: str | None = None
    commercial_use: bool | None = None
    dependencies: dict[str, list[str]] | None = None


class HowToRequest(BaseModel):
    """更新 how-to 的请求体。"""
    content: str


class HowToResponse(BaseModel):
    """how-to 返回。"""
    skill_id: str
    content: str


class ToolSummary(BaseModel):
    """Tool 摘要。"""
    name: str
    display_name: str = ""
    description: str = ""
    skill_id: str = ""


class ToolParameterOut(BaseModel):
    name: str
    type: str = "str"
    description: str = ""
    default: Any = None


class ToolParametersOut(BaseModel):
    required: list[ToolParameterOut] = Field(default_factory=list)
    optional: list[ToolParameterOut] = Field(default_factory=list)


class ToolReturnsOut(BaseModel):
    type: str = "str"
    description: str = ""


class ToolImplementationOut(BaseModel):
    type: str = "module_ref"
    module: str | None = None
    function: str | None = None
    file: str | None = None
    sandbox: bool = False


class ToolDetail(BaseModel):
    """Tool 完整详情。"""
    name: str
    display_name: str = ""
    description: str = ""
    parameters: ToolParametersOut = Field(default_factory=ToolParametersOut)
    returns: ToolReturnsOut = Field(default_factory=ToolReturnsOut)
    implementation: ToolImplementationOut = Field(default_factory=ToolImplementationOut)
    skill_id: str = ""


class UpdateToolRequest(BaseModel):
    """更新 tool 定义的请求体。"""
    display_name: str | None = None
    description: str | None = None
    parameters: dict[str, Any] | None = None
    returns: dict[str, str] | None = None
    implementation: dict[str, Any] | None = None


class MessageResponse(BaseModel):
    """通用消息响应。"""
    message: str
    skill_id: str = ""


class ReloadAllResponse(BaseModel):
    """热加载所有 skill 的响应。"""
    message: str
    skills: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skill_to_summary(skill) -> SkillSummary:
    """将 Skill 对象转换为摘要。"""
    m = skill.metadata
    return SkillSummary(
        id=m.name,
        name=m.name,
        display_name=m.display_name,
        version=m.version,
        category=m.category,
        description=m.description,
        enabled=m.enabled,
        tool_count=len(skill.tool_definitions),
        triggers=m.triggers,
    )


def _skill_to_detail(skill) -> SkillDetail:
    """将 Skill 对象转换为完整详情。"""
    m = skill.metadata
    return SkillDetail(
        id=m.name,
        name=m.name,
        display_name=m.display_name,
        version=m.version,
        category=m.category,
        description=m.description,
        enabled=m.enabled,
        authors=[AuthorOut(name=a.name, role=a.role) for a in m.authors],
        license=m.license,
        commercial_use=m.commercial_use,
        dependencies=DependenciesOut(
            python_packages=m.dependencies.python_packages,
            data_lake=m.dependencies.data_lake,
        ),
        tools=m.tools,
        triggers=m.triggers,
        howto=skill.howto,
        tool_count=len(skill.tool_definitions),
        directory=skill.directory,
    )


def _tool_to_summary(td) -> ToolSummary:
    return ToolSummary(
        name=td.name,
        display_name=td.display_name,
        description=td.description,
        skill_id=td.skill_id,
    )


def _tool_to_detail(td) -> ToolDetail:
    return ToolDetail(
        name=td.name,
        display_name=td.display_name,
        description=td.description,
        parameters=ToolParametersOut(
            required=[
                ToolParameterOut(name=p.name, type=p.type, description=p.description, default=p.default)
                for p in td.parameters.required
            ],
            optional=[
                ToolParameterOut(name=p.name, type=p.type, description=p.description, default=p.default)
                for p in td.parameters.optional
            ],
        ),
        returns=ToolReturnsOut(type=td.returns.type, description=td.returns.description),
        implementation=ToolImplementationOut(
            type=td.implementation.type.value,
            module=td.implementation.module,
            function=td.implementation.function,
            file=td.implementation.file,
            sandbox=td.implementation.sandbox,
        ),
        skill_id=td.skill_id,
    )


# ---------------------------------------------------------------------------
# Endpoints — 注意：/categories 和 /reload-all 必须在 /{skill_id} 之前注册
# ---------------------------------------------------------------------------

@router.get("/skills/categories")
async def get_categories(
    authorization: str | None = Header(None),
):
    """获取所有分类列表。"""
    _require_auth(authorization)
    return _ok(skill_service.get_categories())


@router.post("/skills/reload-all")
async def reload_all_skills(
    authorization: str | None = Header(None),
):
    """热加载所有 skill。"""
    _require_auth(authorization)
    skill_ids = skill_service.reload_all()
    _reload_agent_skills()
    return _ok(skill_ids, f"成功加载 {len(skill_ids)} 个 skill")


@router.get("/skills")
async def list_skills(
    category: str | None = Query(None, description="按分类过滤"),
    enabled: bool | None = Query(None, description="按启用状态过滤"),
    search: str | None = Query(None, description="关键词搜索"),
    authorization: str | None = Header(None),
):
    """获取 Skill 列表，支持过滤和搜索。"""
    _require_auth(authorization)
    skills = skill_service.list_skills(category=category, enabled=enabled, search=search)
    return _ok([_skill_to_summary(s).model_dump() for s in skills])


@router.get("/skills/{skill_id}")
async def get_skill(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """获取 Skill 详情（含 skill.yaml 全部信息）。"""
    _require_auth(authorization)
    skill = skill_service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")
    return _ok(_skill_to_detail(skill).model_dump())


@router.post("/skills", status_code=201)
async def create_skill(
    body: CreateSkillRequest,
    authorization: str | None = Header(None),
):
    """创建新 Skill，自动生成目录结构和模板文件。"""
    _require_auth(authorization)
    try:
        data = body.model_dump(exclude_none=True)
        skill = skill_service.create_skill(data)
        _reload_agent_skills()
        return _ok(_skill_to_detail(skill).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/skills/{skill_id}")
async def update_skill(
    skill_id: str,
    body: UpdateSkillRequest,
    authorization: str | None = Header(None),
):
    """更新 Skill 元数据。"""
    _require_auth(authorization)
    try:
        data = body.model_dump(exclude_none=True)
        skill = skill_service.update_skill_metadata(skill_id, data)
        _reload_agent_skills()
        return _ok(_skill_to_detail(skill).model_dump())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


@router.patch("/skills/{skill_id}/enable")
async def enable_skill(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """启用 Skill。"""
    _require_auth(authorization)
    try:
        skill = skill_service.enable_skill(skill_id)
        _reload_agent_skills()
        return _ok(_skill_to_detail(skill).model_dump())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


@router.patch("/skills/{skill_id}/disable")
async def disable_skill(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """禁用 Skill。"""
    _require_auth(authorization)
    try:
        skill = skill_service.disable_skill(skill_id)
        _reload_agent_skills()
        return _ok(_skill_to_detail(skill).model_dump())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """软删除 Skill（设 enabled: false + 标记 _deleted）。"""
    _require_auth(authorization)
    try:
        skill_service.delete_skill(skill_id)
        _reload_agent_skills()
        return _ok({"skill_id": skill_id}, f"Skill '{skill_id}' 已标记删除")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


# ---------------------------------------------------------------------------
# How-To endpoints
# ---------------------------------------------------------------------------

@router.get("/skills/{skill_id}/how-to")
async def get_howto(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """获取 Skill 的 how-to markdown 内容。"""
    _require_auth(authorization)
    try:
        content = skill_service.get_howto(skill_id)
        return _ok({"skill_id": skill_id, "content": content})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


@router.put("/skills/{skill_id}/how-to")
async def update_howto(
    skill_id: str,
    body: HowToRequest,
    authorization: str | None = Header(None),
):
    """更新 Skill 的 how-to 内容。"""
    _require_auth(authorization)
    try:
        content = skill_service.update_howto(skill_id, body.content)
        return _ok({"skill_id": skill_id, "content": content})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


# ---------------------------------------------------------------------------
# Tool endpoints
# ---------------------------------------------------------------------------

@router.get("/skills/{skill_id}/tools")
async def get_skill_tools(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """获取 Skill 内所有 tool 列表。"""
    _require_auth(authorization)
    try:
        tools = skill_service.get_tools(skill_id)
        return _ok([_tool_to_detail(t).model_dump() for t in tools])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")


@router.get("/skills/{skill_id}/tools/{tool_name}")
async def get_skill_tool(
    skill_id: str,
    tool_name: str,
    authorization: str | None = Header(None),
):
    """获取 Skill 内单个 tool 详情。"""
    _require_auth(authorization)
    try:
        td = skill_service.get_tool(skill_id, tool_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在")

    if td is None:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' 在 Skill '{skill_id}' 中不存在")
    return _ok(_tool_to_detail(td).model_dump())


@router.put("/skills/{skill_id}/tools/{tool_name}")
async def update_skill_tool(
    skill_id: str,
    tool_name: str,
    body: UpdateToolRequest,
    authorization: str | None = Header(None),
):
    """更新 Skill 内某个 tool 的定义。"""
    _require_auth(authorization)
    try:
        data = body.model_dump(exclude_none=True)
        td = skill_service.update_tool(skill_id, tool_name, data)
        return _ok(_tool_to_detail(td).model_dump())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Reload endpoints
# ---------------------------------------------------------------------------

@router.post("/skills/{skill_id}/reload")
async def reload_skill(
    skill_id: str,
    authorization: str | None = Header(None),
):
    """热加载单个 Skill。"""
    _require_auth(authorization)
    skill = skill_service.reload_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' 不存在或加载失败")
    _reload_agent_skills()
    return _ok(_skill_to_detail(skill).model_dump())
