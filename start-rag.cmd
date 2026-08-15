@echo off
setlocal
cd /d "%~dp0"

echo ===========================================
echo   LocalLLM with Wikipedia
echo ===========================================

python webui.py --viewer jsonl --open-browser

if errorlevel 1 pause
endlocal