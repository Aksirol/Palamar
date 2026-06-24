@echo off
title Seed Database (local)

if not exist .venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found.
    echo Run start_local.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Running seed (this will CLEAR all existing data)...
echo.
python manage.py seed_data --clear

echo.
pause
