from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_repo_root() / ".env", Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repo_root: Path = Field(default_factory=_repo_root)
    bind_host: str = "127.0.0.1"
    bind_port: int = 8080

    auth_mode: str = "dev_bypass"
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    llm_provider: str = "azure_openai"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-08-01-preview"
    azure_openai_embedding_deployment: str = ""
    embedding_provider: str = ""
    vector_dim: int = 0

    portal_local_roots: str = ""
    git_host_allowlist: str = "github.com,www.github.com,gitlab.com,www.gitlab.com,dev.azure.com,bitbucket.org,www.bitbucket.org"
    job_timeout_sec: int = 2700
    clone_timeout_sec: int = 180
    ocr_task_timeout_min: int = 15
    ocr_concurrency: int = 4

    @property
    def data_dir(self) -> Path:
        path = self.repo_root / "portal" / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def workspaces_dir(self) -> Path:
        path = self.data_dir / "workspaces"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def ocr_binary(self) -> Path:
        windows = Path(self.repo_root / "dist" / "ocr.exe")
        unix = Path(self.repo_root / "dist" / "ocr")
        if windows.exists():
            return windows
        if unix.exists():
            return unix
        return Path("ocr")

    @property
    def azure_chat_url(self) -> str:
        endpoint = (self.azure_openai_endpoint or "").rstrip("/")
        if not endpoint:
            return ""
        if endpoint.endswith("/openai/v1"):
            return endpoint
        return f"{endpoint}/openai/v1"

    @property
    def local_roots(self) -> list[Path]:
        raw = self.portal_local_roots.strip()
        if not raw:
            return []
        return [Path(part).expanduser().resolve() for part in raw.split(",") if part.strip()]

    @property
    def git_hosts(self) -> set[str]:
        return {h.strip().lower() for h in self.git_host_allowlist.split(",") if h.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
