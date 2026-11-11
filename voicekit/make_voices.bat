@echo off
cd /d "%~dp0"
echo Making Urdu voices for Iqra - Let's Learn...
set PY=
py --version >nul 2>nul && set PY=py
if not defined PY python --version >nul 2>nul && set PY=python
if not defined PY goto nopy
%PY% -m pip install --quiet --upgrade edge-tts
%PY% make_voices.py
pause
exit /b
:nopy
echo.
echo Python is not installed. The download page will open now.
echo Install it (tick "Add python.exe to PATH"), then double-click make_voices.bat again.
start https://www.python.org/downloads/
pause
