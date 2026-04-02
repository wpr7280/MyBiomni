"""SkillLoader – parse skill directories into Skill objects.

Responsibilities:
* Scan a ``skills/`` root directory for sub-directories that contain ``skill.yaml``.
* Parse ``skill.yaml``, ``how_to.md``, and ``tools/*.yaml`` into Pydantic models.
* Support single-skill reload and hot-reload (mtime-based change detection).
"""

from __future__ import annotations

import glob
import os
import time
from pathlib import Path
from typing import Any

import yaml

from biomni.skill.models import Skill, SkillMetadata, ToolDefinition


class SkillLoader:
    """Load Skill definitions from the filesystem.

    Parameters
    ----------
    skills_dir : str | None
        Root directory containing skill sub-directories.  When *None* the
        loader defaults to ``<project_root>/skills/``.
    """

    def __init__(self, skills_dir: str | None = None):
        if skills_dir is None:
            # Default: <repo>/skills/ next to the agent package
            skills_dir = str(Path(__file__).resolve().parents[2] / "skills")
        self.skills_dir: str = skills_dir
        self._skills: dict[str, Skill] = {}  # skill_id → Skill

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> dict[str, Skill]:
        """(Re-)load every skill found under ``skills_dir``.

        Returns a dict mapping *skill_id* → :class:`Skill`.
        """
        self._skills.clear()

        if not os.path.isdir(self.skills_dir):
            print(f"[SkillLoader] skills directory not found: {self.skills_dir}")
            return self._skills

        for entry in sorted(os.listdir(self.skills_dir)):
            skill_path = os.path.join(self.skills_dir, entry)
            if not os.path.isdir(skill_path):
                continue
            yaml_path = os.path.join(skill_path, "skill.yaml")
            if not os.path.isfile(yaml_path):
                continue
            try:
                skill = self._load_skill_dir(skill_path)
                self._skills[skill.id] = skill
                print(f"[SkillLoader] loaded skill: {skill.id} "
                      f"({len(skill.tool_definitions)} tools)")
            except Exception as exc:
                print(f"[SkillLoader] ERROR loading {skill_path}: {exc}")

        print(f"[SkillLoader] total skills loaded: {len(self._skills)}")
        return self._skills

    def reload_skill(self, skill_id: str) -> Skill | None:
        """Reload a single skill from disk.

        Returns the reloaded :class:`Skill` or *None* if the directory is
        missing / invalid.
        """
        skill_path = os.path.join(self.skills_dir, skill_id)
        if not os.path.isdir(skill_path):
            print(f"[SkillLoader] skill directory not found: {skill_path}")
            return None
        try:
            skill = self._load_skill_dir(skill_path)
            self._skills[skill.id] = skill
            print(f"[SkillLoader] reloaded skill: {skill.id}")
            return skill
        except Exception as exc:
            print(f"[SkillLoader] ERROR reloading {skill_id}: {exc}")
            return None

    def get_skills(self) -> dict[str, Skill]:
        """Return the currently-loaded skill map (skill_id → Skill)."""
        return dict(self._skills)

    def check_for_updates(self) -> list[str]:
        """Return a list of skill IDs whose files have changed on disk.

        Compares the stored ``last_modified`` timestamp with the current
        max mtime of files in each skill directory.
        """
        updated: list[str] = []
        if not os.path.isdir(self.skills_dir):
            return updated

        for entry in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, entry)
            if not os.path.isdir(skill_path):
                continue
            yaml_path = os.path.join(skill_path, "skill.yaml")
            if not os.path.isfile(yaml_path):
                continue

            current_mtime = self._get_dir_mtime(skill_path)
            existing = self._skills.get(entry)
            if existing is None or current_mtime > existing.last_modified:
                updated.append(entry)

        return updated

    def hot_reload(self) -> list[str]:
        """Detect changed skills and reload them.  Returns reloaded IDs."""
        changed = self.check_for_updates()
        reloaded: list[str] = []
        for skill_id in changed:
            result = self.reload_skill(skill_id)
            if result is not None:
                reloaded.append(skill_id)
        if reloaded:
            print(f"[SkillLoader] hot-reloaded {len(reloaded)} skill(s): "
                  f"{', '.join(reloaded)}")
        return reloaded

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_skill_dir(self, skill_path: str) -> Skill:
        """Parse a single skill directory into a :class:`Skill`."""
        # 1. skill.yaml (required)
        yaml_path = os.path.join(skill_path, "skill.yaml")
        with open(yaml_path, "r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
        metadata = SkillMetadata(**raw)

        # 2. how_to.md (optional but expected)
        howto_path = os.path.join(skill_path, "how_to.md")
        howto = ""
        if os.path.isfile(howto_path):
            with open(howto_path, "r", encoding="utf-8") as fh:
                howto = fh.read()

        # 3. tools/*.yaml (optional)
        tool_defs: list[ToolDefinition] = []
        tools_dir = os.path.join(skill_path, "tools")
        if os.path.isdir(tools_dir):
            for tool_file in sorted(glob.glob(os.path.join(tools_dir, "*.yaml"))):
                try:
                    td = self._load_tool_yaml(tool_file, skill_id=metadata.name)
                    tool_defs.append(td)
                except Exception as exc:
                    print(f"[SkillLoader] ERROR loading tool "
                          f"{tool_file}: {exc}")

        # 4. Assemble Skill
        mtime = self._get_dir_mtime(skill_path)
        return Skill(
            metadata=metadata,
            howto=howto,
            tool_definitions=tool_defs,
            directory=skill_path,
            last_modified=mtime,
        )

    @staticmethod
    def _load_tool_yaml(tool_file: str, skill_id: str) -> ToolDefinition:
        """Parse a single ``tools/<name>.yaml`` file."""
        with open(tool_file, "r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
        raw["skill_id"] = skill_id
        return ToolDefinition(**raw)

    @staticmethod
    def _get_dir_mtime(dir_path: str) -> float:
        """Return the newest mtime among all files in *dir_path* (recursive)."""
        newest = 0.0
        for root, _dirs, files in os.walk(dir_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mt = os.path.getmtime(fpath)
                    if mt > newest:
                        newest = mt
                except OSError:
                    pass
        return newest
