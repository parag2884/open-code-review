from __future__ import annotations

import ipaddress
from pathlib import Path
from urllib.parse import urlparse

BLOCKED_LOCAL_PREFIXES = (
    Path("C:/Windows"),
    Path("C:/Program Files"),
    Path("C:/Program Files (x86)"),
    Path("/etc"),
    Path("/usr"),
    Path("/bin"),
    Path("/sbin"),
    Path("/proc"),
    Path("/sys"),
)


def validate_git_url(raw: str, allowed_hosts: set[str]) -> str:
    value = (raw or "").strip()
    if not value:
        raise ValueError("Git URL is required")
    parsed = urlparse(value)
    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS Git URLs are allowed")
    if parsed.username or parsed.password:
        raise ValueError("Git URLs must not include credentials")
    if parsed.port not in (None, 443):
        raise ValueError("Git URLs must use port 443")
    host = (parsed.hostname or "").lower()
    if not host or host not in allowed_hosts:
        raise ValueError(f"Git host {host!r} is not on the allowlist")
    if _is_ip_address(host):
        raise ValueError("Git host must not be an IP address")
    path = parsed.path.strip("/")
    if not path or ".." in path.split("/"):
        raise ValueError("Git URL path is invalid")
    return f"https://{host}/{path}"


def validate_local_path(raw: str, allowed_roots: list[Path]) -> Path:
    value = (raw or "").strip().strip('"')
    if not value:
        raise ValueError("Local folder path is required")
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError("Local path must be an existing directory")
    if any(_is_relative_to(path, blocked) for blocked in BLOCKED_LOCAL_PREFIXES):
        raise ValueError("Local path is in a blocked system directory")
    if allowed_roots:
        if not any(_is_relative_to(path, root) for root in allowed_roots):
            raise ValueError("Local path is outside the configured allowlist")
    return path


def collect_python_files(root: Path, limit: int = 80) -> list[str]:
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
    files: list[str] = []
    for item in root.rglob("*.py"):
        if any(part in skip_dirs for part in item.parts):
            continue
        rel = item.relative_to(root).as_posix()
        files.append(rel)
        if len(files) >= limit:
            break
    return files


def _is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False
