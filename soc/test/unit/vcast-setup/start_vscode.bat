@echo off

PUSHD %~dp0
CALL set_env.bat
SET "CODE_EXE=%APPDATA%\..\Local\Programs\Microsoft VS Code\Code.exe"
SET "TARGET_DIR=%~dp0..\project"

REM If launched from inside VS Code, force a fresh instance so this script's
REM environment variables are visible to extensions (license detection, etc.).
IF DEFINED VSCODE_PID (
    START "" "%CODE_EXE%" --new-window --user-data-dir "%TEMP%\vcast-vscode-profile" "%TARGET_DIR%"
) ELSE (
    START "" "%CODE_EXE%" "%TARGET_DIR%"
)
