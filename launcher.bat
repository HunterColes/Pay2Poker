@echo off
echo ========================================
echo  Poker Calculator - Distribution Kit
echo ========================================
echo.
echo Choose an option:
echo 1. Run calculator from source code
echo 2. Build standalone executable
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto run_source
if "%choice%"=="2" goto build_exe
if "%choice%"=="3" goto exit
echo Invalid choice. Please try again.
pause
goto start

:run_source
echo.
echo Running calculator from source...
python poker_payout_calculator.py
goto end

:build_exe
echo.
echo Building standalone executable...
call build_standalone.bat
goto end

:exit
echo Goodbye!
goto end

:end
pause
