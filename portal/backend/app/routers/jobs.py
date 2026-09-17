from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..auth import get_actor
from ..jobs import create_job, get_job, list_findings, list_jobs, list_logs, public_job, run_job
from ..schemas import Actor, ReviewRequest

router = APIRouter(prefix="/api", tags=["jobs"])


@router.post("/reviews")
async def start_review(req: ReviewRequest, actor: Actor = Depends(get_actor)):
    try:
        row = create_job(req, actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    asyncio.create_task(run_job(row["id"]))
    return public_job(row)


@router.get("/jobs")
def jobs(actor: Actor = Depends(get_actor)):
    return [public_job(row) for row in list_jobs()]


@router.get("/jobs/{job_id}")
def job_detail(job_id: str, actor: Actor = Depends(get_actor)):
    row = get_job(job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job": public_job(row),
        "findings": list_findings(job_id),
        "logs": list_logs(job_id),
    }


@router.get("/findings")
def findings(
    actor: Actor = Depends(get_actor),
    job_id: str | None = None,
    severity: str | None = None,
    category: str | None = None,
):
    return list_findings(job_id=job_id, severity=severity, category=category)


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str, request: Request, actor: Actor = Depends(get_actor)):
    if not get_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")

    async def stream():
        last_id = 0
        while True:
            if await request.is_disconnected():
                break
            logs = list_logs(job_id, after_id=last_id)
            for item in logs:
                last_id = item["id"]
                yield f"data: {json.dumps({'type': 'log', **item})}\n\n"
            job = get_job(job_id)
            if job and job["status"] in {"succeeded", "failed"}:
                yield f"data: {json.dumps({'type': 'complete', 'job': public_job(job).model_dump()})}\n\n"
                break
            await asyncio.sleep(0.6)

    return StreamingResponse(stream(), media_type="text/event-stream")
