@echo off
title Shchodennyk - Local Start

echo ================================================
echo   Starting without Docker (local Python mode)
echo ================================================
echo.

:: --- Check Python ---
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Download Python 3.12 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo Python found: %PY_VER%

:: --- Create virtual environment if missing ---
if not exist .venv (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

:: --- Activate virtual environment ---
call .venv\Scripts\activate.bat

:: --- Install / update dependencies ---
echo.
echo Installing dependencies (may take a few minutes on first run)...
pip install -r requirements.txt -q --disable-pip-version-check
if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Some packages failed to install.
    echo The app will still start; PDF export may not work.
)
echo Dependencies ready.

:: --- Create .env if missing ---
if not exist .env (
    echo.
    echo Creating .env with auto-generated SECRET_KEY...
    python -c "import secrets; open('.env','w').write('SECRET_KEY=' + secrets.token_urlsafe(50) + '\nDEBUG=True\n')"
    echo .env created.
) else (
    echo .env found.
)

:: --- Apply migrations ---
echo.
echo Applying database migrations...
python manage.py migrate -v 0
if %ERRORLEVEL% neq 0 (
    echo ERROR: Migrations failed.
    pause
    exit /b 1
)

:: --- Print credentials and open browser ---
echo.
echo ================================================
echo   App is running at: http://127.0.0.1:8000
echo ================================================
echo.
echo   LOGIN CREDENTIALS:
echo   ------------------
echo   Role: Administrator
echo     Login:    admin
echo     Password: admin123
echo.
echo   Role: Teacher  (example)
echo     Login:    kovalchuk_v
echo     Password: teacher123
echo     (all teachers use password: teacher123)
echo.
echo   Role: Student  (example)
echo     Login:    (any student username)
echo     Password: student123
echo     (all students use password: student123)
echo.
echo   No test data? Run seed_local.bat to populate DB.
echo.
echo   NOTE: PDF export requires WeasyPrint + GTK3.
echo         All other features work without it.
echo.
echo ================================================
echo   Press Ctrl+C to stop the server
echo ================================================
echo.

start http://127.0.0.1:8000
python manage.py runserver 127.0.0.1:8000
