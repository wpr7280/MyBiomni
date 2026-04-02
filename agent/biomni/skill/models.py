"""Pydantic data models for the Skill file-based system.

Defines the schema for skill.yaml, tools/*.yaml, and the composite Skill object.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ImplementationType(str, Enum):
    """Supported tool implementation strategies."""

    MODULE_REF = "module_ref"
    TEMPLATE = "template"
    GUIDANCE_ONLY = "guidance_only"


# ---------------------------------------------------------------------------
# Nested helpers
# ---------------------------------------------------------------------------

class AuthorInfo(BaseModel):
    """Author / maintainer of a skill."""

    name: str
    role: str = "contributor"


class PythonDependency(BaseModel):
    """Python package dependency with optional version constraint."""

    # Stored as raw strings like "scanpy>=1.9" for simplicity.
    pass


class DependenciesInfo(BaseModel):
    """Skill-level dependencies."""

    python_packages: list[str] = Field(default_factory=list)
    data_lake: list[str] = Field(default_factory=list)


class ToolParameter(BaseModel):
    """Single parameter definition for a tool."""

    name: str
    type: str = "str"
    description: str = ""
    default: Any = None


class ToolParameters(BaseModel):
    """Required + optional parameter lists for a tool."""

    required: list[ToolParameter] = Field(default_factory=list)
    optional: list[ToolParameter] = Field(default_factory=list)


class ToolReturns(BaseModel):
    """Return-value description for a tool."""

    type: str = "str"
    description: str = ""


class ToolImplementation(BaseModel):
    """How a tool is implemented – module reference, template, or guidance-only."""

    type: ImplementationType = ImplementationType.MODULE_REF
    module: str | None = None
    function: str | None = None
    file: str | None = None
    sandbox: bool = False


# ---------------------------------------------------------------------------
# Top-level models
# ---------------------------------------------------------------------------

class SkillMetadata(BaseModel):
    """Parsed representation of a ``skill.yaml`` file.

    Covers basic info, authorship, dependencies, tool list, trigger keywords,
    and enabled/disabled state.
    """

    # Basic info
    name: str
    display_name: str = ""
    version: str = "1.0.0"
    category: str = ""
    description: str = ""

    # Authorship
    authors: list[AuthorInfo] = Field(default_factory=list)
    license: str = ""
    commercial_use: bool = True

    # Dependencies
    dependencies: DependenciesInfo = Field(default_factory=DependenciesInfo)

    # Tools declared in this skill (names referencing tools/*.yaml)
    tools: list[str] = Field(default_factory=list)

    # Retrieval triggers – keywords / phrases for fast matching
    triggers: list[str] = Field(default_factory=list)

    # State
    enabled: bool = True


class ToolDefinition(BaseModel):
    """Parsed representation of a single ``tools/<tool_name>.yaml`` file.

    Designed so that it can be converted to a LangChain ``StructuredTool``
    that is compatible with the existing ``api_schema_to_langchain_tool()``
    output format.
    """

    name: str
    display_name: str = ""
    description: str = ""

    parameters: ToolParameters = Field(default_factory=ToolParameters)
    returns: ToolReturns = Field(default_factory=ToolReturns)

    implementation: ToolImplementation = Field(default_factory=ToolImplementation)

    # Back-reference to parent skill id (set at load time)
    skill_id: str = ""

    # -----------------------------------------------------------------
    # Conversion helpers
    # -----------------------------------------------------------------

    def to_api_schema(self) -> dict[str, Any]:
        """Convert to the dict format expected by ``api_schema_to_langchain_tool()``.

        The returned dict mirrors the structure produced by
        ``biomni/tool/tool_description/*.py`` – i.e. it has keys
        ``name``, ``description``, ``required_parameters``, and
        ``optional_parameters``.
        """
        required = [
            {
                "name": p.name,
                "type": p.type,
                "description": p.description,
                "default": p.default,
            }
            for p in self.parameters.required
        ]
        optional = [
            {
                "name": p.name,
                "type": p.type,
                "description": p.description,
                "default": p.default,
            }
            for p in self.parameters.optional
        ]
        return {
            "name": self.name,
            "description": self.description,
            "required_parameters": required,
            "optional_parameters": optional,
        }


class Skill(BaseModel):
    """Complete in-memory representation of a Skill directory.

    Combines metadata (``skill.yaml``), how-to guide (``how_to.md``),
    and tool definitions (``tools/*.yaml``) into a single object.
    """

    metadata: SkillMetadata
    howto: str = ""  # Raw markdown content of how_to.md
    tool_definitions: list[ToolDefinition] = Field(default_factory=list)

    # Filesystem bookkeeping
    directory: str = ""  # Absolute path to the skill directory
    last_modified: float = 0.0  # Max mtime across all files in the skill dir

    # Convenience properties ------------------------------------------------

    @property
    def id(self) -> str:
        """Skill identifier – same as ``metadata.name``."""
        return self.metadata.name

    @property
    def enabled(self) -> bool:
        return self.metadata.enabled

    @property
    def tool_names(self) -> list[str]:
        return [t.name for t in self.tool_definitions]
