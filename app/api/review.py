# review/app/api/review.py
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from app.services.review_service import (
    review_uploaded_zip,
    build_agent_review_summary,
    load_agent_review,
)

router = APIRouter()


@router.post("/review")
async def review_zip(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(
        ".zip"
    ):
        raise HTTPException(
            status_code=400,
            detail="ZIP file required",
        )

    report = review_uploaded_zip(
        file
    )

    return report




@router.post("/agent/review")
async def agent_review_zip(
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="ZIP file required",
        )

    review_result = review_uploaded_zip(file)

    review_report = review_result.get("report")

    if not isinstance(review_report, dict):
        raise HTTPException(
            status_code=500,
            detail="Review report was not generated correctly",
        )

    return build_agent_review_summary(
        review_report,
    )


@router.get("/agent/review/{run_id}")
async def get_agent_review(
    run_id: str,
):
    return load_agent_review(
        run_id,
    )