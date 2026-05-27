@echo off

:: This is necessary to help VectorCAST debug the instrument code with winIDEA; appended to PATH temporarily by this script
set WINIDEA_EXE_DIR=C:\winIDEA
set VCAST_WINIDEA_PYTHON_DIR=C:\winIDEA\Python

:: May need this if GHS is installed in different location
::set PATH=C:\ghs\comp_202514;%PATH%

:: This script's directory; Note: Remove the trailing backslash to enhance readability
set THIS_SCRIPT_DIR=%~dp0
set THIS_SCRIPT_DIR=%THIS_SCRIPT_DIR:~0,-1%

:: Base directory of VectorCAST Project
set VCAST_PROJ_BASE=%THIS_SCRIPT_DIR%\..\project

:: Important files VectorCAST may need to use
set VCAST_SUPPORT_FILES=%THIS_SCRIPT_DIR%\support_files

:: Other locations not used in this script, but may need to be used in future...
set VCAST_REQ_REPO_DIR=%THIS_SCRIPT_DIR%\req-repo
set VCAST_CREDENTIALS_FILE=%THIS_SCRIPT_DIR%\credentials.json

:: The license server location for VectorCAST
set VECTOR_LICENSE_FILE=6009@lolicsrv01

::  Base directory of source code
set VCAST_SRC_BASE=%THIS_SCRIPT_DIR%\..\..\..\

:: This'll expand the relative path to absolute path
for /D %%F in ("%VCAST_SRC_BASE%") do set VCAST_SRC_BASE=%%~fF

:: Finally, append needed paths to the PATH temporarily
set PATH=%VCAST_WINIDEA_PYTHON_DIR%;%WINIDEA_EXE_DIR%;%PATH%

:: Name of the VectorCAST Project
for %%F in ("%VCAST_PROJ_BASE%"\*.vcm) do set VCAST_PROJ_NAME=%%~nF
