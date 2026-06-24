@echo off

echo Checking if container is running...
docker ps --filter "name=diary_django" --filter "status=running" -q > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Container is not running. Starting...
    docker compose up --build -d
    timeout /t 5 /nobreak > nul
)

echo.
echo Running seed (this will CLEAR all existing data)...
echo.
docker exec diary_django python manage.py seed_data --clear

echo.
pause
