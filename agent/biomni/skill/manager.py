"""SkillManager – lifecycle management for all loaded skills.

Provides the internal API surface consumed by the Agent layer:
* Enumerate enabled skills
* Retrieve skills by query (trigger keyword matching)
* Obtain LangChain Tool objects for a given skill
* Obtain how-to markdown for prompt injection
* Reload individual skills or the full set
"""

from __future__ import annotations

import importlib
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from biomni.skill.loader import SkillLoader
from biomni.skill.models import (
    ImplementationType,
    Skill,
    ToolDefinition,
)


# ---------------------------------------------------------------------------
# Helpers reused from biomni.utils (type mapping + dynamic schema creation)
# ---------------------------------------------------------------------------

_TYPE_MAP: dict[str, type] = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "bool": bool,
    "boolean": bool,
    "list": list,
    "dict": dict,
    "List[str]": list[str],
    "List[int]": list[int],
    "Dict": dict,
    "Any": Any,
}


def _resolve_type(type_str: str) -> type:
    """Map a string type name to a Python type object."""
    if type_str in _TYPE_MAP:
        return _TYPE_MAP[type_str]
    try:
        return eval(type_str)  # noqa: S307 – fallback for complex types
    except Exception:
        return Any  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# SkillManager
# ---------------------------------------------------------------------------

