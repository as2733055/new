@echo off
REM Quick Start Script for Mobile Chat System (Windows)

setlocal enabledelayedexpansion

cls
echo ========================================
echo   Mobile Chat System - Quick Start
echo ========================================

REM Check Python
echo.
echo Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    exit /b 1
)
echo [OK] Python found

REM Check Flutter
flutter --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Flutter not found. Please install Flutter
    exit /b 1
)
echo [OK] Flutter found

echo.
echo What would you like to do?
echo 1) Run Backend only
echo 2) Run Mobile App only
echo 3) Run Both (Backend + Mobile)
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting Backend...
    cd backend
    
    if not exist "venv" (
        echo Creating virtual environment...
        python -m venv venv
    )
    
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -q -r requirements.txt
    
    echo.
    echo [OK] Dependencies installed
    echo Starting FastAPI server...
    echo Access at: http://localhost:8000
    echo API Docs at: http://localhost:8000/docs
    echo.
    
    uvicorn app.main:app --reload
    
) else if "%choice%"=="2" (
    echo.
    echo Starting Mobile App...
    cd mobile
    
    echo Installing dependencies...
    flutter pub get
    
    echo.
    echo [OK] Dependencies installed
    echo Please ensure:
    echo 1) Backend is running on http://localhost:8000
    echo 2) Update API URL in lib/config.dart if needed
    echo 3) Android emulator is running (flutter devices)
    echo.
    
    flutter run
    
) else if "%choice%"=="3" (
    echo.
    echo Starting Backend and Mobile App...
    
    echo Starting Backend...
    cd backend
    
    if not exist "venv" (
        python -m venv venv
    )
    
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    
    start "Backend - Mobile Chat" uvicorn app.main:app --reload
    
    echo [OK] Backend started
    timeout /t 2 /nobreak
    
    echo Starting Mobile App...
    cd ..\mobile
    
    flutter pub get
    flutter run
    
) else (
    echo [ERROR] Invalid choice
    exit /b 1
)
