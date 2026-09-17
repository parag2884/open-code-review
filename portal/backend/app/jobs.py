from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from . import gitutil, ocr
from .config import get_settings
from .db import get_conn, row_to_dict, utcnow, workspace_for
from .schemas import Actor, ReviewRequest, job_from_row
from .security import collect_python_files, validate_git_url, validate_local_path


def create_job(req: ReviewRequest, actor: Actor) -> dict[str, Any]:
    settings = get_settings()
    if req.source_type == "git":
        source = validate_git_url(req.source, settings.git_hosts)
    else:
        source = str(validate_local_path(req.source, settings.local_roots))

    mode = "review" if (req.from_ref or "").strip() else "scan"
    job_id = str(uuid.uuid4())
    created = utcnow()
    workspace = workspace_for(job_id)
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, status, source_type, source, branch, mode, from_ref, to_ref,
                python_only, effort, actor, actor_oid, created_at, workspace_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                "queued",
                req.source_type,
                source,
                (req.branch or "").strip() or None,
                mode,
                (req.from_ref or "").strip() or None,
                (req.to_ref or "").strip() or None,
                1 if req.python_only else 0,
                req.effort,
                actor.name,
                actor.oid,
                created,
                str(workspace),
            ),
        )
        conn.execute(
            "INSERT INTO audit (created_at, actor, action, job_id, detail) VALUES (?, ?, ?, ?, ?)",
            (created, actor.name, "job.create", job_id, json.dumps({"source_type": req.source_type, "mode": mode})),
        )
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return row_to_dict(row) or {}


def list_jobs() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    return [row_to_dict(row) or {} for row in rows]


def get_job(job_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return row_to_dict(row)


def list_findings(job_id: str | None = None, severity: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM findings WHERE 1=1"
    params: list[Any] = []
    if job_id:
        sql += " AND job_id = ?"
        params.append(job_id)
    if severity:
        sql += " AND LOWER(COALESCE(severity, '')) = ?"
        params.append(severity.lower())
    if category:
        sql += " AND LOWER(COALESCE(category, '')) = ?"
        params.append(category.lower())
    sql += " ORDER BY id DESC"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) or {} for row in rows]


def list_logs(job_id: str, after_id: int = 0) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, created_at, line FROM job_logs WHERE job_id = ? AND id > ? ORDER BY id ASC",
            (job_id, after_id),
        ).fetchall()
    return [row_to_dict(row) or {} for row in rows]


def append_log(job_id: str, line: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO job_logs (job_id, created_at, line) VALUES (?, ?, ?)",
            (job_id, utcnow(), line),
        )


