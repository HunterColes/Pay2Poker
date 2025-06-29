@echo off
echo ========================================
echo  Poker Payout Calculator Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
echo This may take a few minutes...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using spec file
pyinstaller PokerPayoutCalculator.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo  BUILD SUCCESSFUL!
echo ========================================
echo.
echo The executable has been created in the 'dist' folder:
echo   dist\PokerPayoutCalculator.exe
echo.
echo You can now distribute this single file to run the calculator
echo on any Windows computer without needing Python installed.
echo.
echo File size: 
for %%A in (dist\PokerPayoutCalculator.exe) do echo   %%~zA bytes
echo.
pause
