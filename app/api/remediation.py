from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.remediation_service import create_remediation
from orchestrator.run_store import RunNotFoundError, RunStoreError


router = APIRouter()


class RemediationRequest(BaseModel):
    scope: Literal["check", "case"]
    check_id: str
    case_id: str | None = None


@router.post("/runs/{run_id}/remediations")
async def request_remediation(
    run_id: str,
    request: RemediationRequest,
):
    try:
        return create_remediation(
            run_id=run_id,
            scope=request.scope,
            check_id=request.check_id,
            case_id=request.case_id,
        )
    except (RunNotFoundError, LookupError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
