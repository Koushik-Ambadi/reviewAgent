from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.graph_service import (
    GraphArtifactNotFoundError,
    get_graph_catalog,
    get_inter_module_graph,
    get_run_graph,
    get_run_graph_neighborhood,
    get_run_graph_nodes,
)
from orchestrator.run_store import RunNotFoundError, RunStoreError


router = APIRouter()


@router.get("/graphs/catalog")
async def read_graph_catalog():
    return get_graph_catalog()


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


@router.get("/runs/{run_id}/graphs/nodes")
async def read_run_graph_nodes(run_id: str):
    try:
        return get_run_graph_nodes(run_id)
    except (RunNotFoundError, GraphArtifactNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/runs/{run_id}/graphs/neighborhood")
async def read_run_graph_neighborhood(
    run_id: str,
    node_id: str,
    direction: str = "both",
    layers: list[str] | None = Query(default=None),
):
    try:
        return get_run_graph_neighborhood(
            run_id, node_id, direction=direction, layers=layers
        )
    except (RunNotFoundError, GraphArtifactNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RunStoreError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
