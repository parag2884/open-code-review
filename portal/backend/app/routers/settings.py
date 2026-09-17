from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..auth import get_actor
from ..jobs import get_job, list_audit
from ..ocr import ocr_version
from ..schemas import Actor, AuthConfig, LlmTestResult, SettingsView
from ..config import get_settings
from pathlib import Path
import tempfile

from .. import ocr as ocr_runner

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/auth/config", response_model=AuthConfig)
def auth_config() -> AuthConfig:
    settings = get_settings()
    return AuthConfig(
        auth_mode=settings.auth_mode,
        azure_tenant_id=settings.azure_tenant_id if settings.auth_mode.lower() == "entra" else "",
        azure_client_id=settings.azure_client_id if settings.auth_mode.lower() == "entra" else "",
    )


@router.get("/auth/me")
def me(actor: Actor = Depends(get_actor)) -> Actor:
    return actor


@router.get("/settings", response_model=SettingsView)
async def settings_view(actor: Actor = Depends(get_actor)) -> SettingsView:
    settings = get_settings()
    binary = settings.ocr_binary
    found = binary.exists() or binary.name in {"ocr", "ocr.exe"}
    version = await ocr_version()
    return SettingsView(
        auth_mode=settings.auth_mode,
        provider=settings.llm_provider,
        azure_endpoint=settings.azure_chat_url,
        azure_deployment=settings.azure_openai_deployment,
        azure_api_version=settings.azure_openai_api_version,
        ocr_binary=str(binary),
        bind=f"{settings.bind_host}:{settings.bind_port}",
        git_hosts=sorted(settings.git_hosts),
        local_roots=[str(p) for p in settings.local_roots],
        llm_configured=bool(settings.azure_openai_api_key and settings.azure_chat_url and settings.azure_openai_deployment),
        ocr_found=found,
        ocr_version=version,
    )


@router.post("/settings/llm-test", response_model=LlmTestResult)
async def llm_test(actor: Actor = Depends(get_actor)) -> LlmTestResult:
    settings = get_settings()
    if not settings.azure_openai_api_key:
        raise HTTPException(status_code=400, detail="Azure OpenAI API key is not configured in .env")
    home = Path(tempfile.mkdtemp(prefix="ocr-llm-test-"))
    try:
        code, output = await ocr_runner.llm_test(home)
    finally:
        pass
    return LlmTestResult(ok=code == 0, output=output, exit_code=code)


@router.get("/audit")
def audit(actor: Actor = Depends(get_actor), limit: int = 100):
    return list_audit(limit=limit)


@router.get("/jobs/{job_id}/json")
def download_json(job_id: str, actor: Actor = Depends(get_actor)):
    job = get_job(job_id)
    if not job or not job.get("json_path"):
        raise HTTPException(status_code=404, detail="JSON result is not available")
    path = Path(job["json_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="JSON file is missing")
    return FileResponse(path, filename=f"{job_id}.json", media_type="application/json")


@router.get("/jobs/{job_id}/sarif")
def download_sarif(job_id: str, actor: Actor = Depends(get_actor)):
    job = get_job(job_id)
    if not job or not job.get("sarif_path"):
        raise HTTPException(status_code=404, detail="SARIF result is not available")
    path = Path(job["sarif_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="SARIF file is missing")
    return FileResponse(path, filename=f"{job_id}.sarif", media_type="application/sarif+json")
