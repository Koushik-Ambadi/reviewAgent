# app/api/policy.py

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.services.policy_service import (
    load_policy_template,
)

router = APIRouter()


@router.get(
    "/policies/{policy_name}"
)
async def get_policy(
    policy_name: str,
):

    try:

        policy = load_policy_template(
            policy_name,
        )

        return {
            "policy_name": policy_name,
            "template": policy,
        }

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )