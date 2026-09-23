@echo off
rem Start the animation from the repository root and keep a log next to this file.
rem Extra arguments are passed through, e.g.  run_crenature.bat --duration 120
rem Set CRENATURE_PYTHON to a full python.exe path if "python" is not on PATH
rem for the account the scheduled task runs as.
setlocal
set PYTHONUNBUFFERED=1
if "%CRENATURE_PYTHON%"=="" set "CRENATURE_PYTHON=python"
cd /d "%~dp0.."
"%CRENATURE_PYTHON%" -u -m crenature %* > "%~dp0crenature.log" 2>&1
