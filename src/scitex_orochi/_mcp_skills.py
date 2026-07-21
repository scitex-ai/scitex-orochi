"""MCP skills pair for scitex-orochi — ``skills_list`` / ``skills_get``.

The §5 skills tools every scitex MCP server exposes (Convention A bare
names) so agents can discover the package's bundled workflow guides
without shelling out to the CLI. Mirrors ``scitex-orochi skills list``
and ``scitex-orochi skills get <name>``; the markdown corpus lives in
``scitex_orochi/_skills/scitex-orochi/`` (single source of truth shared
with the CLI's ``skills`` group).
"""

from __future__ import annotations

import json

from scitex_orochi._cli.commands.skills_cmd import SKILLS_DIR


def _skill_description(text: str) -> str:
    """First meaningful line of a skill page: heading or opening prose."""
    in_frontmatter = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:80]
    return ""


def collect_skill_entries() -> list[dict[str, str]]:
    """One ``{name, description}`` entry per bundled top-level skill page."""
    if not SKILLS_DIR.exists():
        return []
    return [
        {
            "name": md.stem,
            "description": _skill_description(md.read_text(encoding="utf-8")),
        }
        for md in sorted(SKILLS_DIR.glob("*.md"))
    ]


def register_skills_tools(mcp) -> None:
    """Attach the ``skills_list`` / ``skills_get`` tool pair to ``mcp``."""

    @mcp.tool()
    async def skills_list() -> str:
        """List the bundled scitex-orochi skill pages (name + description)."""
        return json.dumps(collect_skill_entries())

    @mcp.tool()
    async def skills_get(name: str) -> str:
        """Return one bundled skill page by stem name (full markdown text).

        Unknown names return an error object listing the available names.
        """
        path = SKILLS_DIR / f"{name}.md"
        if not path.exists():
            available = sorted(p.stem for p in SKILLS_DIR.glob("*.md"))
            return json.dumps(
                {"name": name, "error": "not found", "available": available}
            )
        return json.dumps(
            {"name": name, "content": path.read_text(encoding="utf-8")}
        )
