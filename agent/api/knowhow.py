"""Know-How 管理 REST API 路由。

提供 Know-How 文档的 CRUD 操作。
Know-How 是流程/方案文档，描述如何组合多个 Skill 解决具体问题。
文件系统（markdown 文件）为 source of truth。
"""

from __future__ import annotations

import os
import re
import glob
from typing import Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field

from core.security import verify_jwt_token

router = APIRouter()

# Know-How 文档目录
KNOW_HOW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "biomni", "know_how")
RESOURCE_DIR = os.path.join(KNOW_HOW_DIR, "resource")


def _reload_agent_knowhow():
    """通知所有缓存的 agent 实例重新加载 know-how 文档。"""
    try:
        from services.agent_service import agent_pool
        for user_id, (config_hash, agent) in list(agent_pool.items()):
            if hasattr(agent, 'know_how_loader'):
                agent.know_how_loader.reload()
                print(f"📚 Reloaded know-how for agent (user {user_id})")
    except Exception as e:
        print(f"⚠️ Failed to reload agent know-how: {e}")


# ---------------------------------------------------------------------------
# 鉴权
# ---------------------------------------------------------------------------

def _require_auth(authorization: str | None = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization header")
    token = authorization
    if token.lower().startswith("bearer "):
        token = token[7:]
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的 Token")
    return payload


def _ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "data": data, "message": message}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class KnowHowSummary(BaseModel):
    id: str
    name: str = ""
    description: str = ""
    authors: str = ""
    version: str = ""
    last_updated: str = ""
    license: str = ""
    commercial_use: str = ""
    status: str = ""


class KnowHowDetail(BaseModel):
    id: str
    name: str = ""
    description: str = ""
    content: str = ""
    authors: str = ""
    version: str = ""
    last_updated: str = ""
    license: str = ""
    commercial_use: str = ""
    status: str = ""
    resources: list[str] = Field(default_factory=list)


class CreateKnowHowRequest(BaseModel):
    id: str
    name: str
    description: str = ""
    content: str = ""
    authors: str = ""
    version: str = "1.0"
    license: str = "CC BY 4.0"
    commercial_use: str = "✅ Allowed"


class UpdateKnowHowRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    content: str | None = None
    authors: str | None = None
    version: str | None = None
    license: str | None = None
    commercial_use: str | None = None


# ---------------------------------------------------------------------------
# 内部函数
# ---------------------------------------------------------------------------

def _extract_metadata(content: str, filename: str) -> dict:
    """从 markdown 内容中提取 metadata。"""
    lines = content.split("\n")

    # Extract title
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if title is None:
        title = filename.replace("_", " ").replace(".md", "").title()

    # Extract metadata section
    metadata = {}
    in_metadata = False
    current_field = None

    for line in lines:
        if line.startswith("## Metadata"):
            in_metadata = True
            continue
        elif in_metadata:
            if line.startswith("##") and "Metadata" not in line:
                break
            elif line.startswith("**") and "**:" in line:
                field_match = line.split("**")[1]
                current_field = field_match.lower().replace(" ", "_")
                colon_idx = line.find("**:")
                if colon_idx != -1:
                    value_part = line[colon_idx + 3:].strip()
                    metadata[current_field] = value_part
            elif current_field and line.strip() and not line.startswith("---"):
                if current_field not in metadata:
                    metadata[current_field] = ""
                if line.startswith("- "):
                    if metadata[current_field]:
                        metadata[current_field] += ", " + line[2:].strip()
                    else:
                        metadata[current_field] = line[2:].strip()

    # Extract description from Overview section or first paragraph
    description = ""
    in_overview = False
    overview_lines = []
    for line in lines:
        if line.startswith("## Overview"):
            in_overview = True
            continue
        elif in_overview:
            if line.startswith("##"):
                break
            elif line.strip():
                overview_lines.append(line.strip())

    if overview_lines:
        description = " ".join(overview_lines)
    else:
        found_title = False
        for line in lines:
            if line.startswith("# "):
                found_title = True
                continue
            if found_title and line.strip() and not line.startswith("#") and not line.startswith("---"):
                if not line.startswith("**") and "Metadata" not in line:
                    description = line.strip()
                    break

    if len(description) > 300:
        description = description[:297] + "..."

    return {
        "name": title,
        "description": metadata.get("short_description", description),
        "authors": metadata.get("authors", ""),
        "version": metadata.get("version", ""),
        "last_updated": metadata.get("last_updated", ""),
        "license": metadata.get("license", ""),
        "commercial_use": metadata.get("commercial_use", ""),
        "status": metadata.get("status", ""),
    }


