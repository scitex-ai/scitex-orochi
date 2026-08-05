"""CLI command: scitex-orochi skills -- browse package skills."""

from __future__ import annotations

import json
from pathlib import Path

import click

from scitex_orochi._cli._helpers import EXAMPLES_HEADER

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "_skills" / "scitex-orochi"


@click.group(
    "skills",
    epilog=EXAMPLES_HEADER
    + "  scitex-orochi skills list\n"
    + "  scitex-orochi skills get SKILL\n"
    + "  scitex-orochi skills export\n",
)
def skills() -> None:
    """View package skills (workflow-oriented guides)."""


@skills.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def skills_list(as_json: bool) -> None:
    """List available skill pages.

    Example:
      $ scitex-orochi skills list --json
    """
    import json

    if not SKILLS_DIR.exists():
        click.echo("No skills found.", err=True)
        return

    entries = []
    for md in sorted(SKILLS_DIR.glob("*.md")):
        name = md.stem
        # Read first non-empty, non-frontmatter line as description
        desc = ""
        in_frontmatter = False
        for line in md.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue
            if stripped and not stripped.startswith("#"):
                desc = stripped[:80]
                break
            if stripped.startswith("# "):
                desc = stripped[2:].strip()
                break
        entries.append({"name": name, "description": desc})

    if as_json:
        click.echo(json.dumps(entries, indent=2))
        return

    click.echo("Available skills for scitex-orochi:\n")
    for entry in entries:
        click.echo(f"  {entry['name']}")
        if entry["description"]:
            click.echo(f"    {entry['description']}")
    click.echo("\nUsage: scitex-orochi skills get <name>")


@skills.command("get")
@click.argument("name")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit the skill as JSON ({name, path, content}) instead of raw text.",
)
@click.pass_context
def skills_get(ctx: click.Context, name: str, as_json: bool) -> None:
    """Show a skill page.

    Example:
      $ scitex-orochi skills get autonomous --json
    """
    as_json = as_json or bool(ctx.obj and ctx.obj.get("json"))
    path = SKILLS_DIR / f"{name}.md"
    # Non-zero on a miss, and the hint to stderr — see docs_cmd.docs_get for
    # the reasoning: returning 0 here made `skills get typo && ...` continue
    # as though the skill had been found.
    if not path.exists():
        click.echo(f"Skill not found: {name}", err=True)
        click.echo("Run 'scitex-orochi skills list' to see available skills.", err=True)
        raise SystemExit(1)
    content = path.read_text(encoding="utf-8")
    if as_json:
        click.echo(json.dumps({"name": name, "path": str(path), "content": content}))
        return
    click.echo(content)


@skills.command("export")
@click.option(
    "--target",
    default=None,
    help="Target directory (default: ~/.claude/skills/scitex/).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be removed and copied, then exit without touching disk.",
)
@click.option(
    "--yes",
    "-y",
    "yes",
    is_flag=True,
    default=False,
    help="Skip the overwrite confirmation (required when running non-interactively).",
)
def skills_export(target: str | None, dry_run: bool, yes: bool) -> None:
    """Export skills to ~/.claude/skills/scitex/.

    Example:
      $ scitex-orochi skills export --target ~/.claude/skills/scitex --dry-run
    """
    import shutil
    import sys

    dest = Path(target) if target else Path.home() / ".claude" / "skills" / "scitex"
    orochi_dest = dest / "scitex-orochi"
    # This command DELETES a directory tree at a caller-supplied path
    # (`--target ~/` removes ~/scitex-orochi). Constitution: "dry-run every
    # bulk operation ... any change whose blast radius you cannot enumerate in
    # advance". Enumerate it before doing it, and never inside the same run
    # that performs it.
    will_remove = orochi_dest.exists()
    if dry_run:
        click.echo("dry-run: no changes made")
        click.echo(f"  would remove: {orochi_dest}" if will_remove else "  would remove: (nothing)")
        click.echo(f"  would copy:   {SKILLS_DIR} -> {orochi_dest}")
        return
    # Confirm ONLY when a destructive removal is actually pending AND someone
    # is there to answer. Prompting unconditionally would hang every scripted
    # caller; not prompting at all makes --yes decorative. isatty is what keeps
    # this additive rather than a breaking change.
    if will_remove and not yes and sys.stdin.isatty():
        click.confirm(f"Remove and replace {orochi_dest}?", abort=True)
    dest.mkdir(parents=True, exist_ok=True)
    if will_remove:
        shutil.rmtree(orochi_dest)
    shutil.copytree(SKILLS_DIR, orochi_dest)
    click.echo(f"Exported skills to {orochi_dest}")
