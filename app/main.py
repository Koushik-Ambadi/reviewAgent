# review/app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.review import (
    router as review_router,
)
from app.api.build import (
    router as build_router,
)
from app.api.evidence import router as evidence_router
from app.api.remediation import (
    router as remediation_router,
)

from app.api.policy import (
    router as policy_router,
)

app = FastAPI(
    title="Review Agent"
)

app.include_router(
    review_router,
    prefix="/api",
)
app.include_router(
    build_router,
    prefix="/api",
)
app.include_router(evidence_router, prefix="/api")
app.include_router(
    remediation_router,
    prefix="/api",
)

app.include_router(
    policy_router,
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

