@echo off
setlocal

echo Cleaning Python cache files in:
echo %~dp0
echo.

REM Remove all __pycache__ directories recursively
for /d /r "%~dp0" %%D in (__pycache__) do (
    if exist "%%D" (
        echo Removing %%D
        rd /s /q "%%D"
    )
)

REM Remove .pyc files
del /s /q "%~dp0*.pyc" >nul 2>&1

REM Remove .pyo files
del /s /q "%~dp0*.pyo" >nul 2>&1

echo.
echo Done.
pause