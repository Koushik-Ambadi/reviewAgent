from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.remediation_service import create_remediation
from orchestrator.run_store import RunNotFoundError, RunStoreError
from repo_remediation import (
    RemediationProviderError,
    RemediationProviderUnavailableError,
)


router = APIRouter()


class RemediationRequest(BaseModel):
    scope: Literal["check", "case"]
    check_id: str
    case_id: str | None = None
    remediation_id: str | None = None
    context_answers: dict[str, str] = Field(default_factory=dict)
    developer_context: dict[str, str] = Field(default_factory=dict)


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
            remediation_id=request.remediation_id,
            context_answers=request.context_answers,
            developer_context=request.developer_context,
        )
    except (RunNotFoundError, LookupError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RemediationProviderUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RemediationProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
