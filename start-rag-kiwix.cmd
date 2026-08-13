@echo off
setlocal
cd /d "%~dp0"

echo ===========================================
echo   LocalLLM with Wikipedia (ruri-embed)
echo     -- with Kiwix Wikipedia viewer.
echo ===========================================

python webui.py --viewer kiwix

if errorlevel 1 pause
endlocal
