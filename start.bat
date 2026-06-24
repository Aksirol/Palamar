@echo off

if not exist .env (
    echo ERROR: .env file not found!
    echo Copy .env.example to .env and set SECRET_KEY.
    pause
    exit /b 1
)

echo Starting Docker...
docker compose up --build -d

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start Docker.
    echo Make sure Docker Desktop is installed and running.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   App is running at: http://localhost:8000
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
echo     Login:    see list below or use any student
echo     Password: student123
echo     (all students use password: student123)
echo.
echo   To seed the database with test data, run:
echo     seed.bat
echo.
echo ================================================
echo   To stop the app: run stop.bat
echo ================================================
echo.
start http://localhost:8000
pause
