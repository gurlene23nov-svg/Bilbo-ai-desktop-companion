
@echo off
setlocal

set "PROJECT_DIR=%~dp0"

start "Bilbo Backend" /min /D "%PROJECT_DIR%" "%PROJECT_DIR%venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

start "" "%PROJECT_DIR%venv\Scripts\pythonw.exe" "%PROJECT_DIR%frontend\companion.py"

endlocal
exit