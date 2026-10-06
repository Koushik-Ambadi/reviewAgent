# app/api/build.py
from fastapi import APIRouter, HTTPException

from orchestrator.build import (
    build_run,)
from orchestrator.run_store import RunNotFoundError, RunStoreError

router = APIRouter()


@router.post(
    "/runs/{run_id}/build"
)
async def trigger_build(
    run_id: str,
):

    try:
        return build_run(run_id)
    except RunNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
