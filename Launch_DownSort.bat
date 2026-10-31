@echo off
title DownSort - Smart Local Downloads Organizer
cd /d "%~dp0"
echo ======================================================================
echo   Starting DownSort - Smart Local Downloads Organizer
echo ======================================================================
echo.
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while launching DownSort.
    pause
)
