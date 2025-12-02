@echo off
REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start Flask app in background
start "" python WebGUI.py