def _load_document(filepath: str) -> dict | None:
    """加载单个 know-how 文档。"""
    if not os.path.exists(filepath):
        return None

    filename = os.path.basename(filepath)
    doc_id = os.path.splitext(filename)[0]

    with open(filepath) as f:
        content = f.read()

    meta = _extract_metadata(content, filename)

    return {
        "id": doc_id,
        "content": content,
        "filepath": filepath,
        **meta,
    }


def _load_all_documents() -> list[dict]:
    """加载所有 know-how 文档。"""
    pattern = os.path.join(KNOW_HOW_DIR, "*.md")
    md_files = sorted(glob.glob(pattern))
    docs = []
    for filepath in md_files:
        filename = os.path.basename(filepath)
        name_no_ext = os.path.splitext(filename)[0]
        # Skip README etc.
        if filename.upper() in ["README.MD", "QUICK_START.MD"] or name_no_ext.isupper():
            continue
        doc = _load_document(filepath)
        if doc:
            docs.append(doc)
    return docs


def _get_resources() -> list[str]:
    """列出 resource 目录下的文件。"""
    if not os.path.exists(RESOURCE_DIR):
        return []
    return sorted(os.listdir(RESOURCE_DIR))


def _build_markdown(data: dict) -> str:
    """根据结构化数据生成 markdown 内容。"""
    name = data.get("name", "Untitled")
    description = data.get("description", "")
    authors = data.get("authors", "")
    version = data.get("version", "1.0")
    license_str = data.get("license", "CC BY 4.0")
    commercial_use = data.get("commercial_use", "✅ Allowed")
    content_body = data.get("content", "")

    # If content already has full markdown structure, return as-is
    if content_body.startswith("# ") and "## Metadata" in content_body:
        return content_body

    now = datetime.utcnow().strftime("%B %Y")

    md = f"""# {name}

---

## Metadata

**Short Description**: {description}

**Authors**: {authors or 'Unknown'}

**Version**: {version}

**Last Updated**: {now}

**License**: {license_str}

**Commercial Use**: {commercial_use}

---

## Overview

{description}

{content_body}
"""
    return md


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/knowhow")
async def list_knowhow(
    search: str | None = Query(None, description="关键词搜索"),
    authorization: str | None = Header(None),
):
    """获取所有 Know-How 文档列表。"""
    _require_auth(authorization)
    docs = _load_all_documents()

    if search:
        search_lower = search.lower()
        docs = [d for d in docs if search_lower in d["name"].lower()
                or search_lower in d["description"].lower()
                or search_lower in d.get("content", "").lower()]

    summaries = [
        KnowHowSummary(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            authors=d.get("authors", ""),
            version=d.get("version", ""),
            last_updated=d.get("last_updated", ""),
            license=d.get("license", ""),
            commercial_use=d.get("commercial_use", ""),
            status=d.get("status", ""),
        ).model_dump()
        for d in docs
    ]
    return _ok(summaries)


