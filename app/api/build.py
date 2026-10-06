# app/api/build.py
from fastapi import APIRouter, HTTPException

from orchestrator.build import (
    build_run,)
from orchestrator.build_jobs import get_build_status, start_build_job
from orchestrator.run_store import RunNotFoundError, RunStoreError

router = APIRouter()


@router.post(
    "/runs/{run_id}/build"
)
async def trigger_build(
    run_id: str,
    background: bool = False,
    run_format: bool = False,
):

    try:
        if background:
            return start_build_job(run_id, run_format=run_format)
        return build_run(run_id)
    except RunNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/runs/{run_id}/build/status")
async def read_build_status(run_id: str):
    try:
        return get_build_status(run_id)
    except RunNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RunStoreError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
