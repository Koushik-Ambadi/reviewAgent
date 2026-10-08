from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.evidence_service import generate_evidence_pack
from orchestrator.run_store import RunNotFoundError, RunStoreError


router = APIRouter()


@router.get("/runs/{run_id}/evidence-pack")
async def download_evidence_pack(run_id: str):
    try:
        path = generate_evidence_pack(run_id)
    except RunNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RunStoreError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return FileResponse(
        path,
        media_type="text/html; charset=utf-8",
        filename=f"{run_id}-evidence-pack.html",
    )
