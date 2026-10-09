from fastapi import APIRouter, HTTPException

from app.services.manager_service import (
    ManagerModuleNotFoundError,
    ManagerRunNotFoundError,
    compare_module_runs,
    get_module,
    get_portfolio,
)


router = APIRouter()


@router.get("/manager/portfolio")
async def read_manager_portfolio():
    return get_portfolio()


@router.get("/manager/modules/{module_name}")
async def read_manager_module(module_name: str):
    try:
        return get_module(module_name)
    except ManagerModuleNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/manager/modules/{module_name}/compare")
async def compare_manager_module_runs(
    module_name: str,
    base_run_id: str | None = None,
    target_run_id: str | None = None,
):
    try:
        return compare_module_runs(
            module_name,
            base_run_id=base_run_id,
            target_run_id=target_run_id,
        )
    except (ManagerModuleNotFoundError, ManagerRunNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
