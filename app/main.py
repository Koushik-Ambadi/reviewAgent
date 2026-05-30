from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.review import (
    router as review_router,
)

app = FastAPI(
    title="Review Agent"
)

app.include_router(
    review_router,
    prefix="/api",
)

app.mount(
    "/",
    StaticFiles(
        directory="app/static",
        html=True,
    ),
    name="static",
)