"""CLI command: scitex-orochi docs -- browse documentation."""

from __future__ import annotations

import json
from pathlib import Path

import click

from scitex_orochi._cli._helpers import EXAMPLES_HEADER

_PKG_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


@click.group(
    "docs",
    epilog=EXAMPLES_HEADER
    + "  scitex-orochi docs list\n"
    + "  scitex-orochi docs get readme\n",
)
def docs() -> None:
    """Browse scitex-orochi documentation."""


_DOC_PAGES = {
    "readme": _PKG_ROOT / "README.md",
    "protocol": _PKG_ROOT / "README.md",
    "cloudflare": _PKG_ROOT / "docs" / "cloudflare-tunnel-config.md",
    "workspaces": _PKG_ROOT / "docs" / "workspace-integration-design.md",
}


@docs.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def docs_list(as_json: bool) -> None:
    """List available documentation pages."""
    import json

    entries = []
    for name, path in _DOC_PAGES.items():
        exists = path.exists()
        entries.append({"name": name, "path": str(path), "exists": exists})

    if as_json:
        click.echo(json.dumps(entries, indent=2))
        return

    click.echo("Available documentation:\n")
    for entry in entries:
        tag = "" if entry["exists"] else " (not found)"
        click.echo(f"  {entry['name']}{tag}")
    click.echo("\nUsage: scitex-orochi docs get <name>")


@docs.command("get")
@click.argument("name")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit the page as JSON ({name, path, content}) instead of raw text.",
)
@click.pass_context
def docs_get(ctx: click.Context, name: str, as_json: bool) -> None:
    """Show a documentation page.

    Example:
      $ scitex-orochi docs get quickstart --json
    """
    as_json = as_json or bool(ctx.obj and ctx.obj.get("json"))
    path = _DOC_PAGES.get(name)
    # Exit NON-ZERO on a miss. This previously printed to stderr and returned
    # 0, so `docs get typo && next-step` ran next-step against a page that was
    # never found — a silent failure of exactly the kind the constitution
    # forbids ("fail fast and fail loud, no silent fallbacks"). The hint goes
    # to stderr too, so it cannot contaminate piped stdout.
    if path is None:
        click.echo(f"Unknown doc page: {name}", err=True)
        click.echo("Run 'scitex-orochi docs list' to see available pages.", err=True)
        raise SystemExit(1)
    if not path.exists():
        click.echo(f"Doc file not found: {path}", err=True)
        raise SystemExit(1)
    content = path.read_text(encoding="utf-8")
    if as_json:
        click.echo(json.dumps({"name": name, "path": str(path), "content": content}))
        return
    click.echo(content)
