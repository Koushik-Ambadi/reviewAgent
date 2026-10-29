from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.intelligence_service import Workspace

router = APIRouter(prefix="/intelligence")

class Rule(BaseModel):
    source: str = Field(alias="from", max_length=200)
    target: str = Field(alias="to", max_length=200)

class Query(BaseModel):
    modules: list[str] | None = Field(default=None, max_length=20)
    mode: str = "connections"
    selected: list[str] = Field(default_factory=list, max_length=20)
    depth: int = Field(default=3, ge=1, le=12)
    limit: int = Field(default=100, ge=1, le=300)
    rules: list[Rule] = Field(default_factory=list, max_length=50)

@router.get("/catalog")
def catalog():
    return Workspace().catalog()

@router.post("/query")
def query(request: Query):
    try:
        return Workspace(request.modules).query(mode=request.mode, selected=request.selected,
            depth=request.depth, limit=request.limit, rules=[r.model_dump(by_alias=True) for r in request.rules])
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

@router.get("/context")
def context(node_id: str):
    try: return Workspace().context(node_id)
    except ValueError as exc: raise HTTPException(400, str(exc)) from exc
