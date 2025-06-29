@echo off
echo Building Poker Payout Calculator executable...
echo.

REM Install required packages
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable with PyInstaller...
pyinstaller --onefile --windowed --name="PokerPayoutCalculator" --icon=poker.ico poker_payout_calculator.py

echo.
echo Build complete! 
echo The executable is located in the 'dist' folder.
echo You can distribute the 'PokerPayoutCalculator.exe' file.
echo.
pause
