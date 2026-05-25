@echo off
REM Replace "C:\Path\To\Directory" with the actual path you want to delete
SET TARGET_DIR="out"

IF EXIST %TARGET_DIR% (
    echo Deleting directory: %TARGET_DIR%
    rmdir /s /q %TARGET_DIR%
    echo Directory deleted.
) ELSE (
    echo Directory does not exist: %TARGET_DIR%
)
