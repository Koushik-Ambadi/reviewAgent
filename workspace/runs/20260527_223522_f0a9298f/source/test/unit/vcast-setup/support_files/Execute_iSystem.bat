rem VectorCAST sets up these variables for it's own use of python. 
rem Because we are not using the VC python, we have to unset.
set PYTHONHOME=
set PYTHONPATH=
rem
rem In the .xjrf file, I set the download file to be vcast.elf, so we copy
rem the actual download file into that name to make the debugger happy!
copy %1 vcast.elf
%VCAST_WINIDEA_PYTHON_DIR%\python.exe %VCAST_SUPPORT_FILES%\vcast_isystems.py %cd%\vcast_ut.xjrf %1