from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from app.services.review_service import (
    review_uploaded_zip,
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