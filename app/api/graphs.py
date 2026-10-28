from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.graph_service import (
    GraphArtifactNotFoundError,
    get_inter_module_graph,
    get_run_graph,
)
from orchestrator.run_store import RunNotFoundError, RunStoreError


router = APIRouter()


@router.get("/runs/{run_id}/graphs")
async def read_run_graph(
    run_id: str,
    scope: str = "module",
    file: str | None = None,
    layers: list[str] | None = Query(default=None),
):
    try:
        return get_run_graph(
            run_id,
            scope=scope,
            selected_file=file,
            layers=layers,
        )
    except (RunNotFoundError, GraphArtifactNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/graphs/inter-module")
async def read_inter_module_graph(
    modules: list[str] | None = Query(default=None),
    layers: list[str] | None = Query(default=None),
):
    try:
        return get_inter_module_graph(module_names=modules, layers=layers)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