def list_audit(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [row_to_dict(row) or {} for row in rows]


async def run_job(job_id: str) -> None:
    job = get_job(job_id)
    if not job:
        return
    settings = get_settings()
    workspace = Path(job["workspace_path"])
    ocr_home = workspace / "ocr-home"
    ocr_home.mkdir(parents=True, exist_ok=True)
    json_path = workspace / "result.json"
    sarif_path = workspace / "result.sarif"
    clone_dir: Path | None = None
    repo_dir: Path | None = None

    async def progress(line: str) -> None:
        append_log(job_id, line)

    try:
        _update_job(job_id, status="running", started_at=utcnow())
        await progress("Preparing workspace")
        ocr.write_isolated_ocr_config(ocr_home, settings, job["effort"] or "medium")

        if job["source_type"] == "git":
            clone_dir = workspace / "clone"
            await progress(f"Cloning {job['source']}")
            await gitutil.clone_repository(job["source"], clone_dir, job.get("branch"))
            repo_dir = clone_dir
            branch = job.get("branch") or await gitutil.detect_default_branch(repo_dir)
            if branch:
                _update_job(job_id, branch=branch)
                await progress(f"Using branch {branch}")
        else:
            repo_dir = Path(job["source"])
            await progress(f"Using local folder {repo_dir}")

        if repo_dir is None or not repo_dir.exists():
            raise RuntimeError("Repository path is not available")

        mode = job["mode"]
        args = _build_ocr_args(job, repo_dir, json_path)
        await progress(f"Starting ocr {mode}")
        code = await ocr.run_ocr(
            args,
            home=ocr_home,
            cwd=repo_dir,
            on_progress=progress,
            timeout=settings.job_timeout_sec,
        )
        if code != 0 and not json_path.exists():
            raise RuntimeError(f"ocr exited with code {code}")

        if not json_path.exists():
            raise RuntimeError("ocr produced no JSON output")

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            payload = {"comments": payload, "summary": {"comments": len(payload)}}
        comments = payload.get("comments") or []
        ocr.write_sarif(comments, sarif_path, repo_dir.name)
        _store_results(job_id, payload, json_path, sarif_path)
        await progress(f"Stored {len(comments)} finding(s) and SARIF export")

        _update_job(job_id, status="succeeded", finished_at=utcnow())
        _audit(job.get("actor") or "system", "job.succeed", job_id, {"status": "succeeded"})
        await progress("Review complete")
        if clone_dir and clone_dir.exists():
            shutil.rmtree(clone_dir, ignore_errors=True)
    except Exception as exc:
        _update_job(job_id, status="failed", finished_at=utcnow(), error=str(exc))
        _audit(job.get("actor") or "system", "job.fail", job_id, {"error": str(exc)})
        append_log(job_id, f"ERROR: {exc}")


def _build_ocr_args(job: dict[str, Any], repo_dir: Path, output: Path, fmt: str = "json") -> list[str]:
    settings = get_settings()
    mode = job["mode"]
    args = [mode, "--repo", str(repo_dir), "--format", fmt, "--audience", "agent", "--output", str(output)]
    if mode == "review":
        from_ref = (job.get("from_ref") or "").strip()
        to_ref = (job.get("to_ref") or "HEAD").strip() or "HEAD"
        args.extend(["--from", from_ref, "--to", to_ref, "--effort", job.get("effort") or "medium"])
    else:
        args.extend(["--concurrency", str(settings.ocr_concurrency), "--timeout", str(settings.ocr_task_timeout_min)])
        if job.get("python_only"):
            py_files = collect_python_files(repo_dir)
            if not py_files:
                raise RuntimeError("Python-only is on, but no .py files were found")
            args.extend(["--path", ",".join(py_files)])
    return args


def _store_results(job_id: str, payload: dict[str, Any], json_path: Path, sarif_path: Path | None) -> None:
    summary = payload.get("summary") or {}
    comments = payload.get("comments") or []
    with get_conn() as conn:
        conn.execute("DELETE FROM findings WHERE job_id = ?", (job_id,))
        for comment in comments:
            conn.execute(
                """
                INSERT INTO findings (
                    job_id, path, content, suggestion_code, existing_code,
                    start_line, end_line, category, severity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    comment.get("path") or "",
                    comment.get("content") or "",
                    comment.get("suggestion_code"),
                    comment.get("existing_code"),
                    comment.get("start_line"),
                    comment.get("end_line"),
                    comment.get("category"),
                    comment.get("severity"),
                ),
            )
        conn.execute(
            """
            UPDATE jobs SET
                files_reviewed = ?, comments = ?, total_tokens = ?, input_tokens = ?,
                output_tokens = ?, elapsed = ?, json_path = ?, sarif_path = COALESCE(?, sarif_path)
            WHERE id = ?
            """,
            (
                summary.get("files_reviewed"),
                summary.get("comments", len(comments)),
                summary.get("total_tokens"),
                summary.get("input_tokens"),
                summary.get("output_tokens"),
                summary.get("elapsed"),
                str(json_path),
                str(sarif_path) if sarif_path else None,
                job_id,
            ),
        )


def _update_job(job_id: str, **fields: Any) -> None:
    if not fields:
        return
    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [job_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE jobs SET {assignments} WHERE id = ?", values)


def _audit(actor: str, action: str, job_id: str, detail: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit (created_at, actor, action, job_id, detail) VALUES (?, ?, ?, ?, ?)",
            (utcnow(), actor, action, job_id, json.dumps(detail)),
        )


def public_job(row: dict[str, Any] | None):
    if not row:
        return None
    return job_from_row(row)
