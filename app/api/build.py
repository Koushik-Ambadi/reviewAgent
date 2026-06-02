# app/api/build.py
from fastapi import (
    APIRouter,
)

from orchestrator.build import (
    build_run,)

router = APIRouter()


@router.post(
    "/runs/{run_id}/build"
)
async def trigger_build(
    run_id: str,
):

    return build_run(
        run_id
    )