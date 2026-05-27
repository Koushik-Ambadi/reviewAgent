@echo off
setlocal

:: %VECTORCAST_DIR% is set in Windows's Environment Variables.
:: %VCAST_PROJ_BASE% and %VCAST_PROJ_NAME% are set by set_env.bat.
call %~dp0set_env.bat

set "VCAST_PROJECT_DIR=%VCAST_PROJ_BASE%\%VCAST_PROJ_NAME%"

:: Default behavior is a safe clean of generated runtime data.
:: Pass --no-clean to skip cleanup.
:: Pass --full-clean to also clear project database/cache state.
if /I not "%~1"=="--no-clean" (
    if exist "%VCAST_PROJ_BASE%\CCAST_.CFG" del /Q "%VCAST_PROJ_BASE%\CCAST_.CFG"
    if exist "%VCAST_PROJECT_DIR%\build" rmdir /S /Q "%VCAST_PROJECT_DIR%\build"
    if exist "%VCAST_PROJECT_DIR%\logs" rmdir /S /Q "%VCAST_PROJECT_DIR%\logs"
    if exist "%VCAST_PROJECT_DIR%\lock" rmdir /S /Q "%VCAST_PROJECT_DIR%\lock"
)

if /I "%~1"=="--full-clean" (
    if exist "%VCAST_PROJECT_DIR%\project.db" del /Q "%VCAST_PROJECT_DIR%\project.db"
    if exist "%VCAST_PROJECT_DIR%\constants" rmdir /S /Q "%VCAST_PROJECT_DIR%\constants"
)

pushd "%VCAST_PROJ_BASE%"
start "" "%VECTORCAST_DIR%\vcastqt.exe" -e "%VCAST_PROJ_NAME%"
popd
endlocal
