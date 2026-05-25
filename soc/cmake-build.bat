@echo off

echo Current directory is: %CD%

::echo Changing current directory...
:: This is the physical path on my PC to the source file directory; necessary when this script is called from another script and working directory needs to change
::cd C:/git-sandbox/abs-core/src
::cd %CD%

::echo Current directory now is: %CD%
echo.

call clean-up.bat

set GHS_ROOT=C:/ghs/comp_202514
set GHS_COMPILER_DIR=%GHS_ROOT%/ccarm.exe
set GHS_GENERATOR="Green Hills MULTI"
set OUTPUT_DIR="out/build/ghs"
set BUILD_LOG_FILE=build.log

:: Generate build system
cmake -DCMAKE_C_COMPILER=%GHS_COMPILER_DIR% -S . -B %OUTPUT_DIR% -G %GHS_GENERATOR%

chcp

:: Build project with the system
cmake --build %OUTPUT_DIR% --parallel %NUMBER_OF_PROCESSSORS% --verbose -- > %BUILD_LOG_FILE% 2>&1
::cmake --build %OUTPUT_DIR% --parallel %NUMBER_OF_PROCESSSORS% --verbose --

:: Output the contents of the build.log to the screen
type %BUILD_LOG_FILE%