@router.get("/knowhow/{doc_id}")
async def get_knowhow(
    doc_id: str,
    authorization: str | None = Header(None),
):
    """获取单个 Know-How 文档详情。"""
    _require_auth(authorization)
    filepath = os.path.join(KNOW_HOW_DIR, f"{doc_id}.md")
    doc = _load_document(filepath)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Know-How '{doc_id}' 不存在")

    resources = _get_resources()

    detail = KnowHowDetail(
        id=doc["id"],
        name=doc["name"],
        description=doc["description"],
        content=doc["content"],
        authors=doc.get("authors", ""),
        version=doc.get("version", ""),
        last_updated=doc.get("last_updated", ""),
        license=doc.get("license", ""),
        commercial_use=doc.get("commercial_use", ""),
        status=doc.get("status", ""),
        resources=resources,
    ).model_dump()
    return _ok(detail)


@router.post("/knowhow", status_code=201)
async def create_knowhow(
    body: CreateKnowHowRequest,
    authorization: str | None = Header(None),
):
    """创建新的 Know-How 文档。"""
    _require_auth(authorization)

    # Validate ID (only allow alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', body.id):
        raise HTTPException(status_code=400, detail="ID 只能包含字母、数字、下划线和连字符")

    filepath = os.path.join(KNOW_HOW_DIR, f"{body.id}.md")
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail=f"Know-How '{body.id}' 已存在")

    # Build markdown content
    data = body.model_dump()
    md_content = _build_markdown(data)

    os.makedirs(KNOW_HOW_DIR, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(md_content)

    doc = _load_document(filepath)
    _reload_agent_knowhow()
    return _ok(KnowHowDetail(**{k: v for k, v in doc.items() if k != "filepath"}, resources=_get_resources()).model_dump())


@router.put("/knowhow/{doc_id}")
async def update_knowhow(
    doc_id: str,
    body: UpdateKnowHowRequest,
    authorization: str | None = Header(None),
):
    """更新 Know-How 文档。"""
    _require_auth(authorization)

    filepath = os.path.join(KNOW_HOW_DIR, f"{doc_id}.md")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Know-How '{doc_id}' 不存在")

    # If content is provided, write it directly (full markdown)
    if body.content is not None:
        with open(filepath, "w") as f:
            f.write(body.content)
    else:
        # Update metadata fields in existing content
        doc = _load_document(filepath)
        current_content = doc["content"]

        # For partial updates, rebuild the markdown
        update_data = body.model_dump(exclude_none=True)
        if update_data:
            merged = {
                "name": update_data.get("name", doc["name"]),
                "description": update_data.get("description", doc["description"]),
                "authors": update_data.get("authors", doc.get("authors", "")),
                "version": update_data.get("version", doc.get("version", "")),
                "license": update_data.get("license", doc.get("license", "")),
                "commercial_use": update_data.get("commercial_use", doc.get("commercial_use", "")),
                "content": current_content,
            }
            md_content = _build_markdown(merged)
            with open(filepath, "w") as f:
                f.write(md_content)

    doc = _load_document(filepath)
    _reload_agent_knowhow()
    return _ok(KnowHowDetail(**{k: v for k, v in doc.items() if k != "filepath"}, resources=_get_resources()).model_dump())


@router.delete("/knowhow/{doc_id}")
async def delete_knowhow(
    doc_id: str,
    authorization: str | None = Header(None),
):
    """删除 Know-How 文档（移动到 .deleted 后缀）。"""
    _require_auth(authorization)

    filepath = os.path.join(KNOW_HOW_DIR, f"{doc_id}.md")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Know-How '{doc_id}' 不存在")

    # Soft delete: rename to .deleted
    deleted_path = filepath + ".deleted"
    os.rename(filepath, deleted_path)
    _reload_agent_knowhow()
    return _ok({"id": doc_id}, f"Know-How '{doc_id}' 已删除")


@router.post("/knowhow/reload")
async def reload_knowhow(
    authorization: str | None = Header(None),
):
    """手动触发 agent 重新加载所有 know-how 文档。"""
    _require_auth(authorization)
    _reload_agent_knowhow()
    docs = _load_all_documents()
    return _ok({"count": len(docs)}, f"已重新加载 {len(docs)} 个 know-how 文档")
