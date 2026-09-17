from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    source_type: Literal["git", "local"]
    source: str
    branch: str | None = None
    from_ref: str | None = None
    to_ref: str | None = None
    python_only: bool = False
    effort: Literal["low", "medium", "high"] = "medium"


class Actor(BaseModel):
    name: str
    oid: str | None = None
    auth_mode: str


class JobSummary(BaseModel):
    id: str
    status: str
    source_type: str
    source: str
    branch: str | None = None
    mode: str
    from_ref: str | None = None
    to_ref: str | None = None
    python_only: bool = False
    effort: str = "medium"
    actor: str
    actor_oid: str | None = None
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None
    files_reviewed: int | None = None
    comments: int | None = None
    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    elapsed: str | None = None


class Finding(BaseModel):
    id: int | None = None
    job_id: str
    path: str
    content: str
    suggestion_code: str | None = None
    existing_code: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    category: str | None = None
    severity: str | None = None


class AuthConfig(BaseModel):
    auth_mode: str
    azure_tenant_id: str = ""
    azure_client_id: str = ""


class SettingsView(BaseModel):
    auth_mode: str
    provider: str
    azure_endpoint: str
    azure_deployment: str
    azure_api_version: str
    ocr_binary: str
    bind: str
    git_hosts: list[str] = Field(default_factory=list)
    local_roots: list[str] = Field(default_factory=list)
    llm_configured: bool
    ocr_found: bool
    ocr_version: str | None = None


class LlmTestResult(BaseModel):
    ok: bool
    output: str
    exit_code: int


def job_from_row(row: dict[str, Any]) -> JobSummary:
    return JobSummary(
        id=row["id"],
        status=row["status"],
        source_type=row["source_type"],
        source=row["source"],
        branch=row.get("branch"),
        mode=row["mode"],
        from_ref=row.get("from_ref"),
        to_ref=row.get("to_ref"),
        python_only=bool(row.get("python_only")),
        effort=row.get("effort") or "medium",
        actor=row["actor"],
        actor_oid=row.get("actor_oid"),
        created_at=row["created_at"],
        started_at=row.get("started_at"),
        finished_at=row.get("finished_at"),
        error=row.get("error"),
        files_reviewed=row.get("files_reviewed"),
        comments=row.get("comments"),
        total_tokens=row.get("total_tokens"),
        input_tokens=row.get("input_tokens"),
        output_tokens=row.get("output_tokens"),
        elapsed=row.get("elapsed"),
    )
