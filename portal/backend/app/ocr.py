from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path

from .config import Settings, get_settings

ProgressFn = Callable[[str], Awaitable[None]]


def write_isolated_ocr_config(home: Path, settings: Settings, effort: str) -> Path:
    config_dir = home / ".opencodereview"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    payload = {
        "provider": "azure_openai",
        "model": settings.azure_openai_deployment,
        "effort": effort,
        "custom_providers": {
            "azure_openai": {
                "url": settings.azure_chat_url,
                "protocol": "openai",
                "model": settings.azure_openai_deployment,
                "api_key": settings.azure_openai_api_key,
            }
        },
    }
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return config_path


def ocr_env(home: Path, settings: Settings) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["OCR_NO_UPDATE"] = "1"
    env["OCR_LLM_URL"] = settings.azure_chat_url
    env["OCR_LLM_TOKEN"] = settings.azure_openai_api_key
    env["OCR_LLM_MODEL"] = settings.azure_openai_deployment
    env["OCR_LLM_PROTOCOL"] = "openai"
    env["OCR_USE_ANTHROPIC"] = "false"
    return env


def resolve_ocr_binary() -> Path:
    settings = get_settings()
    binary = settings.ocr_binary
    if binary.name in {"ocr", "ocr.exe"} and not binary.is_absolute():
        found = shutil.which("ocr") or shutil.which("ocr.exe")
        if found:
            return Path(found)
    if not binary.exists():
        raise FileNotFoundError(f"ocr binary not found at {binary}")
    return binary


async def run_command(
    args: list[str],
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    on_progress: ProgressFn,
    timeout: int,
) -> int:
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    def worker() -> int:
        proc = subprocess.Popen(
            args,
            cwd=str(cwd) if cwd else None,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                text = line.rstrip()
                if text:
                    loop.call_soon_threadsafe(queue.put_nowait, text)
            return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise RuntimeError(f"command timed out: {' '.join(args[:3])}")
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    worker_task = asyncio.create_task(asyncio.to_thread(worker))
    while True:
        item = await queue.get()
        if item is None:
            break
        await on_progress(item)
    return await worker_task


async def run_ocr(
    args: list[str],
    *,
    home: Path,
    cwd: Path | None,
    on_progress: ProgressFn,
    timeout: int,
) -> int:
    settings = get_settings()
    binary = resolve_ocr_binary()
    return await run_command(
        [str(binary), *args],
        cwd=cwd,
        env=ocr_env(home, settings),
        on_progress=on_progress,
        timeout=timeout,
    )


async def llm_test(home: Path) -> tuple[int, str]:
    settings = get_settings()
    write_isolated_ocr_config(home, settings, "low")
    lines: list[str] = []

    async def capture(line: str) -> None:
        lines.append(line)

    code = await run_ocr(
        ["llm", "test"],
        home=home,
        cwd=home,
        on_progress=capture,
        timeout=60,
    )
    return code, "\n".join(lines)


async def ocr_version() -> str:
    try:
        binary = resolve_ocr_binary()
    except FileNotFoundError as exc:
        return str(exc)
    lines: list[str] = []

    async def capture(line: str) -> None:
        lines.append(line)

    try:
        await run_command([str(binary), "version"], cwd=None, env=None, on_progress=capture, timeout=30)
    except Exception as exc:
        return str(exc)
    return lines[0] if lines else "unknown"


def write_sarif(comments: list[dict], dest: Path, repo_name: str = "repository") -> None:
    results = []
    for comment in comments:
        severity = (comment.get("severity") or "").lower()
        level = {"critical": "error", "high": "error", "medium": "warning", "low": "note"}.get(severity, "warning")
        region = {}
        if comment.get("start_line"):
            region["startLine"] = comment["start_line"]
        if comment.get("end_line"):
            region["endLine"] = comment["end_line"]
        results.append(
            {
                "ruleId": comment.get("category") or "review",
                "level": level,
                "message": {"text": comment.get("content") or ""},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": comment.get("path") or ""},
                            "region": region,
                        }
                    }
                ],
            }
        )
    payload = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "OpenCodeReview",
                        "informationUri": "https://github.com/parag2884/open-code-review",
                    }
                },
                "originalUriBaseIds": {"REPO": {"uri": repo_name}},
                "results": results,
            }
        ],
    }
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
