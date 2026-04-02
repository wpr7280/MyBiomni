"""SkillRetriever – enhanced retrieval: match skills first, then load tools.

Provides two retrieval strategies:
1. **Keyword / trigger matching** – fast, no LLM call (via SkillManager).
2. **LLM-based retrieval** – fallback that sends skill summaries to an LLM
   and asks it to pick the most relevant ones.  Compatible with the existing
   ``ToolRetriever.prompt_based_retrieval()`` interface.
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool

from biomni.skill.manager import SkillManager
from biomni.skill.models import Skill


class SkillRetriever:
    """Retrieve relevant skills (and their tools) for a user query.

    Parameters
    ----------
    skill_manager : SkillManager
        The manager instance that owns the loaded skills.
    llm : Any | None
        Optional LLM instance used for the LLM-based fallback retrieval.
        If *None*, only keyword matching is available.
    """

    def __init__(
        self,
        skill_manager: SkillManager,
        llm: Any | None = None,
    ):
        self.manager = skill_manager
        self.llm = llm

    # ------------------------------------------------------------------
    # Primary retrieval entry-point
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_llm_fallback: bool = True,
    ) -> list[Skill]:
        """Retrieve the most relevant skills for *query*.

        1. Try keyword / trigger matching first.
        2. If fewer than *top_k* results and ``use_llm_fallback`` is enabled,
           use LLM-based retrieval to fill the gap.

        Returns an ordered list of :class:`Skill` objects (most relevant first).
        """
        # Step 1: keyword matching
        keyword_results = self.manager.retrieve_skills(query, top_k=top_k)

        if len(keyword_results) >= top_k or not use_llm_fallback or self.llm is None:
            return keyword_results

        # Step 2: LLM fallback
        already_ids = {s.id for s in keyword_results}
        remaining = top_k - len(keyword_results)
        llm_results = self._llm_retrieve(query, top_k=remaining, exclude_ids=already_ids)

        return keyword_results + llm_results

    # ------------------------------------------------------------------
    # Convenience: retrieve tools directly
    # ------------------------------------------------------------------

    def retrieve_tools(
        self,
        query: str,
        top_k_skills: int = 5,
        use_llm_fallback: bool = True,
    ) -> list[StructuredTool]:
        """Retrieve skills then flatten to their LangChain tool objects."""
        skills = self.retrieve(query, top_k=top_k_skills, use_llm_fallback=use_llm_fallback)
        tools: list[StructuredTool] = []
        for skill in skills:
            tools.extend(self.manager.get_skill_tools(skill.id))
        return tools

    def retrieve_howtos(
        self,
        query: str,
        top_k_skills: int = 3,
        use_llm_fallback: bool = True,
    ) -> str:
        """Retrieve skills and concatenate their how-to guides.

        Returns a single string suitable for injection into an agent system
        prompt.
        """
        skills = self.retrieve(query, top_k=top_k_skills, use_llm_fallback=use_llm_fallback)
        parts: list[str] = []
        for skill in skills:
            howto = self.manager.get_skill_howto(skill.id)
            if howto.strip():
                parts.append(f"## Skill: {skill.metadata.display_name or skill.id}\n\n{howto}")
        return "\n\n---\n\n".join(parts)

    # ------------------------------------------------------------------
    # Compatibility with existing ToolRetriever interface
    # ------------------------------------------------------------------

    def prompt_based_retrieval(
        self,
        query: str,
        resources: dict[str, list[Any]],
        llm: Any | None = None,
    ) -> dict[str, list[Any]]:
        """Drop-in compatible with ``ToolRetriever.prompt_based_retrieval()``.

        Accepts the same ``resources`` dict (keys: tools, data_lake,
        libraries, know_how) and returns a filtered copy.  Skill-based
        retrieval is used *in addition to* the tool-level filtering.

        Parameters
        ----------
        query : str
            User query.
        resources : dict
            Available resources keyed by category.
        llm : Any | None
            Optional LLM override.

        Returns
        -------
        dict
            Filtered resources.
        """
        # Retrieve relevant skills
        skills = self.retrieve(query, top_k=5, use_llm_fallback=llm is not None or self.llm is not None)

        # Collect tool names from matched skills
        skill_tool_names: set[str] = set()
        for skill in skills:
            skill_tool_names.update(skill.tool_names)

        # Collect how-to content from matched skills
        skill_howtos: list[dict[str, str]] = []
        for skill in skills:
            howto = self.manager.get_skill_howto(skill.id)
            if howto.strip():
                skill_howtos.append({
                    "id": skill.id,
                    "name": skill.metadata.display_name or skill.id,
                    "description": skill.metadata.description,
                    "content": howto,
                })

        # Filter resources – keep tools that match skill tool names + pass-through others
        filtered: dict[str, list[Any]] = {}
        if "tools" in resources:
            original_tools = resources["tools"]
            # Keep tools that belong to matched skills OR all if no skill match
            if skill_tool_names:
                matched = [t for t in original_tools
                           if isinstance(t, dict) and t.get("name") in skill_tool_names]
                # Also keep originals that didn't match (don't filter out)
                non_matched = [t for t in original_tools
                               if isinstance(t, dict) and t.get("name") not in skill_tool_names]
                # Matched tools come first (higher priority)
                filtered["tools"] = matched + non_matched
            else:
                filtered["tools"] = original_tools

        # Pass through other resource categories
        for key in ("data_lake", "libraries"):
            if key in resources:
                filtered[key] = resources[key]

        # Merge skill how-tos with existing know_how
        existing_knowhow = list(resources.get("know_how", []))
        filtered["know_how"] = skill_howtos + existing_knowhow

        return filtered

    # ------------------------------------------------------------------
    # LLM-based fallback
    # ------------------------------------------------------------------

    def _llm_retrieve(
        self,
        query: str,
        top_k: int = 3,
        exclude_ids: set[str] | None = None,
    ) -> list[Skill]:
        """Use an LLM to pick the most relevant skills from summaries."""
        if self.llm is None:
            return []

        exclude_ids = exclude_ids or set()
        candidates = [
            s for s in self.manager.get_enabled_skills()
            if s.id not in exclude_ids
        ]
        if not candidates:
            return []

        # Build the prompt
        skill_list = "\n".join(
            f"- [{s.id}] {s.metadata.display_name}: {s.metadata.description}"
            for s in candidates
        )
        prompt = (
            f"You are an expert biomedical research assistant. "
            f"Given the user query below, select the top {top_k} most relevant skills "
            f"from the list. Return ONLY the skill IDs (the text in square brackets), "
            f"one per line.\n\n"
            f"USER QUERY: {query}\n\n"
            f"AVAILABLE SKILLS:\n{skill_list}\n\n"
            f"SELECTED SKILL IDS (one per line):"
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            text = response.content if hasattr(response, "content") else str(response)
            selected_ids = self._parse_skill_ids(text, {s.id for s in candidates})
        except Exception as exc:
            print(f"[SkillRetriever] LLM retrieval failed: {exc}")
            return []

        # Map back to Skill objects, preserving order
        id_to_skill = {s.id: s for s in candidates}
        return [id_to_skill[sid] for sid in selected_ids[:top_k] if sid in id_to_skill]

    @staticmethod
    def _parse_skill_ids(text: str, valid_ids: set[str]) -> list[str]:
        """Extract skill IDs from LLM response text."""
        results: list[str] = []
        for line in text.strip().splitlines():
            line = line.strip().strip("-").strip()
            # Try bracket extraction first: [skill_id]
            match = re.search(r"\[([^\]]+)\]", line)
            if match:
                candidate = match.group(1).strip()
            else:
                candidate = line

            if candidate in valid_ids and candidate not in results:
                results.append(candidate)
        return results