class SkillManager:
    """Central manager for all Skill lifecycle operations.

    Parameters
    ----------
    skills_dir : str | None
        Root directory containing skill sub-directories.  Forwarded to
        :class:`SkillLoader`.
    auto_load : bool
        If *True* (default), ``load_all()`` is called during ``__init__``.
    """

    def __init__(
        self,
        skills_dir: str | None = None,
        auto_load: bool = True,
    ):
        self.loader = SkillLoader(skills_dir=skills_dir)
        self._tool_cache: dict[str, list[StructuredTool]] = {}

        if auto_load:
            self.loader.load_all()

    # ------------------------------------------------------------------
    # Skill enumeration
    # ------------------------------------------------------------------

    def get_all_skills(self) -> list[Skill]:
        """Return every loaded skill regardless of enabled state."""
        return list(self.loader.get_skills().values())

    def get_enabled_skills(self) -> list[Skill]:
        """Return only skills whose ``enabled`` flag is *True*."""
        return [s for s in self.loader.get_skills().values() if s.enabled]

    def get_skill(self, skill_id: str) -> Skill | None:
        """Look up a single skill by its ID (``metadata.name``)."""
        return self.loader.get_skills().get(skill_id)

    # ------------------------------------------------------------------
    # Retrieval (keyword / trigger based)
    # ------------------------------------------------------------------

    def retrieve_skills(
        self,
        query: str,
        top_k: int = 5,
        enabled_only: bool = True,
    ) -> list[Skill]:
        """Retrieve the most relevant skills for a given query string.

        Matching logic (fast, no LLM call):
        1. Exact / substring match against ``triggers``.
        2. Substring match against ``description`` and ``display_name``.
        3. Rank by number of trigger hits (descending), return top-k.
        """
        query_lower = query.lower()
        candidates = self.get_enabled_skills() if enabled_only else self.get_all_skills()

        scored: list[tuple[float, Skill]] = []
        for skill in candidates:
            score = self._score_skill(skill, query_lower)
            if score > 0:
                scored.append((score, skill))

        # Sort descending by score
        scored.sort(key=lambda t: t[0], reverse=True)
        return [s for _, s in scored[:top_k]]

    @staticmethod
    def _score_skill(skill: Skill, query_lower: str) -> float:
        """Compute a relevance score for *skill* given a lowered query."""
        score = 0.0

        # Trigger matching (highest weight)
        for trigger in skill.metadata.triggers:
            trigger_lower = trigger.lower()
            if trigger_lower in query_lower or query_lower in trigger_lower:
                score += 10.0
            # Partial word overlap
            trigger_words = set(trigger_lower.split())
            query_words = set(query_lower.split())
            overlap = trigger_words & query_words
            if overlap:
                score += 2.0 * len(overlap)

        # Description / display name matching (lower weight)
        desc_lower = skill.metadata.description.lower()
        display_lower = skill.metadata.display_name.lower()
        for word in query_lower.split():
            if len(word) < 2:
                continue
            if word in desc_lower:
                score += 1.0
            if word in display_lower:
                score += 1.5

        # Category matching
        if skill.metadata.category and skill.metadata.category.lower() in query_lower:
            score += 3.0

        return score

    # ------------------------------------------------------------------
    # Tool objects
    # ------------------------------------------------------------------

    def get_skill_tools(self, skill_id: str) -> list[StructuredTool]:
        """Build and return LangChain ``StructuredTool`` objects for a skill.

        Results are cached per skill_id; the cache is invalidated on reload.
        """
        if skill_id in self._tool_cache:
            return self._tool_cache[skill_id]

        skill = self.get_skill(skill_id)
        if skill is None:
            print(f"[SkillManager] skill not found: {skill_id}")
            return []

        tools: list[StructuredTool] = []
        for td in skill.tool_definitions:
            try:
                tool = self._build_langchain_tool(td)
                if tool is not None:
                    tools.append(tool)
            except Exception as exc:
                print(f"[SkillManager] ERROR building tool "
                      f"{td.name}: {exc}")

        self._tool_cache[skill_id] = tools
        return tools

    def get_all_enabled_tools(self) -> list[StructuredTool]:
        """Return LangChain tools from *all* enabled skills."""
        tools: list[StructuredTool] = []
        for skill in self.get_enabled_skills():
            tools.extend(self.get_skill_tools(skill.id))
        return tools

    # ------------------------------------------------------------------
    # How-to
    # ------------------------------------------------------------------

    def get_skill_howto(self, skill_id: str) -> str:
        """Return the raw how-to markdown for a skill."""
        skill = self.get_skill(skill_id)
        return skill.howto if skill else ""

    # ------------------------------------------------------------------
    # Reload
    # ------------------------------------------------------------------

    def reload_skill(self, skill_id: str) -> Skill | None:
        """Reload a single skill from disk and invalidate its tool cache."""
        self._tool_cache.pop(skill_id, None)
        return self.loader.reload_skill(skill_id)

    def reload_all(self) -> None:
        """Reload every skill from disk."""
        self._tool_cache.clear()
        self.loader.load_all()

    def hot_reload(self) -> list[str]:
        """Detect file changes and reload affected skills."""
        reloaded = self.loader.hot_reload()
        for sid in reloaded:
            self._tool_cache.pop(sid, None)
        return reloaded

    # ------------------------------------------------------------------
    # Internal: Tool YAML → LangChain Tool
    # ------------------------------------------------------------------

    @staticmethod
    def _build_langchain_tool(td: ToolDefinition) -> StructuredTool | None:
        """Convert a :class:`ToolDefinition` into a LangChain ``StructuredTool``.

        For ``module_ref`` implementations the actual Python function is loaded
        via ``importlib`` from the existing ``biomni.tool.*`` modules.

        For ``guidance_only`` tools no callable is created (returns *None*).
        """
        impl = td.implementation

        if impl.type == ImplementationType.GUIDANCE_ONLY:
            # No executable tool – the skill provides guidance only
            return None

        if impl.type == ImplementationType.MODULE_REF:
            if not impl.module or not impl.function:
                print(f"[SkillManager] module_ref tool {td.name} "
                      f"missing module/function")
                return None
            try:
                mod = importlib.import_module(impl.module)
                func = getattr(mod, impl.function)
            except Exception as exc:
                print(f"[SkillManager] cannot import "
                      f"{impl.module}.{impl.function}: {exc}")
                return None
        elif impl.type == ImplementationType.TEMPLATE:
            # Template execution – placeholder; will be fully implemented
            # when sandbox support lands.
            def _template_placeholder(**kwargs: Any) -> str:
                return (
                    f"[template execution not yet supported] "
                    f"tool={td.name}, args={kwargs}"
                )
            func = _template_placeholder
        else:
            return None

        # Build Pydantic args schema dynamically (mirrors utils.py logic)
        annotations: dict[str, type] = {}
        fields: dict[str, Any] = {}
        for p in td.parameters.required:
            annotations[p.name] = _resolve_type(p.type)
            fields[p.name] = Field(description=p.description)

        # Create dynamic BaseModel for args
        ArgsModel = type(
            f"{td.name}_Input",
            (BaseModel,),
            {"__annotations__": annotations, **fields},
        )

        tool = StructuredTool.from_function(
            func=func,
            name=td.name,
            description=td.description,
            args_schema=ArgsModel,
            return_direct=True,
        )
        return tool
