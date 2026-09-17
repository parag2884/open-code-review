from __future__ import annotations

from pathlib import Path

from .config import get_settings
from .ocr import run_command


async def clone_repository(url: str, dest: Path, branch: str | None = None) -> None:
    settings = get_settings()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise RuntimeError(f"Clone destination already exists: {dest}")
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch, "--single-branch"])
    cmd.extend([url, str(dest)])
    lines: list[str] = []

    async def capture(line: str) -> None:
        lines.append(line)

    code = await run_command(cmd, cwd=None, env=None, on_progress=capture, timeout=settings.clone_timeout_sec)
    if code != 0:
        raise RuntimeError("\n".join(lines) or f"git clone exited {code}")


async def detect_default_branch(repo: Path) -> str | None:
    lines: list[str] = []

    async def capture(line: str) -> None:
        lines.append(line)

    code = await run_command(
        ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=None,
        env=None,
        on_progress=capture,
        timeout=30,
    )
    if code != 0 or not lines:
        return None
    return lines[0].strip() or None
